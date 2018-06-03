import os
import unicodedata
import re
from abc import ABC, abstractmethod
from pathlib import Path

class Document:
    def __init__(self, text, url):
        self.text = text # ex: text = "Héllo World!"
        self.url = url

class TokenizedDocument:
    def __init__(self, words, url):
        self.words = words # ex: words = [hello, world]
        self.url = url

class TextProcessor(ABC):
    @abstractmethod
    def process(self, word):
        pass

class Normalizer(TextProcessor):
    def process(self, word):
        # Normalizing accent and lowercasing
        word = ''.join(c for c in unicodedata.normalize('NFD', word) if unicodedata.category(c) != 'Mn')
        word = word.lower()

        return word

class Posting:
    def __init__(self, word, urls):
        self.word = word
        self.urls = urls

class Index:
    def __init__(self, urlToDid, wordToDids):
        self.urlToDid = urlToDid     # Map<String, int>
        self.wordToDids = wordToDids # Map<String, int[]>

# Return index if a word is in posting_list, -1 otherwise
def is_word_in_postingList(posting_list, word):
    i = -1
    for posting in posting_list:
        i += 1
        if posting.word == word:
            return i
        else:
            continue
    return -1

# Function that return a list of posting giving a list of tokenized documents
def index(documents):
    posting_list = []
    for document in documents:
        for word in document.words:
            i = is_word_in_postingList(posting_list, word)        
            # If the word exist on the posting list, adding the url to the list of url
            if i != -1:
                posting_list[i].urls.append(document.url)
            # If the word not exist on the posting list, creating a new posting
            else:
                posting = Posting(word, [document.url])
                posting_list.append(posting)
    return posting_list

# Function that return a list of document from a giving path
def fetch(path):
    document_list = []

    for p in Path(path).glob('./**/*'):
        if p.is_file():
            buf = "%s" % (p) 
            contents = ""
            try:
                with open(buf) as f:
                    for line in f.readlines():
                        contents += line

                doc = Document(contents, buf)
                document_list.insert(0, doc)
            except:
                pass

    return document_list

# Function that return a list of word from a giving text
def text_to_word(text):
    word_list = re.sub("[^\w]", " ",  text).split()
    return word_list

# Function that apply all the process to a document
def analyze(documents, processors):
    words = text_to_word(documents.text)
    for processor in processors:
        words = [processor.process(word) for word in words]

    tokenized_document = TokenizedDocument(words, documents.url)
    return tokenized_document

def main():
        
    print("Hello Moteur!")

    # Creating list of documents
    print("Creating list of documents")
    path = "./resources/20news-bydate-train/talk.politics.misc/"
    document_list = fetch(path)
    document_list = document_list[:100]

    # Creating list of processors objects
    print("Creating list of processors objects")
    processors_list = []
    processor_normalizer = Normalizer()
    processors_list.append(processor_normalizer)

    # Creating list of tokenized_document
    print("Creating list of tokenized_document")
    tokenized_document_list = []
    for document in document_list:
        tokenized_document = analyze(document, processors_list)
        tokenized_document_list.append(tokenized_document)

    # Creating posting list
    print("Creating posting list")
    posting_list = index(tokenized_document_list)
    print("The word {} is in urls {}".format(posting_list[100].word, posting_list[100].urls))


if __name__== "__main__":
  main()

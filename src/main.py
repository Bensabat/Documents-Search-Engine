import os
import unicodedata
import re
import json
from abc import ABC, abstractmethod
from pathlib import Path

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'

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

# Function that build and return an index object
def build(document_list, posting_list):
    urlToDid = {}
    Did = 1
    for document in document_list:
        urlToDid[document.url] = Did
        Did += 1

    wordToDids = {}
    for posting in posting_list:
        urls = []
        for url in posting.urls:
            urls.append(urlToDid[url])

        # Reduce urls
        urls = list(set(urls))
        wordToDids[posting.word] = urls

    index = Index(urlToDid, wordToDids)
    return index

# Function that save index on json file
def save(index, path):
    json_filename_urlToDid = path + "urlToDid.json"
    json_filename_wordToDids = path + "wordToDids.json"

    with open(json_filename_urlToDid, 'w') as f:
        json.dump(index.urlToDid, f)

    with open(json_filename_wordToDids, 'w') as f:
        json.dump(index.wordToDids, f)

# Function that create index from json file
def load(path):
    json_filename_urlToDid = path + "urlToDid.json"
    json_filename_wordToDids = path + "wordToDids.json"
    
    with open(json_filename_urlToDid, 'r') as f:
        datastore_urlToDid = json.load(f)

    with open(json_filename_wordToDids, 'r') as f:
        datastore_wordToDids = json.load(f)

    index = Index(datastore_urlToDid, datastore_wordToDids)
    return index

# Function that search urls associated to a word
def search(word, index_l):
    try:
        ids = index_l.wordToDids[word]
    except:
        print("This word doesn't exist on our word base, please try another.")
        return []

    urlToDid_dict = index_l.urlToDid
    urls = []
    for id in ids:
        url = list(urlToDid_dict.keys())[list(urlToDid_dict.values()).index(id)]
        urls.append(url)

    return urls

def main():
        
    print("\n--- Documents Search Engine ---\n")

    # Creating list of documents
    print(bcolors.OKGREEN + "Creating " + bcolors.ENDC + "list of documents")
    path = "./resources/20news-bydate-train/talk.politics.misc/"
    document_list = fetch(path)
    document_list = document_list[:200]

    # Creating list of processors objects
    print(bcolors.OKGREEN + "Creating " + bcolors.ENDC + "list of processors objects")
    processors_list = []
    processor_normalizer = Normalizer()
    processors_list.append(processor_normalizer)

    # Creating list of tokenized_document
    print(bcolors.OKGREEN + "Creating " + bcolors.ENDC + "list of tokenized_document")
    tokenized_document_list = []
    for document in document_list:
        tokenized_document = analyze(document, processors_list)
        tokenized_document_list.append(tokenized_document)

    # Creating posting list
    print(bcolors.OKGREEN + "Creating " + bcolors.ENDC + "posting list")
    posting_list = index(tokenized_document_list)
    #print("The word {} is in urls {}".format(posting_list[100].word, posting_list[100].urls))

    # Creating index
    print(bcolors.OKGREEN + "Creating " + bcolors.ENDC + "index")
    index_o = build(document_list, posting_list)

    # Saving index on disk
    print(bcolors.OKGREEN + "Saving " + bcolors.ENDC + "index on disk")
    path_index = "./resources/"
    save(index_o, path_index)

    # Loading index saved from disk
    print(bcolors.OKGREEN + "Loading " + bcolors.ENDC + "index saved from disk")
    index_l = load(path_index)

    # Searching user input words
    word = input("\nPlease enter a word (-quit to exit): ")
    while word not in ["-Quit", "-quit", "-exit", "-stop"]:
        print ("You entered the word " + bcolors.OKBLUE + str(word) + bcolors.ENDC + ".")

        for processor in processors_list:
            word = processor.process(word)

        urls = search(word, index_l)
        if urls:
            print("This word appears on these texts: ")            
            print(urls)

        word = input("\nPlease enter a word (-quit to exit): ")
    
    print("\nThanks for use!\n")


if __name__== "__main__":
  main()

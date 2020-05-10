'''
'''

#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import linecache
import json
import pickle
import math
import csv
import operator
import numpy as np
import random
from nltk import stem
from nltk.corpus import stopwords
from content_finder import ContentFinder
from urllib.request import urlopen
from bs4 import BeautifulSoup
from graph import Graph

#stemmer
stemmer = stem.PorterStemmer()
#set stop words to be ignored
stop_words = set(stopwords.words('english'))
#Dictionary for saving our tokens and the reference to their postings list.
#it has terms from title and content zones
dictionary = dict()


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

# Converts raw response data into readable information and checks for proper html formatting
def get_content(page_url):
    print("Retrieving " + page_url + " contents...")
    html_string = ''
    try:
        response = urlopen(page_url)
        if 'text/html' in response.getheader('Content-Type'):
            html_bytes = response.read()
            html_string = html_bytes.decode("utf-8")
        finder = ContentFinder(page_url)
        finder.feed(html_string)
    except Exception as e:
        print(str(e))
        return set()
    return finder.page_content()

# Converts raw response data into readable information and checks for proper html formatting
def get_content_soup(page_url):
    content_dict = {'title': '', 'content': ''}
    print("Retrieving " + page_url + " contents...")
    html_string = ''
    try:
        response = urlopen(page_url)
        if 'text/html' in response.getheader('Content-Type'):
            html_bytes = response.read()
            html_string = html_bytes.decode("utf-8")
        soup = BeautifulSoup(html_string, 'html.parser')
        for tag in soup.findAll('p'):
             content_dict['content'] = content_dict['content'] + tag.getText()
        for tag in soup.findAll('title'):
             content_dict['title'] = content_dict['title'] + tag.getText()  
             content_dict['title'] = content_dict['title'].replace('- Wikipedia','')
    except Exception as e:
        print(str(e))
        return set()
    return content_dict

#Updates the dictionary with doc ids term counts
def update_terms_zones_dictionary(doc_id, text, zone):
    # Tokenizes the docs text that could be in the title zone or the content zone
    # Also sums up term frequencies
    # Updates the global variable: dictionary (key = doc_id, postings list)

    #tokenize
    words = nltk.word_tokenize(text)
    
    for word in words:
        #to lower
        word = word.lower()
        #skip stop words
        if word in stop_words:
            continue
        
        #stemming
        word = stemmer.stem(word)
        #adding the word's zone
        word = word + zone

        #For each word check if its already registered in the dictionary
        #If its not, a new postings list is created for that word
        #If its already registered, its postings list is retrieved
        postings_list = dictionary.get(word, list())
        
        #This is to check if the word is not registered and a postings list 
        #was just created for it
        if(len(postings_list) == 0):
            #Create the tuple of (docId, termF)
            docID_termF = (doc_id, 1)
            #Then add the file name (id) in which the word appears
            postings_list.append(docID_termF)
            #Save the postings list in the dictionary
            dictionary[word] = postings_list

        #If the word was already in the dictionary, we check that the last entry
        #in its posting list is not the same as the filename (id) we are currently checking
        #as we don't want duplicate doc ids in the postings list
        else:
            #We check the last appearance of the word, to see if it was in the current doc
            last_appearance = postings_list[len(postings_list) - 1]
            #Check if this last appearance was in the current doc
            if(last_appearance[0] == doc_id):
                #If it was in the current doc, we add to the term frequency
                postings_list[len(postings_list) - 1] = (last_appearance[0], last_appearance[1] + 1)
            else:
                #If it was not, we append a new tuple to the list and start with term frequency = 1
                docID_termF = (doc_id, 1)
                postings_list.append(docID_termF)
                dictionary[word] = postings_list

#Obtains the graph generated in the crawling process
def retrieve_graph(file_name):
    try:
        saved_graph = Graph()
        with open(file_name,"rb") as f:
            print("Retrieving graph...")
            saved_graph.vertices = pickle.load(f)
            print("Loaded vertices")
            saved_graph.edges = pickle.load(f)
            print("Loaded edges")
            saved_graph.edge_indices = pickle.load(f)
        print("Success in retrieving graph")
        return saved_graph
    except:
        print("!!!Failed to retrieve saved graph")

#Page rank using a precomputed adjacency matrix of the crawled pages
#10% probability of transporting to a random node
#90% probabiliy of following a link in the node
#random_probability = probability for teleportation
#returns the rank vector "a"
def page_rank(graph_file, random_probability):
    print("Computing page rank...")
    ranks_vector = []
    if random_probability < 0 or random_probability > 1:
        return ranks_vector
    complementary_probability = 1 - random_probability
    #graph with instance variables:
    #vertices dictionary with key = url, edges = adjacency matrix
    graph = retrieve_graph(graph_file)
    #numpy matrix for faster calculations
    adjacency_matrix = graph.edges
    #1. Get total nodes in graph
    N = len(graph.vertices)
    #2. This is the value of the edge when it has no outlinks (teleportation)
    teleport = 1/N * random_probability
    #3. This is the A matrix to be multiplied by the vector of probabilities
    A = [] 
    #4. x = the vector to be multiplied by the A matrix, equal probability to be in a page
    x = [1] * N
    #5. The rank vector to be returned
    a = []
    #6. For each row in adj matrix (each vertex)
    for vertex in adjacency_matrix:
        print("Computing vertex weights...")
        # The list of weights for the current vertex of the adj matrix
        vertex_weights = []
        # outedges will be needed to know the edge value in A when it has outlinks
        outedges = np.count_nonzero(vertex)
        # value of edge in A when it has outlinks (no teleportation)
        no_teleport = 0
        if(outedges != 0):
            no_teleport = 1/outedges * complementary_probability
        for edge in vertex:
            weight = 0
            if edge == 1:
                # No teleportation
                weight = no_teleport + teleport
            else:
                # Teleportation needed
                weight = teleport
            vertex_weights.append(weight)
        A.append(vertex_weights)

    Anp = np.array(A)
    xnp = np.array(x)
    #7. Obtain the rank vector
    stable = False
    #repeat until stable or max_iterations met
    max_iterations = 100
    it = 0
    while(not stable and it < max_iterations):
        print("Stabilizing rank vector...")
        a = Anp.dot(xnp)
        comparison = a == xnp
        stable = comparison.all()
        xnp = a
        it += 1
    return a

#Function to map each doc or page to its rank by a dictionary
#returns dictionary {doc_id: rank}
def map_docid_rank(rank_vector, ids_urls, graph_file):
    docid_rank = dict()
    graph = retrieve_graph(graph_file)
    edge_indices = graph.edge_indices
    for doc_id in ids_urls:
        rank = rank_vector[edge_indices[ids_urls[doc_id]]]
        docid_rank[doc_id] = rank
    return docid_rank   

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    #Dicitionary for saving the normalized weights for document vector
    lengths = dict()

    ids_urls = dict()

    #Number of docs read from csv
    total_docs = 1
    max_docs = 2000

    # Using readlines() 
    with open(in_dir, 'r', encoding="utf8") as urls_file:
        lines = urls_file.readlines() 
    random.shuffle(lines)

    # Strips the newline character 
    for page_url in lines: 
        if(total_docs > max_docs):
           break

        #If line is blank, just skip
        if page_url is None or page_url == ' ' or page_url == '\n' or page_url == '\t':
            continue
        
        print("Indexed pages: " + str(total_docs))
        #get the web page's contents as a dictionary with title and content zones as keys
        doc = get_content_soup(page_url)
        
        #save the different columns of the doc
        doc_id = total_docs
        ids_urls[doc_id] = page_url.rstrip("\n")
        #Remove punctuation in title and content
        doc_title = re.sub(r"[,;@#?!&$()%\[\]°~^_.+=\"><`|}{*':/]+ *", " ", doc["title"])
        doc_content = re.sub(r"([\[]).*?([\]])", "\g<1>\g<2>",  doc["content"])
        doc_content = re.sub(r"[,;@#?()\[\]°~^_.+=\"><`|}{*':/]+ *", " ", doc_content)

        print(doc_title)

        #The dictionaryies are updated, postings lists are updated or new terms added
        update_terms_zones_dictionary(doc_id, doc_title, ".title")
        update_terms_zones_dictionary(doc_id, doc_content, ".content")

        total_docs += 1

    #This section stores the Log TF using the word counts in the postings in the dictionary
    #It saves the Log TF in an auxiliary dictionary named lengths
    for word in dictionary:
        #Get postings list for the word
        postings_list = dictionary[word]

        for docID_termF in postings_list:
            #Get the vector for the doc, where the docId is docID_termF[0]
            #If there is no vector for this doc, then create a new dict
            #I am using dictionaries as the vector for the word only for the calculations
            doc_vector = lengths.get(docID_termF[0], dict())
            #I add the logarithmic term frequency to that document vector
            doc_vector[word] = 1 + math.log(docID_termF[1], 10)
            #Save that to its corresponding doc
            lengths[docID_termF[0]] = doc_vector

    #This section normalizes the Log TFs 
    for doc_vector in lengths.values():
        #We store each of the values in a list and then use:
        #np.linalg.norm to do the normalization = sqrt(sum(values^2))
        weights = doc_vector.values()
        #We get the vectors magnitude
        magnitude = np.linalg.norm(np.array(list(weights)))
        for word in doc_vector.keys():
            #For every word entry in the vector 
            #normalize by dividing the weight by the magnitude
            doc_vector[word] = doc_vector[word] / magnitude

    #This section replaces the word count in the tuple of the dictionary with the Normalized Log TF
    #It also sorts the postings list by doc ID
    for word in dictionary:
        #Get postings list for the word
        postings_list = dictionary[word]
        new_postings_list = list()
        for docID_termF in postings_list:
            docID_termF = ( docID_termF[0], lengths[docID_termF[0]][word] )
            new_postings_list.append(docID_termF)
        new_postings_list.sort()
        dictionary[word] =  new_postings_list
    
    #In this sections calculate the page rank and map docs ids to their rank
    rank_vector = page_rank("saved/graph.pkl", 0.1)
    ids_ranks = map_docid_rank(rank_vector, ids_urls, "saved/graph.pkl")

    with open('debug/ugly_dictionary.txt', 'w') as fp:
        json.dump(dictionary, fp)
    with open('debug/ugly_ids_urls.txt', 'w') as fp:
        json.dump(ids_urls, fp)
    with open('debug/ugly_ids_ranks.txt', 'w') as fp:
        json.dump(ids_ranks, fp)

    #This section traverse each word (key) in the dictionary, get its postings list and save it in a different file  
    postings_list_file = open(out_postings, "wb") 
    for word in dictionary:
        #Get postings list for the word
        postings_list = dictionary[word]
        #Get the document frequency
        document_frequency = len(postings_list)
        #Know the starting position for the pointer
        postings_list_position = postings_list_file.tell()
        # Writing to file 
        pickle.dump(postings_list, postings_list_file)
        #Replace postings list with reference to the position
        dictionary[word] = (document_frequency, postings_list_position)
    #Close the postings lists file
    postings_list_file.close() 

    #Now open the dictionary file and save the three dictionaries
    with open(out_dict, 'wb') as dictionary_file:
        pickle.dump(total_docs, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(dictionary, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(ids_urls, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(ids_ranks, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)
    
    '''
    The structure we have is:

    dictionary.txt: Has three dictionaries
    {word.zone : [doc_freq, pointer], word.zone: [doc_freq, pointer], ...}
    {date : [doc_freq, pointer], date: [doc_freq, pointer], ...}
    {court : [doc_freq, pointer], court: [doc_freq, pointer], ...}

    postings.txt: Has the postings for the three dictionaries
    For the dictionary postings:
        [[docID,termFrequency],[docID,termFrequency]]
            [[docID,termFrequency]] ...
    For the date_dictionary postings:
        [docId, docId, docId, docId]
    For the court_dictionary postings:
        [docId, docId, docId, docId]
    ...

    Both documents together would be:
    { word.zone: [doc_freq, [[docID,termFrequency], ... ]], 
        word.zone: [doc_freq, [[docID,termFrequency].}, ...]] }
    { date: [doc_freq, [docID, docID, ... ]], date: [doc_freq, [docID, docID, ... ]] }
    { court: [doc_freq, [docID, docID, ... ]], date: [doc_freq, [docID, docID, ... ]] }

    lengths.txt
    [document: [word: weight, word: weight, ...], document: [word: weight, word: weight, ...]]
    Decided to make it like this to keep control of which weights correspond to which words
    Although for a document I will traverse all the weights to get the score
    If the word is not in the document vector [which in my case is a dictionary], then its weight is 0
    This way I am no using a sparse matrix

    '''

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)

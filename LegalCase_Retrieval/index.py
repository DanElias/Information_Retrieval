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
from nltk import stem
from nltk.corpus import stopwords


#stemmer
stemmer = stem.PorterStemmer()
#set stop words to be ignored
stop_words = set(stopwords.words('english'))
#Dictionary for saving our tokens and the reference to their postings list.
#it has terms from title and content zones
dictionary = dict()
#Dictionary for saving the postings list of doc ids for each date (year)
#this a field.
date_dictionary = dict()
#Dictionary for saving our tokens and the reference to their postings list
#this is a field.
court_dictionary = dict()


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

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

def update_date_field_dictionary(doc_id, date):
    #Adds the doc id to the date field dictionary
    #check if the date already appears in the dictionary
    #if the date is not present, create a new list for the new entry
    postings_list = date_dictionary.get(date, list())
    #Bulletproof to check there are no repeated doc ids
    if(doc_id not in postings_list):
        postings_list.append(doc_id)
        date_dictionary[date] = postings_list

def update_court_field_dictionary(doc_id, court):
    #Adds the doc id to the court field dictionary
    #check if the court already appears in the dictionary
    #if the court is not present, create a new list for the new entry
    postings_list = court_dictionary.get(court, list())
    #Bulletproof to check there are no repeated doc ids
    if(doc_id not in postings_list):
        postings_list.append(doc_id)
        court_dictionary[court] = postings_list

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    maxInt = sys.maxsize

    while True:
        # decrease the maxInt value by factor 10 
        # as long as the OverflowError occurs.
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt/10)

    #Dicitionary for saving the normalized weights for document vector
    lengths = dict()

    #Number of docs read from csv
    total_docs = 1
    max_docs = 1000

    #Data stored in csv read file line by line and save columns data
    with open(os.path.join(in_dir), 'r', encoding="utf8") as data_csv:
        reader = csv.DictReader(data_csv)
        #each line corresponds to a document
        for doc in reader:

            #if(total_docs > max_docs):
            #   break

            #If line is blank, just skip
            if doc is None:
                continue
            
            #save the different columns of the doc
            doc_id = int(doc["document_id"])
            #Remove punctuation in title and content
            doc_title = re.sub(r"[,;@#?!&$()%\[\]°~^_.+=\"><`|}{*':/]+ *", " ", doc["title"])
            doc_content = re.sub(r"[,;@#?!&$()%\[\]°~^_.+=\"><`|}{*':/]+ *", " ", doc["content"])
            doc_date = doc["date_posted"]
            doc_year = doc_date[0:4]
            doc_court = doc["court"]

            #The dictionaryies are updated, postings lists are updated or new terms added
            update_terms_zones_dictionary(doc_id, doc_title, ".title")
            update_terms_zones_dictionary(doc_id, doc_content, ".content")
            update_date_field_dictionary(doc_id, doc_year)
            update_court_field_dictionary(doc_id, doc_court)

            total_docs += 1

        data_csv.close()

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

    ''' 
    with open('ugly_dictionary.txt', 'w') as fp:
        json.dump(dictionary, fp)
    '''
    #Determine the relevance of each doc by the court that it has in its court field
    #Save the relevant docs and their relevance
    relevant_courts_dict = { "SG Court of Appeal":2, "SG Privy Council":2, "UK House of Lords":2, "UK Supreme Court":2,
    "High Court of Australia":2, "CA Supreme Court":2, "SG High Court":1.5, "Singapore International Commercial Court":1.5,
    "HK High Court": 1.5, "HK Court of First Instance": 1.5, "UK Crown Court": 1.5, "UK Court of Appeal": 1.5, "UK High Court": 1.5, 
    "Federal Court of Australia": 1.5, "NSW Court of Appeal": 1.5, "NSW Court of Criminal Appeal": 1.5, "NSW Supreme Court": 1.5}

    relevant_docs = dict()
    
    for court_name in relevant_courts_dict:
        court_postings_list = court_dictionary.get(court_name, -1)
        if(court_postings_list != -1):
            for docid in court_postings_list:
                #save a dictionary of docID and its relevance (2 or 1.5) according to its court
                relevant_docs[docid] = relevant_courts_dict[court_name]

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
    for date in date_dictionary:
        #Get postings list for the date
        postings_list = date_dictionary[date]
        #Get the document frequency
        document_frequency = len(postings_list)
        #Know the starting position for the pointer
        postings_list_position = postings_list_file.tell()
        # Writing to file 
        pickle.dump(postings_list, postings_list_file)
        #Replace postings list with reference to the position
        date_dictionary[date] = (document_frequency, postings_list_position)
    for court in court_dictionary:
        #Get postings list for the date
        postings_list = court_dictionary[court]
        #Get the document frequency
        document_frequency = len(postings_list)
        #Know the starting position for the pointer
        postings_list_position = postings_list_file.tell()
        # Writing to file 
        pickle.dump(postings_list, postings_list_file)
        #Replace postings list with reference to the position
        court_dictionary[court] = (document_frequency, postings_list_position)
    #Close the postings lists file
    postings_list_file.close() 

    #Now open the dictionary file and save the three dictionaries
    with open(out_dict, 'wb') as dictionary_file:
        pickle.dump(total_docs, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(dictionary, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(date_dictionary, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(court_dictionary, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(relevant_docs, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)
    
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

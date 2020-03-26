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
import numpy as np
from nltk import stem

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    stemmer = stem.PorterStemmer()

    #Dictionary for saving our tokens and the reference to their postings list
    dictionary = dict()
    #Dicitionary for saving the normalized weights for document vector
    lengths = dict()
    #Number of files that will be indexed
    num_files = 100000
    #1. We have to open the reuters training docs directory and traverse it, opening each doc.
     #List all files in the dir and sort them by numerical order, to have sorted postings lists
    lst = os.listdir(in_dir)
    lst.sort(key=lambda f: int(re.sub(r'\D', '', f)))

    #2. For each file in the dir:
    for filename in lst:
        #Open it
        f = open(in_dir+"/"+filename, "r")
        #Read it
        text = f.read()
        #Get the sentences in the file
        sentences = nltk.sent_tokenize(text)

        for sentence in sentences:
            #For each sentence get the words that compose it
            words = nltk.word_tokenize(sentence)

            for word in words:
            
                word = stemmer.stem(word.lower())

                #For each word check if its already registered in the dictionary
                #If its not, a new postings list is created for that word
                #If its already registered, its postings list is retrieved
                postings_list = dictionary.get(word, list())
                
                #This is to check if the word is not registered and a postings list 
                #was just created for it
                if(len(postings_list) == 0):
                    #Create the tuple of (docId, termF)
                    docID_termF = (int(filename), 1)
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
                    if(last_appearance[0] == int(filename)):
                        #If it was in the current doc, we add to the term frequency
                        postings_list[len(postings_list) - 1] = (last_appearance[0], last_appearance[1] + 1)
                    else:
                        #If it was not, we append a new tuple to the list and start with term frequency = 1
                        docID_termF = (int(filename), 1)
                        postings_list.append(docID_termF)
                        dictionary[word] = postings_list

        #This is to limit the number of docs that will be indexed               
        num_files -= 1 
        if(num_files <= 0): 
            break
    
    with open('ugly_dictionary.txt', 'w') as fp:
        json.dump(dictionary, fp)
    #After checking all the words in the files, we have our dictionary with its postings lists
    # But we don't want to save the postings list with the dictionary as they can be quite large
    # Now we will traverse each word (key) in the dictionary, get its postings list and save it in a different file        
    
    postings_list_file = open(out_postings, "wb") 
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
    #Now open the dictionary file and save it

    with open(out_dict, 'wb') as dictionary_file:
        pickle.dump(dictionary, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)

    '''
    with open('ugly_lengths.txt', 'w') as fp:
        json.dump(lengths, fp)
    '''
    #Here we use the cosine normalization
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

    #Save it in the same working directory, where search.py is also suppossed to be
    with open(os.path.join(os.getcwd(), "lengths.txt"), 'wb') as lengths_file:
        print(os.path.join(os.getcwd(), "lengths.txt"))
        pickle.dump(lengths, lengths_file, protocol = pickle.HIGHEST_PROTOCOL)

    '''
    with open('ugly_lengths_normalized.txt', 'w') as fp:
        json.dump(lengths, fp)
    '''
    '''
    with open(out_dict, 'w') as fp:
        json.dump(dictionary, fp)
    '''

    '''
    The structure we have is:

    dictionary.txt
    {word : [doc_freq, pointer], word: [doc_freq, pointer], ....}

    postings.txt
    [[docID,termFrequency],[docID,termFrequency]]
     [[docID,termFrequency]]
    ...

    Both documents together would be:
    { word: [doc_freq, [[docID,termFrequency],[docID,termFrequency]]], 
    word: [doc_freq,  [[docID,termFrequency]]] }

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

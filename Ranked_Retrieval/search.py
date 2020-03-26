'''
'''

#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import pickle
from nltk import stem
import math
from collections import defaultdict
import os
from heapq import heapify, heappush, heappop 

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

#Opening file error function
def error_opening_file(file):
    print("Error ocurred: could not open file " + file)

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    dictionary = dict()
    lengths = dict()
    stemmer = stem.PorterStemmer()
    
    #Open dictionary in memory
    with open(dict_file, "rb") as dictionary_f:
        dictionary = pickle.load(dictionary_f)
    
    with open(os.path.join(os.getcwd(), "lengths.txt"), "rb") as lengths_f:
        lengths = pickle.load(lengths_f)

    #Open and read each line of the queries file
    try:
        fd = open(queries_file, 'r', encoding="utf8") 
        line = fd.readline()
    except:
        error_opening_file(queries_file)
        sys.exit(2)

    #Erase the contents of the file
    output_file = open(results_file,"w")
    output_file.close()
    #Open file to append lines
    output_file = open(results_file,"a")

    #Evaluate each line or query
    while line:

        #If its blank just write nothing
        if(line == " " or line == "\n" or line == "\t"):
            output_file.write('\n')
            line = fd.readline()
            continue

        #Tokenize the query
        tokens = nltk.word_tokenize(line)
        scores = defaultdict(lambda: 0)

        # Creating empty heap 
        heap = [] 
        heapify(heap)

        #COSINE SCORE
        #For each query term t
        stemmed_tokens = list()
        unique_tokens = set()
        for token in tokens:
            stemmed_tokens.append(stemmer.stem(token.lower()))
            unique_tokens.add(stemmer.stem(token.lower()))

        for token in unique_tokens:
           
            docFreq_pointer = dictionary.get(token, -1)

            if(docFreq_pointer == -1):
                continue

            # get the document_frequency for the token
            document_frequency = docFreq_pointer[0]

            #read the posting lists, only open the file in this line
            postings_f = open(postings_file, "rb")
            #Move to the position in the file where docFreq_pointer[1] = pointer
            postings_f.seek(docFreq_pointer[1])
            #Only read the object at that position
            token_postings_list = pickle.load(postings_f)
            #Close file
            postings_f.close()
            #print("token postings list:")
            #print(token_postings_list)

            for docID_termF in token_postings_list:
                doc_vector = lengths[docID_termF[0]]
                query_idf = (len(lengths) + 1) / (document_frequency + 1)

                """
                print("current token of query:")
                print(token)

                print("term frequency in query:")
                print(stemmed_tokens.count(token))

                print("weight of term in doc vector:")
                print(doc_vector[token])

                print("tf of term in query:")
                print(1 + math.log(stemmed_tokens.count(token), 10))

                print("idf division:")
                print(query_idf)

                print("idf of term in query:")
                print(math.log((query_idf),10))

                print("weight of the term in query:")
                print(((1 + math.log(stemmed_tokens.count(token), 10)) * math.log((query_idf),10)))
                """
                
                scores[docID_termF[0]] += (doc_vector[token]) * ((1 + math.log(stemmed_tokens.count(token), 10)) * math.log((query_idf),10))
                heappush(heap, ( -1 * scores[docID_termF[0]] , docID_termF[0]))

        maxTen = heap[:10]
        result = []
        for cosineSim_docId in maxTen:
            result.append(cosineSim_docId[1])
        #Write the result with the specified format
        output_file.write(' '.join(map(str, result)))
        #Prepare new line
        output_file.write("\n")

        line = fd.readline()

    output_file.close
    fd.close
    
dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)

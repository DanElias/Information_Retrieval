'''

    Copyright 2020 Daniel Elias Becerra

'''

#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import pickle

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

#Opening file error function
def error_opening_file(file):
    print("Error ocurred: could not open file " + file)

#Only get the postings list for that term and not all the postings lists for all the dictionary
def get_postings_list(dictionary, term):
    postings_f = open(postings_file, "rb")
    postings_f.seek(dictionary[term])
    postings_list = pickle.load(postings_f)
    postings_f.close()
    return postings_list

def and_query(list1, list2):
    if(list1 is None or list2 is None):
        return list()

    merge_list = list()
    i = j = 0

    while i < len(list1) and j < len(list2):
        posting1 = list1[i]
        posting2 = list2[j]
        if(posting1 == posting2):
            merge_list.append(posting1)
            i += 1
            j += 1
        elif(posting1 < posting2):
            i += 1
        else:
            j += 1
            
    return merge_list

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    dictionary = dict()

    #Open and read each line of the queries file
    try:
        fd = open(queries_file, 'r', encoding="utf8") 
        line = fd.readline().lower()
    except:
        error_opening_file(queries_file)
        fd.close()
        sys.exit(2)
    
    #TO-DO : Parse query and do the functions for each AND OR NOT
    while line:
        line = fd.readline()
    fd.close

    #Open dictionary in memory
    with open(dict_file, "rb") as dictionary_f:
        dictionary = pickle.load(dictionary_f)

    print(and_query(get_postings_list(dictionary, "and"), get_postings_list(dictionary, "prospects")))
    
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

'''
'''

#!/usr/bin/python3
import re
import nltk
from nltk.corpus import wordnet
import sys
import getopt
import pickle
from nltk import stem
from nltk.corpus import stopwords
import math
from collections import defaultdict
import os
from heapq import heapify, heappush, heappop 
import pip
import numpy
print(numpy.__file__)

stop_words = set(stopwords.words('english'))
total_docs = 0
dictionary = dict()
date_dictionary = dict()
court_dictionary = dict()
relevant_docs = dict()
stemmer = stem.PorterStemmer()

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

#Opening file error function
def error_opening_file(file):
    print("Error ocurred: could not open file " + file)

#Only add results when list1[i] == list2[j]
def and_query(list1, list2):
    
    merge_list = list()
    i = 0
    j = 0

    skip_offset = math.floor(math.sqrt(len(list1)))

    while i < len(list1) and j < len(list2):
        if(list1[i][0] == list2[j][0]):
            merge_list.append((list1[i][0], list1[i][1] + list2[j][1]))
            i += 1
            j += 1
        elif(i + skip_offset < len(list1)):
            if(list1[i + skip_offset][0] <= list2[j][0]):
                i += skip_offset
            elif(list1[i][0] < list2[j][0]):
                i += 1
            else:
                j += 1
        elif(list1[i][0] < list2[j][0]):
            i +=  1
        else:
            j += 1
    
    return merge_list

#Use query expansion with wordnet
def query_expansion(queries):
    expanded_queries = list()

    for query in queries:
        clean_query = re.sub(r"[,;@#?!&$()%\[\]°~^_.+=\"><`|}{*':/]+ *", " ", query)
        query_words = nltk.word_tokenize(clean_query)
        expanded_query = ""
        i = 0
        for word in query_words:
            #Dont find synonyms for stop words
            if( word in stop_words):
                continue
            word = word.lower()
            #These will be the synonym for the word in the query
            synonyms = set()
            #The synonyms include the same word we started with
            synonyms.add(word)
            for synset in wordnet.synsets(word):
                for lemma in synset.lemmas():
                    #Add the word synonyms
                    synonyms.add(lemma.name()) 
                    #Lets just add maximum 4 synonyms
                    if (len(synonyms) > 4):
                        break
                if (len(synonyms) > 4):
                    break
            #So now instead of just one word, it has trasnformed into a list of words
            query_words[i] = list(synonyms)
            #Now we add the words to the new query
            expanded_query = expanded_query + " ".join(query_words[i]) + " "
            #Keep track of which word we are exanping
            i += 1
        #Now append each expanded query to the final queries to be analyzed
        expanded_queries.append(expanded_query)
    return expanded_queries

#Receives the query to be processed
#returns the list of the most relevant docs for that query, sorted by docID for the AND
def ranked_retrieval_search(query, total_docs, dictionary, date_dictionary, court_dictionary, relevant_docs):
    #Tokenize the query, should not remove "" for the phrasal queries if this is implemented
    query = re.sub(r"[,;@#?!&$()%\[\]°~^_.+=\"><`|}{*':/]+ *", " ", query)
    #Tokenize
    tokens = nltk.word_tokenize(query)
    #cosine scores
    scores = defaultdict(lambda: 0)
    # Creating empty heap 
    heap = [] 
    heapify(heap)

    #COSINE SCORE
    #For each query term t
    stemmed_tokens = list()
    unique_tokens = set()

    for token in tokens:
        token = token.lower()
        if token in stop_words:
            continue

        stemmed_token = stemmer.stem(token)
        #new_token = stemmed_token  + ".title"
        #stemmed_tokens.append(new_token)
        #unique_tokens.add(new_token)
        new_token = stemmed_token  + ".content"
        stemmed_tokens.append(new_token)
        unique_tokens.add(new_token)
        

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

        # + 1 as I'm considering query to be another doc
        query_idf = (total_docs + 1) / (document_frequency + 1)
        query_idf = math.log((query_idf),10)

        for docID_termF in token_postings_list:
            doc_id = docID_termF[0] #doc id
            doc_tf = docID_termF[1] #the normalized log tf value for that token in that doc
            query_tf = 1 + math.log(stemmed_tokens.count(token), 10) #query tf
            # a doc is updated in each iteration, only the weight is summed to the corresponding doc
            # in the end each doc should have its total score
            relevance = relevant_docs.get(doc_id, 0)
            scores[doc_id] = scores[doc_id] + (doc_tf * query_tf * query_idf) + relevance

    '''
    scores = sorted(scores.items(), key=lambda x:x[1], reverse=True)
    results = list()
    for docId in scores:
        results.append(docId[0])
    '''
    return sorted(scores.items(), key=lambda x:x[0], reverse=False)

#Run the query search
def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    #Open dictionary in memory
    with open(dict_file, "rb") as dictionary_f:
        total_docs = pickle.load(dictionary_f)
        dictionary = pickle.load(dictionary_f)
        date_dictionary = pickle.load(dictionary_f)
        court_dictionary = pickle.load(dictionary_f)
        relevant_docs = pickle.load(dictionary_f)

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

    #Evaluate each line or query (it is assummed just one query line in the query file)
    while line:

        #If its blank just write nothing
        if(line == " " or line == "\n" or line == "\t" or line == ""):
            output_file.write('\n')
            line = fd.readline()
            #assume query file has just one query
            break

        queries = line.split('AND')

        expanded_queries = query_expansion(queries)

        final_result_scores = list()
        
        for query in expanded_queries:
            if(len(final_result_scores) == 0):
                final_result_scores = ranked_retrieval_search(query, total_docs, dictionary, date_dictionary, court_dictionary, relevant_docs)
            else: 
                final_result_scores = and_query(final_result_scores, ranked_retrieval_search(query, total_docs, dictionary, date_dictionary, court_dictionary, relevant_docs))
        
        final_result_scores.sort(key=lambda x:x[1], reverse=True)
        final_result = list()
        for docId in final_result_scores:
            final_result.append(docId[0])

        #Write the result with the specified format
        output_file.write(' '.join(map(str, final_result)))
        #end with new line?
        output_file.write("\n")
        #read next line that should be empty
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

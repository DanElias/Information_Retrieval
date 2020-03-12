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
    #Number of files that will be indexed
    num_files = 1000000
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
        #This " " token will be used for NOT queries
        not_postings_list = dictionary.get(" ", list())
        not_postings_list.append(int(filename))
        dictionary[" "] = not_postings_list

        for sentence in sentences:
            #For each sentence get the words that compose it
            words = nltk.word_tokenize(sentence)

            for word in words:
                
                word = word.lower()
                word = stemmer.stem(word)
                

                #For each word check if its already registered in the dictionary
                #If its not, a new postings list is created for that word
                #If its already registered, its postings list is retrieved
                postings_list = dictionary.get(word, list())
                
                #This is to check if the word is not registered and a postings list 
                #was just created for it
                if(len(postings_list) == 0):
                    #In that case save the postings list in the dictionary
                    dictionary[word] = postings_list
                    #Then add the file name (id) in which the word appears
                    postings_list.append(int(filename))

                #If the word was already in the dictionary, we check that the last entry
                #in its posting list is not the same as the filename (id) we are currently checking
                #as we don't want duplicate doc ids in the postings list
                elif(postings_list[len(postings_list)-1] != int(filename)):
                    #So if its the first time that it appears in the file we save the filename (id)
                    postings_list.append(int(filename))

        #This is to limit the number of docs that will be indexed               
        num_files -= 1 
        if(num_files <= 0): 
            break
    
    #with open('ugly_dictionary.txt', 'w') as fp:
        #json.dump(dictionary, fp)
    #After checking all the words in the files, we have our dictionary with its postings lists
    # But we don't want to save the postings list with the dictionary as they can be quite large
    # Now we will traverse each word (key) in the dictionary, get its postings list and save it in a different file        
    
    postings_list_file = open(out_postings, "wb") 
    for word in dictionary:
        postings_list = dictionary[word]
        #Know the starting position
        postings_list_position = postings_list_file.tell()
        # Writing to file 
        pickle.dump(postings_list, postings_list_file)
        #Replace postings list with reference to the position
        dictionary[word] = postings_list_position
    #Close the postings lists file
    postings_list_file.close() 
    #Now open the dictionary file and save it
    
    with open(out_dict, 'wb') as dictionary_file:
        pickle.dump(dictionary, dictionary_file, protocol=pickle.HIGHEST_PROTOCOL)
    '''
    with open(out_dict, 'w') as fp:
        json.dump(dictionary, fp)
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

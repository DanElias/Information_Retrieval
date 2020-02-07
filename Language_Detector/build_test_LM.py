#!/usr/bin/python3
"""
    Copyright 2020 Daniel Elias Becerra

    Language Detector, determines if the given sentence is Indonesian
    Malaysian, Tamil or another Language, based on a created Language Model
    using character 4-grams. 

    I'm using the unigram version of the 4-gram for the probability calculation
    which is dividing the count of the 4gram unigram by the count of all 4-grams (regardless of prefix)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import getopt
#For regular expressions:
import re
#For NLP tasks:
import nltk
#For dictionary handling:
import json
#For the log function
import math
#For the variance:
import numpy
#For creating the 4grams:
from nltk.util import ngrams

"""
    This function builds language models for each label
    each line in in_file contains a label and a string separated by a space
    Returns a Dictionary that contains the LM's for each Language
"""
def build_LM(in_file):
    #Declaration of the dictionaries
    indonesian_LM = dict()
    malaysian_LM = dict()
    tamil_LM = dict()
    #This is the dictionary that will be returned by the function
    languages = dict()
    
    print('building language models...')

    #Try opening the file in read mode and test reading the first line
    #[1]https://stackabuse.com/read-a-file-line-by-line-in-python/
    try:
        fd = open(in_file, 'r', encoding="utf8") 
        #1. Read the line make all letters lower case
        line = fd.readline().lower()
    except:
        error_opening_file(in_file)
        fd.close()
        sys.exit(2)

    #[2]https://kite.com/python/docs/nltk.ngrams  -  Learnt about nltk ngrams
    #[3]https://www.quora.com/How-do-I-remove-punctuation-from-a-Python-string - Learnt about regex in Python
    #[4]https://stackoverflow.com/questions/33642522/python-regex-sub-with-multiple-patterns
    # As we are using one smoothing, these variables will count how many 4grams each language has
    # Later on we will add this count to the size of the complete vocabulary
    count_indonesian_LM = 0
    count_malaysian_LM = 0
    count_tamil_LM = 0
    #We read line by line
    while line:
        #2. Patterns to be deleted from the line = punctuation, special characters, line breaks, digits
        pattern1 = r'[^\w\s]'
        pattern2 = r'\n'
        pattern3 = r'[0-9]'
        combined_pattern = r'|'.join((pattern1, pattern2, pattern3))
        line_no_punctuation = re.sub(combined_pattern,'',line)
        #3. Partition the line into words, when a white space is found
        line_partitioned =  line_no_punctuation.partition(' ')
        #4. The first word of the line is its language, don't use for the LM
        line_language = line_partitioned[0]
        #5. The next words will be used for the LM, we add [0] as we want all the words, no longer separated
        line_string = line_partitioned[2:][0]
        #6. We generate the character 4 grams and save them into a list, we use <S> and <E> for more accuracy
        line_ngrams_list = list(ngrams(
                                line_string, 
                                4, 
                                pad_left=True, 
                                pad_right=True, 
                                left_pad_symbol='<S>', 
                                right_pad_symbol='<E>'
                            ))
        #7. Count each time a ngram appears and add to its count in corresponding dictionary.
        # Also count how many ocurrences of ngram occurr in the Language
        for ngram in line_ngrams_list:
            ngram_joined = ''.join(ngram)

            #8. This is the one-smoothing, if its the first time we see it in each dictionary, we add it once
            #Therefore we will have also ngrams that appear in other languages, but just counted once
            #Probability will not be zero, it will change latter on when we know the number of 4grams for the LM's
            if not ngram_joined in indonesian_LM:
                indonesian_LM[ngram_joined] = [1, 0.0]

            if not ngram_joined in malaysian_LM :
                malaysian_LM[ngram_joined] = [1, 0.0]

            if not ngram_joined in tamil_LM:
                tamil_LM[ngram_joined] = [1, 0.0]

            #Here is where we add to the count of each dictionary
            if line_language == "indonesian":
                indonesian_LM[ngram_joined][0] += 1
            elif line_language == "malaysian":
                malaysian_LM[ngram_joined][0] += 1
            else :
                tamil_LM[ngram_joined][0] += 1

        if line_language == "indonesian":
            count_indonesian_LM += len(line_ngrams_list)
        elif line_language == "malaysian":
            count_malaysian_LM += len(line_ngrams_list)
        else :
            count_tamil_LM += len(line_ngrams_list)

        #Move forward to the next line
        line = fd.readline().lower()
    #Close the file after reading all of its content
    fd.close()  

    #9. Calculate the probability for each ngram in each LM and save it in the dictionary
    #These variables are used to validate that the product of all the ngram probabilities for each language is 1
    indonesian_probabilities = 0
    malaysian_probabilities = 0
    tamil_probabilities = 0
    vocabulary_size = len(indonesian_LM)

    for key, pair in indonesian_LM.items():
        indonesian_LM[key][1] = pair[0]/(vocabulary_size + count_indonesian_LM)
        indonesian_probabilities += indonesian_LM[key][1]
    for key, pair in malaysian_LM.items():
        malaysian_LM[key][1] = pair[0]/(vocabulary_size + count_malaysian_LM)
        malaysian_probabilities += malaysian_LM[key][1]
    for key, pair in tamil_LM.items():
        tamil_LM[key][1] = pair[0]/(vocabulary_size + count_tamil_LM)
        tamil_probabilities += tamil_LM[key][1]

    #10. Check that the sum of all the ngram probabilities for each language add up to 1
    print("Probabilities sum to 1: ")
    print(indonesian_probabilities)
    print(malaysian_probabilities)
    print(tamil_probabilities)

    #11. Finally save the language models in a single dictionary and return it
    languages["indonesian"] = indonesian_LM
    languages["malaysian"] = malaysian_LM
    languages["tamil"] = tamil_LM
    return languages
#---------------------------------END OF build_LM FUNCTION-----------------------------------------


"""
    This function builds test sentences and determines which language they belong to
    Reads the file that contains the lines to be tested.
    Writes to a file that has the name of the language is sentence belongs to and the sentence itself
"""
def test_LM(in_file, out_file, LM):
    print("testing language models...")

    #Open the file in read mode and test reading the first line
    output_file = open(out_file,"w")
    output_file.close()
    try:
        fd = open(in_file, 'r', encoding="utf8") 
        #1. Read the line as it is
        line = fd.readline()
    except:
        error_opening_file(in_file)
        fd.close()
        sys.exit(2)

    while line:
        #Decided to test the line just as it is
        #pattern1 = r'[^\w\s]'
        #pattern2 = r'\n'
        #pattern3 = r'[0-9]'
        #combined_pattern = r'|'.join((pattern1, pattern2, pattern3))
        #line_string = re.sub(combined_pattern,'',line)
        #2. Generate list of 4grams with the line read
        line_ngrams_list = list(ngrams(
                                line, 
                                4, 
                                pad_left=True, 
                                pad_right=True, 
                                left_pad_symbol='<S>', 
                                right_pad_symbol='<E>'
                            ))

        #We will store the probabilities for each language for each linee
        probability_indonesian = 0
        probability_malaysian = 0
        probability_tamil = 0
        
        #We joing the ngram to seach for it in each LM
        for ngram in line_ngrams_list:
            ngram_joined = ''.join(ngram)
            #4. Start summing the logs of the probabilites to know the probability for language for the line 
            #All three LM have the same keys because of the the one smoothing,
            #Therefore this condition, doesn't matter which LM we check in
            #Also, this condition is to check if the 4gram exists in the LM, if it doesn't we just ignore it
            if ngram_joined in LM["indonesian"]:
                probability_indonesian += math.log(LM["indonesian"].get(ngram_joined)[1])
                probability_malaysian += math.log(LM["malaysian"].get(ngram_joined)[1])
                probability_tamil += math.log(LM["tamil"].get(ngram_joined)[1])

        
        print(line)
        print(probability_indonesian)
        print(probability_malaysian)
        print(probability_tamil)
        
        #5. We see which probability is the highest
        #Because of logs the sums are negative, but max function still works
        probabilities = {
                probability_indonesian:"indonesian",
                probability_malaysian:"malaysian",
                probability_tamil:"tamil"
            }
        winning_probability = probabilities.get(max(probabilities))

        #6. Determine if a sentence is alien "other"
        #Tried determining which languages where alien, but didn0't have that much luck
        #Only works if the variance is 0 (equal probability for each language)
        #But it fails for the case of 
        # Oel hu Txew trram na'rngit tarmok, tsole'a syeptutet atsawl frato m srey.
        # As for examen 'r a m  ' actually appears in Tamil, so it believes it is tamil
        #Maybe with some other statistical formula like T test or something it could better determine
        # if the sentence is alien, but I don't really remember this hypotheses tests.
        variance = numpy.var([probability_indonesian, probability_malaysian, probability_tamil])
        if(variance == 0):
            winning_probability = "other"
        
        #7. Write to the file 
        output_file = open(out_file,"a")
        output_file.write(winning_probability + ' ' + line)

        #Move forward to the next line
        line = fd.readline()

    #Close the file
    fd.close()
#---------------------------------END OF test_LM FUNCTION-----------------------------------------

#Usage function
def usage():
    print("usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file")

#Opening file error function
def error_opening_file(file):
    print("Error ocurred: could not open file " + file)

#Retrieve the txt arguments and validate them
input_file_b = input_file_t = output_file = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"

if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)

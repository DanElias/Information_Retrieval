#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import nltk
import sys
import getopt
import re
import json

from nltk.util import ngrams

indonesian_LM = dict()
malaysian_LM = dict()
tamil_LM = dict()

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print('building language models...')
    # This is an empty method
    # Pls implement your code in below

    #Open the file in read mode and test reading the first line
    #https://stackabuse.com/read-a-file-line-by-line-in-python/
    try:
        fd = open(in_file, 'r', encoding="utf8") 
        #1. Read the line make all letters lower case
        line = fd.readline().lower()
    except:
        error_opening_file(in_file)
        fd.close()
        sys.exit(2)

    #https://kite.com/python/docs/nltk.ngrams
    #https://www.quora.com/How-do-I-remove-punctuation-from-a-Python-string
    #https://stackoverflow.com/questions/33642522/python-regex-sub-with-multiple-patterns
    # These variables will be used to count how many ocurrences of ngram occurr in the Language
    count_indonesian_LM = 0
    count_malaysian_LM = 0
    count_tamil_LM = 0
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
        #6. We generate the character 4 grams and save them into a list
        ine_string = ' '.join(line_string.split())
        line_ngrams_list = list(ngrams(
                                line_string, 
                                4, 
                                pad_left=True, 
                                pad_right=True, 
                                left_pad_symbol='<S>', 
                                right_pad_symbol='<E>'
                            ))
        #7. Count each time a ngram appears and save it in its corresponding dictionary.
        # Also count how many ocurrences of ngram occurr in the Language
        for ngram in line_ngrams_list:
            ngram_joined = ''.join(ngram)

            #8. This is the one-smoothing
            if not ngram_joined in indonesian_LM:
                indonesian_LM[ngram_joined] = [1, 0.0]

            if not ngram_joined in malaysian_LM :
                malaysian_LM[ngram_joined] = [1, 0.0]

            if not ngram_joined in tamil_LM:
                tamil_LM[ngram_joined] = [1, 0.0]

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

        line = fd.readline().lower()
            
    #9. Calculate the probability for each ngram in each LM
    #10. Validate that the product of all the ngram probabilities for each language is 1
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

    with open('indonesian.txt', 'w') as file:
     file.write(json.dumps(indonesian_LM))
    with open('malaysian.txt', 'w') as file:
     file.write(json.dumps(indonesian_LM)) # use `json.loads` to do the reverse
    with open('tamil.txt', 'w') as file:
     file.write(json.dumps(indonesian_LM)) # use `json.loads` to do the reverse
    
    fd.close()

def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    # This is an empty method
    # Pls implement your code in below

    #Open the file in read mode and test reading the first line
    #https://stackabuse.com/read-a-file-line-by-line-in-python/
    try:
        fd = open(in_file, 'r', encoding="utf8") 
        #1. Read the line make all letters lower case
        line = fd.readline().lower()
    except:
        error_opening_file(in_file)
        fd.close()
        sys.exit(2)

    #https://kite.com/python/docs/nltk.ngrams
    #https://www.quora.com/How-do-I-remove-punctuation-from-a-Python-string
    #https://stackoverflow.com/questions/33642522/python-regex-sub-with-multiple-patterns
    # These variables will be used to count how many ocurrences of ngram occurr in the Language
    while line:
        #2. Patterns to be deleted from the line = punctuation, special characters, line breaks, digits
        pattern1 = r'[^\w\s]'
        pattern2 = r'\n'
        pattern3 = r'[0-9]'
        combined_pattern = r'|'.join((pattern1, pattern2, pattern3))
        line_string = re.sub(combined_pattern,'',line)
        line_string = ' '.join(line_string.split())
        line_ngrams_list = list(ngrams(
                                line_string, 
                                4, 
                                pad_left=True, 
                                pad_right=True, 
                                left_pad_symbol='<S>', 
                                right_pad_symbol='<E>'
                            ))

        probability_indonesian = 1
        probability_malaysian = 1
        probability_tamil = 1
        for ngram in line_ngrams_list:
            ngram_joined = ''.join(ngram)

            if ngram_joined in indonesian_LM:
                probability_indonesian *= indonesian_LM.get(ngram_joined)[1]
                probability_malaysian *= malaysian_LM.get(ngram_joined)[1]
                probability_tamil *= tamil_LM.get(ngram_joined)[1]

        print(probability_indonesian)
        print(probability_malaysian)
        print(probability_tamil)

        probabilities = {
                probability_indonesian:"indonesian",
                probability_malaysian:"malaysian",
                probability_tamil:"tamil"
            }
        winning_probability = probabilities.get(max(probabilities))
        print(line_string)
        print("The sentence is: " + winning_probability)
        print('\n')

        line = fd.readline().lower()
    fd.close()

def usage():
    print("usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file")

def error_opening_file(file):
    print("Error ocurred: could not open file " + file)

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

print ('The file works!')

#LM = build_LM(input_file_b)
build_LM(input_file_b)
#test_LM(input_file_t, output_file, LM)
test_LM(input_file_t, output_file, 0)

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

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

#Opening file error function
def error_opening_file(file):
    print("Error ocurred: could not open file " + file)

#Only get the postings list for that term and not all the postings lists for all the dictionary
def get_postings_list(dictionary, term):
    pointer = dictionary.get(term, -1)
    if(pointer == -1):
        return list()
    #open file but still not read it
    postings_f = open(postings_file, "rb")
    #Move to the position in the file
    postings_f.seek(pointer)
    #Only read the object at that position
    postings_list = pickle.load(postings_f)
    #Close file
    postings_f.close()
    #return the object
    return postings_list

#Only add results when list1[i] == list2[j]
def and_query(list1, list2):
    merge_list = list()
    i = j = 0

    skip_offset = math.floor(math.sqrt(len(list1)))

    
    while i < len(list1) and j < len(list2):
        if(list1[i] == list2[j]):
            merge_list.append(list1[i])
            i += 1
            j += 1
        elif(i + skip_offset < len(list1)):
            if(list1[i + skip_offset] <= list2[j]):
                i += skip_offset
            elif(list1[i] < list2[j]):
                i += 1
            else:
                j += 1
        elif(list1[i] < list2[j]):
            i +=  1
        else:
            j += 1

    '''
    while i < len(list1) and j < len(list2):
        if(list1[i] == list2[j]):
            merge_list.append(list1[i])
            i += 1
            j += 1
        elif(list1[i] < list2[j]):
            i += 1
        else:
            j += 1
    '''

    return merge_list

#Only add results when list1[i] < list2[j]
def and_not_query(list1, list2):
    if(list2 is None):
        return list1
    elif(list1 is None):
        return list()

    merge_list = list()
    i = j = 0
    
    while i < len(list1) and j < len(list2):
        if(list1[i] == list2[j]):
            i += 1
            j += 1
        elif(list1[i] < list2[j]):
            merge_list.append(list1[i])
            i += 1
        else:
            j += 1

    if(j >= len(list2)):
        while i < len(list1):
            merge_list.append(list1[i])
            i += 1

    return merge_list

#Merge lists
def or_query(list1, list2):
    merge_list = list()
    i = j = 0

    while i < len(list1) and j < len(list2):
        if(list1[i] == list2[j]):
            merge_list.append(list1[i])
            i += 1
            j += 1
        elif(list1[i] < list2[j]):
            merge_list.append(list1[i])
            i += 1
        else:
            merge_list.append(list2[j])
            j += 1

    while i < len(list1):
        merge_list.append(list1[i])
        i += 1

    while j < len(list2):
        merge_list.append(list2[j])
        j += 1

    return merge_list

#Evaluate the Postfix and do the corresponding operations
def postfix_evaluator(postfix, operators, dictionary):
    stack = []
    result = []
    for token in postfix:
        precedence = operators.get(token, 0)

        #Its a word
        if(precedence == 0):
            stack.append(get_postings_list(dictionary, token))
            continue

        #NOT
        if(token == "NOT"):
            second = stack.pop()
            first = get_postings_list(dictionary, " ")
            result = and_not_query(first, second)
            stack.append(result)
            continue
        
        #AND
        if(token == "AND"):
            second = stack.pop()
            first = stack.pop()
            result = and_query(first, second)
            stack.append(result)
            continue

        #OR
        if(token == "OR"):
            second = stack.pop()
            first = stack.pop()
            result = or_query(first, second)
            stack.append(result)
            continue
    
    result = stack.pop()
    return result

#Follow the shunting yard algorithm
def shunting_yard(tokens, operators, dictionary):
    queue = []
    stack = []
    stemmer = stem.PorterStemmer()
    for token in tokens:
        precedence = operators.get(token, 0)

        #If the token is a word
        if(precedence == 0):
            token = token.lower()
            token = stemmer.stem(token)
            queue.append(token)
            continue

        #If the token is a left parenthesis
        if(token == "("):
            stack.append(token)
            continue

        #If the token is a right parenthesis
        if(token == ")" and len(stack) > 0):
            while(stack[len(stack)-1] != "("):
                queue.append(stack.pop())
                if(len(stack) == 0):
                    break
           
            stack.pop()
            continue

        if(len(stack) > 0):
            #We need to pop the top operators from stack if it has higher precedence than the current token operator
            while(precedence >= operators.get(stack[len(stack)-1], 0) and operators.get(stack[len(stack)-1], 0) != 1 and operators.get(stack[len(stack)-1], 0) != 2):
                queue.append(stack.pop())
                if(len(stack) == 0):
                    break
                    
        stack.append(token)
        if(len(stack) > 0 and len(queue) > 0):
            if(token == "NOT" and stack[len(stack)-1] == "NOT" and queue[len(queue)-1] == "NOT"):
                stack.pop()
                queue.pop()

    while(len(stack) > 0):
        queue.append(stack.pop())

    return queue

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    dictionary = dict()
    #Operators and their precedence
    operators = {'(':1,')':2,'NOT':3, 'AND':4, 'OR':5}
    #Open dictionary in memory
    with open(dict_file, "rb") as dictionary_f:
        dictionary = pickle.load(dictionary_f)

    #Open and read each line of the queries file
    try:
        fd = open(queries_file, 'r', encoding="utf8") 
        line = fd.readline()
    except:
        error_opening_file(queries_file)
        fd.close()
        sys.exit(2)

    #Erase the contents of the file
    output_file = open(results_file,"w")
    output_file.close()
    #Open file to append lines
    output_file = open(results_file,"a")
    #Evaluate each line
    while line:
        #If its blank just write nothing
        if(line == " " or line == "\n" or line == "\t"):
            output_file.write('\n')
            line = fd.readline()
            continue

        #Tokenize the line
        tokens = nltk.word_tokenize(line)

        #If its just a word then get its postings list
        if(len(tokens) == 1):
            stemmer = stem.PorterStemmer()
            token = tokens[0].lower()
            token = stemmer.stem(token)
            result = get_postings_list(dictionary, token)
            output_file.write(' '.join(map(str, result)))
            output_file.write('\n')
            line = fd.readline()
            continue
        
        #Get the postfix of the query using the shunting yard algorithm
        postfix = shunting_yard(tokens, operators, dictionary)
        #Evaluate the postfix and get the result
        result = postfix_evaluator(postfix, operators, dictionary)
        #Write the result with the specified format
        output_file.write(' '.join(map(str, result)))
        #Prepare new line
        output_file.write('\n')

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


== Ranked Retrieval ==

This is the README file for A0000000X's submission

== Python Version ==

I'm using Python Version <3.7.6> for
this assignment.

== General Notes about this assignment ==

    index.py
    1. Open the reuters training data
    2. For each document
        3.Tokenize each line
        4. Tokenize words in line
        5. For each word
            6. Apply porter stemming and to lower
            7. Find word in dictionary and get postings list
                First I am storing postings list in the dictionary, later on I will substitute
                the dicitonary with its pointer to it in the postings.txt
            8. If its a new word, then create its postings list and append to it a pair
                (docID, termF) where termF starts in 1 and docID is the current filename as we are using reuters
            9. If its a word that was already in the dictionary, first we check if its last pair in the postings list was
                corresponding to the current docID, if it is not we insert a new pair (docID, termF) 
                where termF starts in 1 and docID is the current filename as we are using reuters
            9. If its a word that was already in the dictionary, and the last pair was already of the current docID,
                then we add one to the termF of this pair.
    10. For each word in the dictionary
        11. Retrieve its postings list
        12. Here I am also going to add something else:
            I will traverse each postings_list retriving each docID
            I will save in a new dictionary called lengths doc_vectors
            where lengths[docID] is a dictionary named doc_vector where 
            doc_vector[word] = 1 + math.log(docID_termF[1], 10)
            Therefore I am already calculating the Logarithmic TF of the words in each doc_vector
            I am using the dictionary because the docID can appear in another word in the dictionary
            so I don't want to lose the value of the TF for a word in the doc_vector for a docID
        13.After traversing the postings list I get the document frequency for the word
        14. Then I save in the postings_lists file the posting list using tell() and pickle dump
        15. Then in the dictionary of words I replace the postings list with a pair 
            (document_frequency, postings_list_position) where oostings_list_position 
            is the pointer to the postings list of that word
        16. I save the dictionary in a file
        17. Now in the indexing I also made the cosine normalization:
            18. I traverse the lenghts (remember it is a dictionary) retrieving each doc_vector (also a dictionary)
            19. For the doc_vector I get the Logarithmic TF values of each word
            20. I apply np.linalg.norm to this values to get the doc_vector magnitude
        21. Then for each word in the doc_vector
            22. I divide the word Logarithmic TF by the magnitude of the doc_vector
                doc_vector[word] = doc_vector[word] / magnitude
                And so I apply cosine normalization
        23. Finally I save the lengths dictionary in lengths.txt 
            
            NOTE: lengths.txt is saved in the current working directory and then automatically accessed by search.py
            Therefore it is not passed as a parameter, so please run the search.py and index.py in the same directory

            NOTE: length.txt is just saved as a dictionary and then just read completely by seach.py
            I know the same thing as done with the postings_lists can be applied to not load all the lengths
            dictionary into memory but I had no time to add this enhacement.
    
    search.py
    1. Open the dictionary file and save in dictionary
    2. Open the lenghts file and save in dictionary
    3. Open output file and erase its contents, open for append
    4. Open the queries file and read each line
    5. If its blank just write in results a blank line
    6. tokenize in words the query
    7. Apply porter stemmer and to lower to the token gotten from the query
        8. I am saving repeated tokens in an array and unique tokens in a set, 
        9. This is used to not calculate cosine similarity with repeated tokens (a choice of mine)
    10. Retirve postings for each token
    11. calculate for the token in the query its vector by doing TF-IDF operations needed
    12. Apply also the COSINESCORE algorithm without using the division by length as cosine normalization was already done at indexing
    13. Save score to heap
    14. retrieve the max 10 doc IDs and write them to results.txt
            

== Files included with this submission ==

    Only focus on:
    index.py
    search.py

    the others were just for testing

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[X] I, A213170X, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[X] I A0213170X, did not follow the class rules regarding homework
assignment, because of the following reason:

    I only changed that the cosine normalization is done in the indexing
    And for the DOT Product in the COSINE SCORE, I just multiply the doc_vector[word] value * query_vector[word] value
    where doc_vector[word] value already has log TF and cosine normalization
    and query_vector[word] has already the log TF * IDF

We suggest that we should be graded as follows:

    Some parts can be enhanced, but no time to do it :(

== References ==

    Only the class presentations, videos and forum discussions

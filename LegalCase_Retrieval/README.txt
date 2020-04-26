
== Legal Case Retrieval ==

This is the README file for A0213170X's submission

== Python Version ==

I'm using Python Version <3.7.6> for
this assignment.

== General Notes about this assignment ==

    index.py
    1. Open the csv to read data, bulletproofed so no OverflowError occurs
    2. For each line of the csv (which is a document) as a dictionary 
	 2.1 Get fields and zones of doc
	    2.1.1 Save doc_id as int
	    2.1.2 Save doc_title zone with no special characters
	    2.1.3 Save doc_content zone with no special characters
	    2.1.4 Save doc_date as string
	    2.1.5 Save doc_year (first 4 chars of doc_date)
	    2.1.6 Save doc_court
	   2.2 dictionary will have the terms gotten from title and content zones
		the terms have ".title" or ".content" concatenated respectively
		
	   2.3 update_terms_zones_dictionary(doc_id, text, zone)
	        2.3.1 Tokenizes the words of either the title zone or the content zone received
                2.3.2 Each token is sent to lower case
		2.3.3 English stop words are skipped
		2.3.4 Porter stemmer is used on the token
		2.3.5 The zone name is concatenated to the token
            	2.3.6 Find token in dictionary and update its postings its list (done for title and content zones)
                        First I am storing postings list in the dictionary, later on I will substitute
                        the dicitonary with its pointer to it in the postings.txt
		        
			If its a new token, then create its postings list and append to it a pair
                        (docID, termF) where termF starts in 1 and docID is the current doc_id
            		
			If its a token that was already in the dictionary, first I check if 
			its last pair in the postings list is equal to the current doc_id, 
			if it isn't, I insert a new pair (docID, termF), if its the same then
			then I add one to the termF of this pair.

	    2.4  update_date_field_dictionary(doc_id, doc_year)
	     Creates a dictionary with years as keys and values as postings lists
	     which are just lists with doc_ids that were published in that year
	    2.5  update_court_field_dictionary(doc_id, doc_year)
	     Creates a dictionary with court names as keys and values as postings lists
	     which are just lists with doc_ids that were made by that court
	    2.6 A count of the total indexed documents or cvs lines is also kept
    
     3. Now I change the dictionary counts to log tf and
            keep this info in an axuiliar dict called lengths
            I traverse each postings_list retriving each docID
            where lengths[docID] is a dictionary named doc_vector where 
            doc_vector[word] = 1 + math.log(docID_termF[1], 10)

     4. Now I normalize the log TFs in lengths
	   I used numpy here so please help me installing numpy :( couln't add it to project
	
     5. Then I replace in the dictionary, for each tuple (doc_id, tf) the
	    tf by the normalized log tf
	
     6. I create dictionary with the relevant courts with the given text file in luminous
	   I give a value of 2 to Important courts and 1.5 to ¿Important courts?
           Then I create another dictionary named relevant_docs so I know which documents
           were published by relevant courts.

     7. Then I save in the postings_lists file the posting list using tell() and pickle dump
        7.1 Then in the dictionary of words I replace the postings list with a pair 
            (document_frequency, postings_list_position) where oostings_list_position 
            is the pointer to the postings list of that word

     8. The same as 7 and 7.1 is done for date_dictionary 
     9. The same as 7 and 7.1 is done for court_dictionary 

     10. Finally I dump in the dictionary.txt 5 variables:
		total_docs indexed
		dictionary (title and content terms dictionary)
		date_dictionary
		court_dictionary
		relevant_docs
    
    search.py
    1. Open pickled variables:
	total_docs indexed
	dictionary (title and content terms dictionary)
	date_dictionary
	court_dictionary
	relevant_docs

    3. Open output file and erase its contents, open for append
    4. Open the queries file and read the line
    5. split queries by 'AND' and save in a list of queries
    6. expand queries = query_expansion(queries)
	uses wordnet to expand each word in each of the queries
	finds synonyms using wordnet.synset
	Then adds the original word and synonyms to the query to expand it
 	returns the expanded queries 
    7. for each of the expanded queries:
	7.1 uses the ranked retrieval algorithm (cosine similarity)
    	  7.1.1 tokenize in words the query
    	  7.1.2 Apply porter stemmer and to lower to the token gotten from the query
          7.1.3 I am saving repeated tokens in an array and unique tokens in a set, 
          7.1.4 This is used to not calculate cosine similarity with repeated tokens (a choice of mine)
    	  7.1.5 Retrieve postings for each token
		I commented retrieving postings for the token.title option, just left .content zone
		Exploration can be made by adding the .title tokens
		NOTE: here I add the relevance part of searching for doc ID in relevant_docs
    	  7.1.6 calculate for the token in the query its vector by doing TF-IDF operations needed
    	  7.1.7 Apply also the COSINESCORE algorithm without using the division by length as cosine normalization was already done at indexing
    	  7.1.8 Save scores and return the dictionary of this scores sorted by docID for the possible AND operations (merge algorithm with skip pointers)
	7.2 If another query is present by using AND then call again ranked retrieval on the second query
	    Then merge with the result of the previous call to ranked retrieval
	  7.2.1 and_query(list1, list2)
		Merges (intersection) the two query results and uses skip pointers
            
== Files included with this submission ==

    Only focus on:
    index.py
    search.py
    dictionary.txt
    postings.txt
    BONUS.txt 
     (had no time to write about it but I used wordnet and added more authority to the scores of docs found in relevant_docs
    README.txt
	

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

    PLEASE INSTALL NUMPY and help my team of one person, could not add it to my zip

We suggest that we should be graded as follows:

    Some parts can be enhanced, but no time to do it :(

== References ==

    Only the class presentations, videos and forum discussions

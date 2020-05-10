
== Web Search Engine for Computer Science ==

This is the README file for A0213170X's submission

== Python Version ==

I'm using Python Version <3.7.6> for
this assignment.

== General Notes about this assignment ==

	All the crawling process is in the document CRAWLER.txt

	index.py and search.py were all done all by myself, using Beautiful Soup and numpy only
	Tried making my own HTMLParser class but failed so I used Beautiful Soup

    index.py
    1. Open the crawled.txt in saved folder - page urls to be analyzed
    2. For each line of the crawled pages
	 2.1 Get fields and zones of doc
	 	Calls function get_content_soup()
		 	With Beautiful soup I obbatin the tags with 'p' and get the text
			tags with p correspond to .content zone
			tags with 'title' correspond to .title zone
			I return a dictionary with the processed text found in the page
	    2.1.1 Save doc_id as int
	    2.1.2 Save doc_title zone with no special characters
	    2.1.3 Save doc_content zone with no special characters
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
    
     3. Now I change the dictionary counts to log tf and
            keep this info in an axuiliar dict called lengths
            I traverse each postings_list retriving each docID
            where lengths[docID] is a dictionary named doc_vector where 
            doc_vector[word] = 1 + math.log(docID_termF[1], 10)

     4. Now I normalize the log TFs in lengths
	   I used numpy here so please help me installing numpy :( couln't add it to project
	
     5. Then I replace in the dictionary, for each tuple (doc_id, tf) the
	    tf by the normalized log tf

     6. Then I save in the postings_lists file the posting list using tell() and pickle dump
        6.1 Then in the dictionary of words I replace the postings list with a pair 
            (document_frequency, postings_list_position) where oostings_list_position 
            is the pointer to the postings list of that word

	 7. PAGERANK
	 	I obtain the ranks vector by calling page_rank functions
		 page_rank()
		 Page rank using a precomputed adjacency matrix of the crawled pages
		 10% probability of transporting to a random node
		 90% probabiliy of following a link in the node
		 random_probability = probability for teleportation
		 returns the rank vector "a"
		 
		 First it retrieves the graph we previously constructed with the crawler
		 7.1. Get total nodes in graph
		 7.2. Calculates teleportation weight = This is the value of the edge when it has no outlinks
		 7.3. Creates A matrix to be multiplied by the vector of probabilities
		 7.4. Initializes a probability vector of ones, same prob  for everyone
	
		 7.5. Construct A matrix
		 	Each row in the graph.edges is a vertex with its outlinks
			The no teleport weight is 1/outlinks * 0.9
			if edge == 1:
                # No teleportation
                weight = no_teleport + teleport
            else:
                # Teleportation needed
                weight = teleport

			This is better explained with the code 
		
		 7.6. Then with the A matrix why do dot product with the probabilities matrix X
		 7.7. We iterate until the x matrix stabilizes or max iterations achieved (I experimented with 100 its)
         7.8. The page rank vector is returned

	 8. I map the doc id given to the urls to its page rank and save this relation
		in a dictionary called ids_ranks, easier access in the search process

     9. Finally I dump in the dictionary.txt 5 variables:
		total_docs indexed
		dictionary (title and content terms dictionary)
		ids_urls (doc id and its url dictionary)
		ids_ranks (doc id and its rank)
    
    search.py
    1. Open pickled variables:
	total_docs indexed
	dictionary (title and content terms dictionary)
	ids_urls (doc id and its url dictionary)
	ids_ranks (doc id and its rank)

    3. Open output file and erase its contents, open for append
    4. Open the queries file and read the line
    5. split queries by 'AND' and save in a list of queries
	 NOTE: I decided to just leave the boolean handling as an extra feature
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

		Experiments: Remember I separated terms in dictionary with .title and .content zones
			I give more relevance if the term in query is found to have an entry as a .title in the dictionary
			This actually enhanced the results

		NOTE: here I add the relevance part of the PAGE RANK algorithm
    	  7.1.6 calculate for the token in the query its vector by doing TF-IDF operations needed
    	  7.1.7 Apply also the COSINESCORE algorithm without using the division by length as cosine normalization was already done at indexing
		  7.1.8 ADD THE RELEVANCE METRIC - THE DOC_IDS RANK IN dictionary ids_ranks to the scores I also add more relevance if token has .title (is in the html's title)
    	  7.1.9 Save scores and return the dictionary of this scores sorted by docID for the possible AND operations (merge algorithm with skip pointers)
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
	graph.py: a copy of the graph.py inside /crawler : more info on CRAWLER.txt
	content_finder.py: my failed attemp to parse HTML without BeautifulSoup
	/crawler
		- this folder has the files used for the crawling program - read CRAWLER.txt
	/saved
		- different results versions for running crawler
	/debug
		- just used to see results more graphically, they don't matter
	/queries
		- has example queries
	/wikipedia
		- has the queue.txt crawled.txt graph.pkl used in the last run of the crawler
	results.txt: my last results
    README.txt

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[X] I, A213170X, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[X] I A0213170X, did not follow the class rules regarding homework
assignment, because of the following reason:

    Please install numpy and Beautiful Soup, had no time to add them to submission and
	I really don't know how to do it

We suggest that we should be graded as follows:

    Some parts can be enhanced but I actually learned multithreading in Python
	and OOP in python, so that was a huge thing cause I did not know anything about it in Python before this.


== References ==

    Only the class presentations, videos and forum discussions
	https://www.youtube.com/watch?v=2RRSw7Ycv0c - crawler tutorial

== Boolean Retrieval ==

This is the README file for A0213170XX's submission

== Python Version ==

I'm using Python Version <3.7.6> for
this assignment.

== General Notes about this assignment ==
	index.py
	1. open each file in the reuters directory
	2. Use nltk to tokenize each work in the file
	3. Use stemming and case folding
	4. add word to dictionary
	5. Save a postings list to that word key and add when the word is found again in another file
	7. Traverse each word in the dictionary
	8. save each of the postings list for eahc word into postings.txt with pickle
	9. Get the position in the postings.txt file were the object was serialized
	10. Save this position to the dictionary, so the postings list is replace with its reference
	11. Serialize the dictionary into dictionary.txt

	search.py
	1. Retrive dictionary
	2. define operators and precedences
	3. Read each line of the queries.txt file
	4. Apply tokenization, stemming, case folding
	5. Send tokens to be converted to infix form with the shunting_yard function
	6. Evaluate the infix form given by the shunting yard function
		7. Three functions made . and, and not, or, so depending on the operator
			one of this functions is called
		8. Not was made by saving in the dictionary a key with all the docID and then using the AND NOT with it and the simple word
	8. Write the resulting list to the results.txt

	More details in the code level documentation

== Files included with this submission ==
	index.py
	-- Indexes the documents
	
	search.py
	-- Searches for the queries

	postings.txt
	-- Result of postings serialized with pickle
	
	dictionary.txt
	-- Result of serialized dictionary with reference to the postings in postings.txt
	
== Statement of individual work ==

[x] I, A0213170X, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[x] I, A0313170X, did not follow the class rules regarding homework
assignment, because of the following reason:

 -- Do to time issues, other midterms, homeworks and more stuff, I did not manage to finish the skip pointers 
	implementation well at all, but I tried to implement it for the AND
	Just that note, I followed all the other instructions.
	Also be good with me as I worked alone :( thank you!

== References ==

    [1] https://docs.python.org/3/library/pickle.html
    [2] https://www.tutorialspoint.com/python/file_seek.htm
    [3] https://www.geeksforgeeks.org/stack-in-python/
    [4] https://www.youtube.com/watch?v=HJOnJU77EUs&t=471s

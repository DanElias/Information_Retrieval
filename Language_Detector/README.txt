== Language Detector ==

This is the README file for A0213170XX's submission

== Python Version ==

I'm using Python Version <3.7.6> for
this assignment.

== General Notes about this assignment ==

build_test_LM.py

    build_LM(in_file) function

        This function builds language models for each label
        each line in in_file contains a label and a string separated by a space
        Returns a Dictionary that contains the LM's for each Language.

        Basic steps to create the LMs:
        1. Open input.train.txt and read line by line, making all letters lower case
            Lower case is used to consider the words are still the same no matter if they are capitalized
        2. Delete patterns from the line = punctuation, special characters, line breaks, digits
            I consider these not being part of the LM, an exception could be made for punctuation, but not considering it.
        3. Retrieve the language name from the line
        4. Generate 4grams from the rest of the line
            I included <S> and <E> symbols just to experiment
        5. Count each time a ngram appears and add to its count in corresponding dictionary.
             Note: I'm using dictionaries that store a pair [count, probability], just to not loose the count data
             Use one-smoothing, if its the first time we see a ngram in a dictionary, I add it once to it
             Therefore we will have also ngrams that appear in other languages, but just counted once
        7. After storing the count, we will calculate the probability for each entry in each LM dictionary
            I calculate the probability until this step as now we know the vocabulary size.
            Therefore I traverse each LM dictionary, (Indonesian, Malaysian, Tamil) and I calculate the probability for each entry:
                indonesian_LM[key][1] = pair[0]/(vocabulary_size + count_indonesian_LM)
                where indonesian_LM[key][1] reference the second location of the pair, in other words, the probability slot
                so I divide the count of the 4gram entry in the dictionary by 
                the sum of the vocabulary_size and the count of 4grams in each language as given in the input.train.txt
        8. Also in the last step, after I calculate each probability I sum it to a counter to 
            know if the end the sum of probabilities is one.
        9. Finally I save the language models in a single dictionary and return it

    test_LM(in_file, out_file, LM) function

        This function builds test sentences and determines which language they belong to
        Reads the file that contains the lines to be tested.
        Writes to a file that has the name of the language the sentence belongs to and the sentence itself

        Basic steps to test the LMs:
        1. As the build LM I read the file line by line,
            I don't apply any regex to filter out any characters because I suppose this is just the
            raw input a user types in. Also I wanted to experiment.
        2. Generate the 4gram list for each line
        3. For each 4gram generated, check if its in a LM, if not, just don't take it into account
        4. Acces the LM["language"]["4gram"][1] for each Language's LM
            Start summing the logs of the probabilites to know the probability for language for the line 
            All three LM have the same keys (4grams) because of the the one smoothing,
            Therefore in this condition, it doesn't matter which LM we check if the 4gram exists in the dictionary
        5. With a max function, discover which of the three languages summed the max probability
            Negatives resulting of the logs don't affect the max function.
        6. Calculate the variance = numpy.var([probability_indonesian, probability_malaysian, probability_tamil])
            If its zero, then its an alien language "other"
        7. Print to the output file the winning language's name and the original analyzed sentence

    Essay Questions

    1) In the homework assignment, we are using character-based ngrams, 
    i.e., the gram units are characters. Do you expect token-based ngram models to perform better?
            
            As we saw on the tutorial character-based ngrams work better for this case as the combinations of characters
        can be max 26^4, using token-based ngrams would have a probability of (Words in a language)^4 which is way more complex
         I did not try this experiment because I had no time for it. :(

    2) What do you think will happen if we provided more data for each category for you to build the language 
    models? What if we only provided more data for Indonesian?

        Hypothesis: The sentences that give Indonesian and Malaysian probabilites really similar will change
        to have more probability of being Indonesian

        Results: It actually happened the other way around. By adding more examples of indonesian sentences,
        The program predicted more sentences to be Malaysian. That's because I believe the LM becomes more
        accurate and it is easier for it to distinguish between Malaysian and Indonesian.
        Also the word count for Indonesian gets larger and the count is divided by a bigger number,
        therefore the probability is smaller. Results in the input.indonesian.txt
    
    3) What do you think will happen if you strip out punctuations and/or numbers? 
    What about converting upper case characters to lower case?

        Using raw input:
            Salah satu anggota keluarga kerajaan dari negara lain seringkali diminta tinggal di Konstantinopel.
                -864.1778692099259
                -889.8945591021725
                -1038.4598658942825
            Akkuantaikku akust"kaavu tanta koai" (Adeodatus = tytttus) eum peyarir.
                -467.38496726436955
                -468.74707871865553
                -400.11254353505404
            Sementara itu, Alexios berhasil mengalahkan Pecheneg dalam Pertempuran Levounion pada tanggal 28 April 1091.
                -769.7228152597905
                -791.4183842536843
                -920.9507921021317
            Accuracy: 90% (because of the "other" sentences)
        
        Stripping out punctuations and/or numbers:
            Salah satu anggota keluarga kerajaan dari negara lain seringkali diminta tinggal di Konstantinopel.
                -758.3810493808361
                -770.29026899349
                -919.0809794631734

            Akkuantaikku akust"kaavu tanta koai" (Adeodatus = tytttus) eum peyarir.
                -369.22242348803763
                -370.18287418115085
                -313.86289347770554

            Sementara itu, Alexios berhasil mengalahkan Pecheneg dalam Pertempuran Levounion pada tanggal 28 April 1091.
                -529.4119968741463
                -546.247372896311
                -660.5643962095112

            Accuracy: 95% (because of the "other" sentences)

            Conclusions:
                Raw input gives more difference between the final probabilites for each sentence tested with each LM 
                We can conclude more distinct 4grams are created as a result of having more characters and Upper case letters
                    Maximum around 70^4 possibilites instead of 26^4
                Conclusion is punctuation might give the program to distinguish languages better
                Although, this might not be totally true is we still have characters like digits and maybe '()' That don't matter
                Also, not removing punctuation affected detecting alien languages as they include the " ' " character

        4) We use 4-gram models in this homework assignment. What do you think will happen if we varied 
        the ngram size, such as using unigrams, bigrams and trigrams?   

            Let's try!

            With 2grams the accuracy decreases to 75%. Probably because some 2grams like "ti" are repeated across the
            3 languages
            With 3 grams the accuracy decreased to 85%. Better than 2grams!
            With 4 grams the accuracy is 95%! Good!
            With 5 grams the accuracy is still 95%!
            With 6 grams the accuracy is still 95%!
            With 7 grams the accuracy is still 95%!
            With 8 grams the accuracy is 90%! Oh no started decreasing!
            With 9 grams the accuracy is 80%! Oh still decreasing!
            With 10 grams the accuracy is 75%! Ok lets stop here!

            Conclusion is maybe 4 - 7 grams work well as most of the words in those languages are Probably.
            made up of 4 - 7 characters. Having 9 or 10 character words is strange.
            Therefore, we must find an optimal ngram model to choose that gives us the best results!

        Really interesting topic! Really liked it!

== Files included with this submission ==

1) input.train.txt
    Input file used to build the LMs.
    It contains about 900 lines, where each line is a label/string pair separated by a space. 
    The label will either read malaysian, indonesian, or tamil.

2) input.test.txt
    The input file to test the LMs.
    It contains 20 strings, each in a line. 
    Some strings do not belong to any of the three languages the program detects. 

3) input.correct.txt
    Contains the correct labels for the input in input.test.txt, in the same format as input.train.txt 
    (i.e., each label/string pair is separated by a space).

4) build_test_LM.py
    Is the file described in the last section. The program that creates and uses the LMs

5) input.indonesian.txt
    Just as the input.train.txt but with more indonesian samples and less malaysian samples.

6) input.predict.q2.txt
    The results of answering the 2nd Essay Question

== Statement of individual work ==

[x] I, A0213170X, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[x] I, A0313170X, did not follow the class rules regarding homework
assignment, because of the following reason:

-- I suggest that I should be graded as follows:

    This is my first time using Python so I would like to not be penalized if I made any mistakes
    or used something in a bad way in my assignment, as I have no prior experience with this language
    and any other libraries or functions I should have used to make my code simpler.

    Also, eval.py gives my implementation 95% of accuracy, but the only reason is because
    it fails in one case with the "other" language. Tried correcting it but the sentence:
        'Kehidupan Pribadi' which is Indonesian is changed to "other"

    I tried solving this with variance but it doesn't work as the sentence:
        'Oel hu Txew trram na'rngit tarmok, tsole'a syeptutet atsawl frato m srey' 
            which is "other"
    has less variance than: 
        'Kehidupan Pribadi' 
            which is actually 'indonesian'
    So I considered less variance equal to more difficult to decide which language is
            *NOTE: I'm calculating the variance between the difference of each final 
            probability for each LM for each sentence
    In other words trying to solve the "other" issue affected 'Kehidupan Pribadi'
    Also the reason why 'Oel hu Txew trram na'rngit tarmok, tsole'a syeptutet atsawl frato m srey'
    is detected as Tamil is because 'ram  ' actually is a 4gram that appears in the Tamil LM.

    On the other hand:
        qaleghqa'mo' jIQuch
    Is correclty predicted as "other" as none of its 4grams appear in any of the LM so its variance is 0

    Maybe the answer to this problem is easier, but I'm having trouble remembering my 
    Probability and Statistics class as I took it 1.5 yeas ago and we did not learn that much Probability.

    Also I tested 3/4 essay questions, I hope that makes up for the final 5% of accuracy I'm missing :(

    Thank you!

== References ==

    [1]https://stackabuse.com/read-a-file-line-by-line-in-python/ - Learn how to manipulate files in Python
    [2]https://kite.com/python/docs/nltk.ngrams  -  Learnt about nltk ngrams
    [3]https://www.quora.com/How-do-I-remove-punctuation-from-a-Python-string - Learnt about regex in Python
    [4]https://stackoverflow.com/questions/33642522/python-regex-sub-with-multiple-patterns - Learnt about regex in Python

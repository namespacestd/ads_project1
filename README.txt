Martin Li (mcl2159)
Alex Dong (aqd2000)
COMS E6111 Advanced Database Systems
Project 1

===================
| Files Submitted |
===================

main.py, helper.py, Makefile, README.txt, transcript-snow-leopard.txt, transcript-gates.txt, transcript-columbia.txt
nltk (library), yaml (library)

==============
| How to Run |
==============

make

    After running make, the program will ask for a series of three inputs: Bing Account Key, target query, and target precision@10.

    Sample Run:

    $ make
    Enter Bing Account Key: xQsuyV9c3sG/oW9e5FTBmfm/YrTq6uXXmtNV+k5Mmxs
    Insert Target Query: snow leopard
    Insert Target Precision@10: .9
    
===================
| Internal Design |
===================

There are several helper functions included in helper.py for tasks such as formatting query URLs, tokenizing strings, and adding/subtracting vectors.

Most of the program logic is in main.py. First, the program prompts the user for the Bing account key, the initial query, and the target precision@10. The program returns results from Bing and the user marks each one as relevant or non-relevant. The results are stored in word_counts, a dictionary that contains the term counts for the documents and whether the document is relevant or not. NOTE: Several libraries (nltk and yaml) are used to extract the content of the HTML results.

From here, several functions are used to organize the approach:
- word_document_frequency() takes word_counts as input and returns a dictionary (word_frequency) containing terms and the number of documents the terms appear in.
- tf_idf_document_weights() takes word_counts and word_frequency as input and returns a dictionary (document_word_weights) containing terms and their normalized weights using the tf-idf weighting scheme.
- rocchio_algorithm() takes document_word_weights as input (as well as the number of relevant documents and number of total results) and applies the Rocchio Algorithm, returning a vector of potential terms to be added to the query.
- special_term_weights() gives extra weight to terms that appear in titles and summaries (see Approach section).

Finally, the term with the highest weight after all of these functions have been applied is added to the query and reorder_query_list() orders the modified query based on term weight. Results for the new query are shown to the user and the process repeats until the target precision@10 is attained.

============
| Approach |
============

Our query modification approach first uses the tf-idf weighting scheme to determine the weight of each term in each document result from the original query. Each document is then modeled as a document vector consisting of the terms in document and their weights. These weights are normalized so that document lengths do not skew term weights. As the user marks each document as relevant or not, the document vectors are added to either the relevant or non-relevant set.

Next, the Rocchio Algorithm is applied. The set of non-relevant document vectors (divided by the number of non-relevent documents) is subtracted from the set of relevant document vectors (divided by the number of relevant documents). The result is a vector of potential terms to add to the query and their weights. Because terms in the title or summary of a document are generally more indicative of a document's content than terms in the body, our method then artificially increases the weight of terms that occur in the title or summary of the documents. Greater weight is given to terms that occur in a higher number of titles or summaries.

Finally, from the resulting terms, the one with the greatest weight is added to the original query to form the modified query. The terms in the modified query are ordered by their weight in descending order.

============
| Bing Key |
============

xQsuyV9c3sG/oW9e5FTBmfm/YrTq6uXXmtNV+k5Mmxs
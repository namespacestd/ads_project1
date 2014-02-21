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

Besides a couple of helper functions for adding and subtracting document vectors, all of the main program logic is simply at the top level.

============
| Approach |
============

Our query modification approach first uses the tf-idf weighting scheme to determine the weight of each term in each document result from the original query. Each document is then modeled as a document vector consisting of the terms in document and their weights. These weights are normalized so that document lengths do not skew term weights. As the user marks each document as relevant or not, the document vectors are added to either the relevant or nonrelevant set.

Next, the Rocchio Algorithm is applied. The set of nonrelevant document vectors (divided by the number of nonrelevent documents) is subtracted from the set of relevant document vectors (divided by the number of relevant documents). The result is a vector of potential terms to add to the query and their weights. Because terms in the title or summary of a document are generally more indicative of a document's content than terms in the body, our method then artificially increases the weight of terms that occur in the title or summary of the documents. Greater weight is given to terms that occur in a higher number of titles or summaries.

Finally, from the resulting terms, the one with the greatest weight is added to the original query to form the modified query. The terms in the modified query are ordered by their weight in descending order.

============
| Bing Key |
============

xQsuyV9c3sG/oW9e5FTBmfm/YrTq6uXXmtNV+k5Mmxs
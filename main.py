
import urllib2
import base64
import xml.etree.ElementTree as ET
import nltk
import string
import math
from collections import Counter
import operator

def add_document_vectors(documentDictionary1, documentDictionary2):
    word_weights = documentDictionary1

    for word in documentDictionary2.keys():
        try:
            word_weights[word] += documentDictionary2[word]
        except:
            word_weights[word] = documentDictionary2[word]
    return word_weights

def subtract_document_vectors(documentDictionary1, documentDictionary2):
    word_weights = documentDictionary1

    for word in documentDictionary2.keys():
        try:
            word_weights[word] -= documentDictionary2[word]
        except:
            word_weights[word] = -1 * documentDictionary2[word]
    return word_weights

user_query = raw_input("Insert Query: ")
resulting_precision = 0.0
target_precision = raw_input("Insert Target Precision: ")

querylist = nltk.word_tokenize(user_query)

while resulting_precision < float(target_precision):
    resulting_precision = 0.0
    bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27'
    for query in querylist:
        bingUrl += (query + '%20')
    bingUrl += '%27&$top=10&$format=Atom'
    #Provide your account key here
    accountKey = 'xQsuyV9c3sG/oW9e5FTBmfm/YrTq6uXXmtNV+k5Mmxs'
    atom_prefix = '{http://www.w3.org/2005/Atom}'
    microsoft_prefix = '{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}'
    inner_prefix = '{http://schemas.microsoft.com/ado/2007/08/dataservices}'

    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()
    #content contains the xml/json response from Bing.

    root = ET.fromstring(content)  

    url = root[5].attrib['href']
    total_results = 0
    num_relevant = 0.0

    print "Parameters:"
    print "Client Key: " + accountKey
    print "Query: " + str(querylist)
    print "Precision: " + target_precision
    print "URL: " + bingUrl
    print "Total Results: 10"
    print "Bing Search Results:"
    print "========================"

    word_counts = []
    title_tokens = []
    summary_tokens = []
    not_html_response = 0

    for node in root.findall(atom_prefix+'entry'):
        total_results+=1
        print "Result " + str(total_results)
        print "["
        entry_node = node.find(atom_prefix+'content').find(microsoft_prefix+'properties')
        URL = entry_node.find(inner_prefix+'Url').text
        print " URL: " + URL

        title = entry_node.find(inner_prefix+'Title').text
        print " Title: " + title
        summary = entry_node.find(inner_prefix+'Description').text
        print " Summary: " + summary
        print "]\n"

        tokens = []
        
        try:
            req = urllib2.Request(URL, headers = headers)
            response = urllib2.urlopen(req)
            content = response.read()
            raw = nltk.clean_html(content)
            tokens = map(lambda x: x.lower().translate(string.maketrans("",""), string.punctuation), nltk.word_tokenize(raw))
            tokens = filter(lambda s: not str(s).lstrip('-').isdigit(), tokens)

            counts = Counter(tokens)

            relevancy = False

            relevancy = raw_input("Relevant (Y/N)?")
            if relevancy.lower() == "y":               
                title_punc_removed = map(lambda x: x.lower().translate(string.maketrans("",""), string.punctuation), nltk.word_tokenize(title))
                title_token = filter(lambda s: not str(s).lstrip('-').isdigit(), title_punc_removed)
                title_tokens = title_tokens + title_token

                summary_punc_removed = map(lambda x: x.lower().translate(string.maketrans("",""), string.punctuation), nltk.word_tokenize(summary))
                summary_token = filter(lambda s: not str(s).lstrip('-').isdigit(), summary_punc_removed)
                summary_tokens = summary_tokens + summary_token

                num_relevant+=1
                relevancy = True

            word_counts.append({"document" : counts, "relevancy" : relevancy });
        except:
            print "Removing non-HTML response"
            not_html_response+=1    

    if num_relevant == 0:
        print "Program Terminating. No relevant results found in top 10."
        break
    if total_results != 10:
        print "Program Terminating. Less than 10 results returned by Bing."
        break

    total_results-=not_html_response
    resulting_precision = num_relevant / total_results
    print "Precision: " + str(resulting_precision)

    if resulting_precision >= float(target_precision):
        print "Final Query: " + str(querylist)
        break

    word_document_frequency = {}

#number of documents that a word appears in
    for documents in word_counts:
        for word in documents['document'].keys():
            if word not in word_document_frequency.keys():
                document_frequency = 0

                for documents in word_counts:
                    if word in documents['document'].keys():
                        document_frequency+=1

                word_document_frequency[word] = document_frequency

    document_word_weights = []

#Weights of words (and normalization)
    for documents in word_counts:
        word_weights = {}
        normalized_weights = {}
        
        sum_of_squares = 0

        for word in documents['document'].keys():
            weight = documents['document'][word] * math.log(total_results / word_document_frequency[word])
            word_weights[word] = weight
            sum_of_squares += math.pow(weight,2)

        for word in word_weights.keys():
            normalized_weight = word_weights[word] / math.sqrt(sum_of_squares)
            normalized_weights[word] = normalized_weight

        document_word_weights.append({'relevancy' : documents['relevancy'], 'weights' : word_weights, 'normalized_weights' : normalized_weights, 'sum_of_squares' : math.sqrt(sum_of_squares)})

    relevant_vectors = {}
    nonrelevant_vectors = {}

#Rocchio Algorithm and add the highest weighted word to query
    for document in document_word_weights:
        if document['relevancy'] == True:
            relevant_vectors = add_document_vectors(relevant_vectors, document['normalized_weights'])
        else:
            nonrelevant_vectors = add_document_vectors(nonrelevant_vectors, document['normalized_weights'])

    for word in relevant_vectors.keys():
        relevant_vectors[word] = relevant_vectors[word] / num_relevant
    for word in nonrelevant_vectors.keys():
        nonrelevant_vectors[word] = nonrelevant_vectors[word] / (total_results - num_relevant)

    final_vector_values = subtract_document_vectors(relevant_vectors, nonrelevant_vectors)
    try:
        title_tokens = filter(lambda a: a != '', title_tokens)
    except:
        pass

    title_counts = Counter(title_tokens)
    for title in title_counts.keys():
        try:
            #final_vector_values[title] *= ((title_counts[title] / num_relevant) * 5)
            final_vector_values[title] *= (title_counts[title] + 1)
        except:
            pass

    summary_counts = Counter(summary_tokens)
    for summary in summary_counts.keys():
        try:
            #final_vector_values[summary] *= ((summary_counts[summary] / num_relevant) * 5)
            final_vector_values[summary] *= (summary_counts[summary] + 1)
        except:
            pass

    max_key = max(final_vector_values.iterkeys(), key=(lambda key: final_vector_values[key]))
    print "Adding \"" + max_key + "\" to query."

    '''
    for word in final_vector_values.keys():
        if final_vector_values[word] > 0:
            print word + " " + str(final_vector_values[word])'''

    querylist.append(max_key)

    reordered_query_list = []
    weighted_query_list = {}

    for query in querylist:
        try:
            weighted_query_list[query] = final_vector_values[query]
        except:
            weighted_query_list[query] = 0

    query_key_values = sorted(weighted_query_list.iteritems(), key=operator.itemgetter(1), reverse=True)
    
    for query in query_key_values:
        reordered_query_list.append(query[0])

    querylist = reordered_query_list


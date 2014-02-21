
import urllib2, base64, nltk, string, math, operator
import xml.etree.ElementTree as ET
from collections import Counter
from helper import *

def word_document_frequency(documents):
    word_document_frequency = {}

    for document in documents:
        for word in document['document'].keys():
            if word not in word_document_frequency.keys():
                document_frequency = 0

                for document in documents:
                    if word in document['document'].keys():
                        document_frequency+=1

                word_document_frequency[word] = document_frequency
    return word_document_frequency

def if_idf_document_weights(word_counts, word_frequency):
    document_word_weights = []

    for documents in word_counts:
        word_weights = {}
        normalized_weights = {}
            
        sum_of_squares = 0

        for word in documents['document'].keys():
            weight = documents['document'][word] * math.log(total_results / word_frequency[word])
            word_weights[word] = weight
            sum_of_squares += math.pow(weight,2)

        for word in word_weights.keys():
            normalized_weight = word_weights[word] / math.sqrt(sum_of_squares)
            normalized_weights[word] = normalized_weight

        document_word_weights.append({'relevancy' : documents['relevancy'], 'weights' : word_weights, 'normalized_weights' : normalized_weights, 'sum_of_squares' : math.sqrt(sum_of_squares)})
    return document_word_weights

def rocchio_algorithm(document_word_weights, num_relevant, total_results):
    relevant_vectors = {}
    nonrelevant_vectors = {}

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
    return final_vector_values

def special_term_weights(final_vector_values, special_terms):
    counts = Counter(special_terms)
    for title in counts.keys():
        try:
            final_vector_values[title] *= (counts[title] + 1)
        except:
            pass
    return final_vector_values

def reorder_query_list(querylist, final_vector_values):
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

    return reordered_query_list

atom_prefix = '{http://www.w3.org/2005/Atom}'
microsoft_prefix = '{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}'
inner_prefix = '{http://schemas.microsoft.com/ado/2007/08/dataservices}'
accountKey = 'xQsuyV9c3sG/oW9e5FTBmfm/YrTq6uXXmtNV+k5Mmxs'
  
accountKey = raw_input("Enter Bing Account Key: ")
user_query = raw_input("Insert Target Query: ")
resulting_precision = 0.0
target_precision = raw_input("Insert Target Precision@10: ")

querylist = nltk.word_tokenize(user_query)

while resulting_precision < float(target_precision):
    resulting_precision = 0.0
    
    bingUrl = bing_URL_from_querylist(querylist)    
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()

    root = ET.fromstring(content)  

    url = root[5].attrib['href']
    total_results = 0
    num_relevant = 0.0
    bing_results = root.findall(atom_prefix+'entry')

    print "\nParameters:"
    print "Client Key: " + accountKey
    print "Query: " + str(querylist)
    print "Precision: " + target_precision
    print "URL: " + bingUrl
    print "Total Results: " + str(len(bing_results))
    print "Bing Search Results:"
    print "======================"

    if len(bing_results) != 10:
        print "Program Terminating. Less than 10 results returned by Bing."
        break

    word_counts = []
    title_tokens = []
    summary_tokens = []
    not_html_response = 0    

    for node in bing_results:
        total_results+=1
        print "Result " + str(total_results) + "\n["
        entry_node = node.find(atom_prefix+'content').find(microsoft_prefix+'properties')
        URL = entry_node.find(inner_prefix+'Url').text
        print " URL: " + URL

        title = entry_node.find(inner_prefix+'Title').text
        print " Title: " + title
        summary = entry_node.find(inner_prefix+'Description').text
        print " Summary: " + summary + "\n]\n"

        tokens = []
        
        try:
            relevancy = False

            relevancy = raw_input("Relevant (Y/N)? ")
            if relevancy.lower() == "y":
                num_relevant+=1
                title_tokens = title_tokens + tokenize_and_clean(title)
                summary_tokens = summary_tokens + tokenize_and_clean(summary)                
                relevancy = True

            req = urllib2.Request(URL, headers = headers)
            response = urllib2.urlopen(req)
            content = response.read()
            raw = nltk.clean_html(content)
            tokens = tokenize_and_clean(raw)
            counts = Counter(tokens)

            word_counts.append({"document" : counts, "relevancy" : relevancy });
        except:
            not_html_response+=1    

    if num_relevant == 0:
        print "Program Terminating. No relevant results found in top 10."
        break

    resulting_precision = num_relevant / total_results
    total_results-=not_html_response
    print "======================"
    print "FEEDBACK SUMMARY"
    print "Query: " + str(querylist)
    print "Precision: " + str(resulting_precision)

    if resulting_precision >= float(target_precision):
        print "Desired precision reached. Program ending."
        break
    else:
        print "Still below the desired precision of " + target_precision

    word_frequency = word_document_frequency(word_counts)
    document_word_weights = if_idf_document_weights(word_counts, word_frequency)
    final_vector_values = rocchio_algorithm(document_word_weights, num_relevant, total_results)

    final_vector_values = special_term_weights(final_vector_values, title_tokens)
    final_vector_values = special_term_weights(final_vector_values, summary_tokens)

    max_key = max(final_vector_values.iterkeys(), key=(lambda key: final_vector_values[key]))
    print "Augmenting current querylist with \"" + max_key + "\""

    querylist.append(max_key)
    querylist = reorder_query_list(querylist, final_vector_values)


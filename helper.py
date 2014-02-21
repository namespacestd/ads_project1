import string
import nltk

def bing_URL_from_querylist(querylist):
    bingURL = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27'
    for index in range(len(querylist)):
        if index != len(querylist)-1:
            bingURL += (querylist[index] + '%20')
        else:
            bingURL += querylist[index]
    bingURL += '%27&$top=10&$format=Atom'
    return bingURL

def tokenize_and_clean(raw):
    try:
        tokens = map(lambda x: x.lower().translate(string.maketrans("",""), string.punctuation), nltk.word_tokenize(raw))
        tokens = filter(lambda s: not str(s).lstrip('-').isdigit(), tokens)

        try:
            tokens = filter(lambda a: a != '', tokens)
        except:
            pass

        return tokens
    except:
        pass

    return raw
    

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

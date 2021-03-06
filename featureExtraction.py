# -*- coding: utf-8 -*-
"""
Method to build and dump the dataset. Hacky for now, should later be
automated.

@author: Nathanael Romano and Daniel Levy
"""

import numpy as np

import textUtil as txt

### GENERIC FEATURE EXTRACTOR ###
  
def create_feature_vector(entity, text, method='skip_1', model=None):
    '''Creates feature vector using specified method.
    
    Model holds a word2vec model.
    '''
    vector = {}
    if model is not None:
        sentences = [s for s in text.split('.') if entity in s]
        return word2vec_features(entity, sentences, model)
    words = text.split()
    for i, word in enumerate(words):
        # only update for the corresponding entity
        if word != entity:
            continue
        vector.update(extractor(method)(words, i))
    return vector
    

def extractor(method):
    '''Returns feature extractor function.'''
    try:
        return globals()[method]
    except KeyError:
        msg = 'Extractor {} not implemented'
        raise NotImplementedError(msg.format(method))

### FEATURE EXTRACTORS

def skip_1(words, index):
    '''Simple 1-length skip_gram method.
    
    w1 w w2 will add 'before_w1' and 'after_w2' to feature vector.
    '''
    dict_ = {}
    if not words:
        return dict_
    # adding -1, + 1 words
    if index - 1 >= 0:
        w_minus_1 = txt.removeToken(words[index - 1])
        dict_['before_' + str(w_minus_1)] = 1
    if index + 1 < len(words):
        w_plus_1 = txt.removeToken(words[index + 1])
        dict_['after_' + str(w_plus_1)] = 1
    return dict_


def skip_2(words, index):
    '''Simple 2-length skip_gram method.
    
    w1 w2 w w3 w4 will add 'before_w1', 'before_w2', 'after_w3' and 'after_w4'
    to feature vector.
    '''
    dict_ = {}
    if not words:
        return dict_
    # adding -1, + 1 words
    dict_.update(skip_1(words, index))
    # adding -2, + 2 words
    if index - 2 >= 0:
        w_minus_2 = txt.removeToken(words[index - 2])
        dict_['before_' + str(w_minus_2)] = 1
    if index + 2 < len(words):
        w_plus_2 = txt.removeToken(words[index + 2])
        dict_['after_' + str(w_plus_2)] = 1
    return dict_
    
    
def word2vec_features(entity, sentences, model):
    '''Uses a word2vec trained on 1200 sports article.
    
    Computes the average vector for the words in the entity's sentence.'''
    arrays = []
    for sentence in sentences:
        count = 0
        array = np.zeros(model.vector_size)
        for w in sentence:
            if w in model and w != 'ent':
                count += 1
                array += model[w]
        arrays.append(array / float(count))
    if arrays:
        return sum(arrays) / len(arrays)
    else:
        return np.zeros(model.vector_size)


def gram_skip_2(words, index, n=4):
    '''ngram on skip_2_gram, continuous.
    
    w1 w2 w w3 w4 will add a 3gram of w1 w2 w3 w4.
    '''
    dict_ = {}
    if not words:
        return dict_
    skipped = []
    if index - 2 >= 0:
        skipped.append(txt.removeToken(words[index - 2]))
    if index - 1 >= 0:
        skipped.append(txt.removeToken(words[index - 1]))
    if index + 1 < len(words):
        skipped.append(txt.removeToken(words[index + 1]))
    if index + 2 < len(words):
        skipped.append(txt.removeToken(words[index + 2]))
    skipped = ''.join(skipped)
    for i in range(len(skipped)-n):
        dict_[skipped[i:i + n]] = 1
    return dict_

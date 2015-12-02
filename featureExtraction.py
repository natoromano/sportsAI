# -*- coding: utf-8 -*-
"""
Method to build and dump the dataset. Hacky for now, should later be
automated.

@author: Nathanael Romano and Daniel Levy
"""

import textUtil as txt
    
def extractor(method):
    '''Returns feature extractor function.'''
    try:
        return globals()[method]
    except KeyError:
        msg = 'Extractor {} not implemented'
        raise NotImplementedError(msg.format(method))


def skip_1(words, index):
    '''Simple 1-length skip_gram method.
    
    w1 w w2 will add 'before_w1' and 'after_w2' to feature vector.
    '''
    dict_ = {}
    w_minus_1 = txt.removeToken(words[index - 1])
    w_plus_1 = txt.removeToken(words[index + 1])
    dict_['before_' + str(w_minus_1)] = 1
    dict_['after_' + str(w_plus_1)] = 1
    return dict_


def skip_2(words, index):
    '''Simple 2-length skip_gram method.
    
    w1 w2 w w3 w4 will add 'before_w1', 'before_w2', 'after_w3' and 'after_w4'
    to feature vector.
    '''
    dict_ = {}
    w_minus_1 = txt.removeToken(words[index - 1])
    w_plus_1 = txt.removeToken(words[index + 1])
    dict_['before_' + str(w_minus_1)] = 1
    dict_['after_' + str(w_plus_1)] = 1
    if index - 2 >= 0:
        w_minus_2 = txt.removeToken(words[index - 2])
        dict_['before_' + str(w_minus_2)] = 1
    if index + 2 < len(words):
        w_plus_2 = txt.removeToken(words[index + 2])
        dict_['after_' + str(w_plus_2)] = 1
    return dict_

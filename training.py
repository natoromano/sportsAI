# -*- coding: utf-8 -*-
"""
Methods to train the model, using various algorithms.

@author: Nathanael Romano and Daniel Levy
"""

import sys
sys.path.append('liblinear/python')

import liblinearutil as llb

import dataset as dts

### LOADING ###

def load_dataset(name):
    '''Loads the given dataset.
    
    Name is the data set name, e.g. who_won_1031.
    '''
    path = 'features/' + name + '.features'
    return dts.Dataset.load(path)

### TRAINNG METHODS ###

def logistic_regression(name):
    '''Trains a logistic regression model on the feature extracted data.
    
    Name is the data set name, e.g. who_won_1031.
    '''
    data = load_dataset(name)
    return llb.train(data.Y, data.X, '-s 0')
    
    
def svm(name):
    '''Trains a logistic regression model on the feature extracted data.
    
    Name is the data set name, e.g. who_won_1031.
    '''
    data = load_dataset(name)
    return llb.train(data.Y, data.X, '-s 1')

# ACTUAL TRAINING

def get_training_method(method):
    '''Gets the training method (method input is a string).'''
    try:
        return globals()[method]
    except:
        msg = 'No training method for {}'
        raise NotImplementedError(msg.format(method))


def train_and_save(name, method):
    '''Runs training.
    
    Must use the liblinear library.
    '''
    print 'Training dataset {} with method {}.'.format(name, method)
    model = get_training_method(method)(name)
    try:
        llb.save_model('models/{}.model'.format(name), model)
        print 'Saved model.'
    except:
        print 'Could not save model.'
    
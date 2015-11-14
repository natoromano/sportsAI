# -*- coding: utf-8 -*-
"""
Script to train the model, using various algorithms.

@author: Nathanael Romano and Daniel Levy
"""

import pickle
from sklearn import linear_model, svm

import dataset

def loadDataset(name):
    '''Loads the given dataset.
    
    Name is the data set name, e.g. who_won_1031.
    '''
    path = name + '.csv'
    return dataset.Dataset.fromCSV(path)

def trainLogisticRegression(name):
    '''Trains a logistic regression model on the feature extracted data.
    
    Name is the data set name, e.g. who_won_1031.
    '''
    data = loadDataset(name)
    model = linear_model.LogisticRegression()
    X = data.getX(excludedColumns = ['label','word'])
    y = data.getY(labelColumn = 'label')
    model.fit(X,y)
    return model

def run(name):
    '''Runs training.'''
    model = trainLogisticRegression(name)
    f = open('{}.model'.format(name), 'w')
    pickle.dump(model, f)
    f.close()

run('who_won_1031')

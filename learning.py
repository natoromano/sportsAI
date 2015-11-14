# -*- coding: utf-8 -*-
"""
Classes and methods to learn from the dataset.

@author: Nathanael Romano and Daniel Levy

!!!!!!!!!!! OBSOLETE !!!!!!!!!!!!
"""

import time

import numpy as np
import pandas as pd
from sklearn import svm, linear_model

import game

start_time = time.time()

df = pd.DataFrame.from_csv('dataset_who_won_urls_1108.csv')

def Training():

    def __init__(self):
        return 

    def loadDataset(self, csv):
        start_time = time.time()
        self.df = pd.DataFrame.from_csv(csv)
        self.loadingTime = time.time() - start_time()

    def setModel(self, model):
        self.model = model

    def train(self):
        start_time = time.time()
        
        trainingColumns = np.delete(columns, 0)
        X = self.df[trainingColumns]
        y = df['label']

        self.model.fit(X,y)

        self.trainingTime = time.time() - start_time()

    def addExamplesFromDict(self, d):
        self.df.append(d)
        self.fillna(0)

print 'Loading took' , time.time() - start_time

start_time = time.time()

columns = df.columns.values

trainingColumns = np.delete(columns, 0)
X = df[trainingColumns]
y = df['label']

model = svm.SVC(probability=True)
model.fit(X, y)

print 'Training took', time.time() - start_time

testUrl = 'http://www.espnfc.us/uefa-champions-league/match/434210/as-roma-bayer-leverkusen/report'

testGame = game.Game(testUrl)

scores = []
text = testGame.text

tests = []
testWords = []
for s in text:
    s = '#BEGIN# '+s+' #END#'
    words = s.split(' ')
    for i in range(1,len(words)-1):
        d = {}
        w_minus_1 = words[i-1]
        w_plus_1 = words[i+1]

        d['word_before_=_'+str(w_minus_1)] = 1
        d['word_after_=_'+str(w_plus_1)] = 1

        tests.append(d)
        testWords.append(words[i])

df = df.append(tests)
df.fillna(0, inplace=True)

n = len(testWords)

Xtest = df[-n:]

for i, _ in enumerate(testWords):
    x = Xtest[trainingColumns][i:i+1]
    score = model.predict_log_proba(x)[0][1]
    scores.append((score, testWords[i]))

scores.sort()

print scores[-5:]

import numpy as np
import pandas as pd
import time
import game

from sklearn import svm, linear_model

start_time = time.time()

df = pd.DataFrame.from_csv('dataset_who_won_urls_1108.csv')

print 'Loading took' , time.time() - start_time

start_time = time.time()

columns = df.columns.values

trainingColumns = np.delete(columns, 0)

X = df[trainingColumns]
y = df['label']

model = svm.SVC()
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
    score = model.decision_function[0]
    scores.append((score[0], testWords[i]))

scores.sort()

print scores[:5]


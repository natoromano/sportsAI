dataset_path = 'who_won_30.csv'

import dataset

from sklearn import linear_model, svm

d = dataset.Dataset()
d.fromCSV(dataset_path)

model = linear_model.LogisticRegression()

X = d.getX(excludedColumns = ['label','word'])
y = d.getY(labelColumn = 'label')

model.fit(X,y)

import pickle

f = open('who_won_30.model','w')

pickle.dump(model, f)

f.close()


# -*- coding: utf-8 -*-
"""
Classes and methods to handle datasets.

@author: Nathanael Romano and Daniel Levy
"""

import os
import pickle

import game
import textUtil as txt
import featureExtraction as ext

### DATASET CLASS ###

class Dataset(object):
    '''Base class for a dataset.
    
    self.X and self.Y are two lists of respecively the examples and their
    labels, but self exhibits a mapping x:y.
    '''
    
    def __init__(self, name):
        self.name = name
        self.X = []
        self.Y = []
        self.entities = []
        self._features = {}
        self._max_feature_key = 0

    @classmethod
    def load(cls, path):
        '''Loads the dataset from the given path.'''
        f = open(path, 'rb')
        try:
            return pickle.load(f)
        except:
            return None
        
    def append(self, example, entity):
        '''Adds an example to the dataset.'''
        x_string, y = example
        x = {}
        for k, v in x_string.iteritems():
            if k in self._features:
                x[self._features[k]] = v
            else:
                self._add_feature(k)
                x[self._max_feature_key] = v
        self.X.append(x)
        self.Y.append(y)
        self.entities.append(entity)
        
    def dump(self, path):
        '''Dumps the dataset to the given path.'''
        f = open(path, 'wb')
        pickle.dump(self, f)
        f.close()
        
    def _add_feature(self, feature):
        '''Adds a feature to self's dictionnary.'''
        self._max_feature_key += 1
        self._features[feature] = self._max_feature_key


### BUILDING DATASET ###

def build_dataset(urls, name, query, method='skip_1', entities=None):
    '''Builds the data set for a list of game URLs and a given query.'''
    entities = entities or {}
    # create Dataset object
    print 'Starting to build dataset {}.'.format(name)
    dataset = Dataset(name)
    for url in urls:
        # create game objects
        try:
            g = game.Game(url)
        except:
            continue
        # get and anonimyze text
        text = g.text
        for i in range(len(text)):
            text[i], entities = txt.anonymize(text[i], entities)
        inv_entities = {v: k for k, v in entities.items()}
        # fetch answer
        answer = g.query_dict[query]
        for s in text:
            s = '#BEGIN# ' + s + ' #END#'
            words = s.split(' ')
            # iterate over entities
            for i in range(1, len(words)-1):
                if not txt.isToken(words[i]):
                    continue     
                feature_vector = ext.extractor(method)(words, i)
                entityNumber = int(words[i][3:])
                label = (inv_entities[entityNumber] in answer.split(' ')) * 1.0
                # add feature vect and label to dataset
                dataset.append((feature_vector, label), words[i])
    return dataset, entities
    

def build_dataset_from_path(path, name, query, method='skip_1', entities=None):
    '''Builds the data set for a path to pickle dump and a given query.
    
    Should be merged with previous function.
    '''
    entities = entities or {}
    # create Dataset object
    print 'Starting to build dataset {}.'.format(name)
    dataset = Dataset(name)
    f = open(path, 'rb')
    while True:
        # create game objects
        try:
            g = pickle.load(f)
        except:
            break
        # get and anonimyze text
        text = g.text
        for i in range(len(text)):
            text[i], entities = txt.anonymize(text[i], entities)
        inv_entities = {v: k for k, v in entities.items()}
        # fetch answer
        answer = g.query_dict[query]
        for s in text:
            s = '#BEGIN# ' + s + ' #END#'
            words = s.split(' ')
            # iterate over entities
            for i in range(1, len(words)-1):
                if not txt.isToken(words[i]):
                    continue     
                feature_vector = ext.extractor(method)(words, i)
                entityNumber = int(words[i][3:])
                label = (inv_entities[entityNumber] in answer.split(' ')) * 1.0
                # add feature vect and label to dataset
                dataset.append((feature_vector, label), words[i])
    f.close()
    return dataset, entities


def build_and_dump(query, urls=None, path=None):
    '''Dumps the data set and entities to files.
    
    The games should be taken from a list of urls by givin the argument urls,
    or by a path by giving a path to a pickle dump of games.
    '''
    def make_name(name, type_='features'):
        return 'data/{}.{}'.format(name, type_)
    if urls:
        name = txt.queryName(query) + '_' + str(len(urls))
    else:
        name = path.split('/')[-1].split('.')[0]
    if urls:
        dataset, entities = build_dataset(urls, name, query)
    if path:
        dataset, entities = build_dataset_from_path(path, name, query)
    if os.path.isfile(make_name(name)):
        os.remove(make_name(name))
    dataset.dump(make_name(name))
    if os.path.isfile(make_name(name, 'entities')):
        os.remove(make_name(name, 'entities'))   
    f = open(make_name(name, 'entities'), 'wb')
    pickle.dump(entities, f)
    f.close()
    print 'Sucessfully dumped dataset.'

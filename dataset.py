# -*- coding: utf-8 -*-
"""
Classes and methods to handle datasets.

@author: Nathanael Romano and Daniel Levy
"""

import os
import pickle

from gensim.models import word2vec

import game as gme
import textUtil as txt
import featureExtraction as ext

PATH = 'features/'
WORD2VEC_PATH = 'word2vec/vectors3.bin'

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
            
    @classmethod
    def from_columns(cls, name):
        '''As with the pandas framework, create a Dataset object using the
        _features dictionnary.'''
        path = 'features/{}.columns'.format(name)
        f = open(path, 'rb')
        dataset = cls(name)
        dataset._features = pickle.load(f)
        if dataset._features:
            dataset._max_feature_key = max(dataset._features.values())
        else:
            dataset._max_feature_key = 0
        return dataset
        
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
    '''Builds the data set for a list of game URLs and a given query.
    
    Only for testing.
    The try/except clauses are here because sometimes the scraping does not
    work, because of the EPSN website. In this case, the error is often a list
    index out of range, as most of the scraping methods will break when they
    reach specific areas of the HTML source code.
    '''
    if method=='word2vec':
        model = word2vec.Word2Vec.load_word2vec_format(WORD2VEC_PATH,
                                                      binary=True)
    entities = entities or {}
    # create Dataset object
    print 'Starting to build dataset {}.'.format(name)
    dataset = Dataset(name)
    for url in urls:
        # create game objects
        try:
            g = gme.Game(url)
        except:
            continue
        try:
            answer = g.query_dict[query]
        except KeyError:
            continue # question not in dataset (e.g. who scored the 1st goal)
        # get and anonimyze text
        text = ' '.join(g.text)
        text, entities = txt.anonymize(text)
        #for i in range(len(text)):
            #text[i], entities = txt.anonymize(text[i], entities)
        inv_entities = {v: k for k, v in entities.items()}
        # fetch answer
        # create feature vector for each entity in text
        for ent_id in inv_entities.iterkeys():
            ent_name = 'ent' + str(ent_id)
            if method!='word2vec':
                feature_vector = ext.create_feature_vector(ent_name, 
                                                           text, method)
                try:
                    label = (ent_id == inv_entities[answer]) * 1.0
                except KeyError:
                    label = (inv_entities[ent_id] in answer) * 1.0               
                # add feature vector to dataset
                dataset.append((feature_vector, label), ent_name)
            else:
                feature_vector = ext.create_feature_vector(ent_name, text,
                                                           method, model=model)
                try:
                    label = (ent_id == inv_entities[answer]) * 1.0
                except KeyError:
                    label = (inv_entities[ent_id] in answer) * 1.0 
                dataset.append((dict(zip(range(len(feature_vector)), 
                                         feature_vector)), label), ent_name)
    return dataset, entities


def build_dataset_from_path(path, name, query, method='skip_1', entities=None):
    '''Builds the data set for a path to pickle dump and a given query.
    
    Loops over the text entities.
    '''
    if method=='word2vec':
        model = word2vec.Word2Vec.load_word2vec_format(WORD2VEC_PATH, 
                                                      binary=True)
    entities = entities or {}
    # create Dataset object
    print 'Starting to build dataset {}.'.format(name)
    dataset = Dataset(name)
    f = open(path, 'rb')
    while True:
        # create game objects
        try:
            g = pickle.load(f)
            print 'Loaded game in training set.'
        except:
            break
        try:
            answer = g.query_dict[query]
        except KeyError:
            continue # question not in dataset (e.g. who scored the 1st goal)
        # get and anonimyze text
        text = ' '.join([t.decode() for t in g.text])
        text, entities = txt.anonymize(text)
        #for i in range(len(text)):
            #text[i], entities = txt.anonymize(text[i], entities)
        inv_entities = {v: k for k, v in entities.items()}
        # fetch answer
        answer = g.query_dict[query]
        # create feature vector for each entity in text
        for ent_id in inv_entities.iterkeys():
            ent_name = 'ent' + str(ent_id)
            if method!='word2vec':
                feature_vector = ext.create_feature_vector(ent_name, 
                                                           text, method)
                try:
                    label = (ent_id == inv_entities[answer]) * 1.0
                except KeyError:
                    label = (inv_entities[ent_id] in answer) * 1.0                
                # add feature vector to dataset
                dataset.append((feature_vector, label), ent_name)
            else:
                feature_vector = ext.create_feature_vector(ent_name, text,
                                                           method, model=model)
                try:
                    label = (ent_id == inv_entities[answer]) * 1.0
                except KeyError:
                    label = (inv_entities[ent_id] in answer) * 1.0 
                dataset.append((dict(zip(range(len(feature_vector)), 
                                         feature_vector)), label), ent_name)
    f.close()
    return dataset, entities


def build_and_dump(name, query, method='skip_1', urls=None, path=None):
    '''Dumps the data set and entities to files.
    
    The games should be taken from a list of urls by givin the argument urls,
    or by a path by giving a path to a pickle dump of games.
    '''
    def make_name(name, type_='features'):
        return 'features/{}.{}'.format(name, type_)
    if urls:
        dataset, entities = build_dataset(urls, name, query, method)
    if path:
        dataset, entities = build_dataset_from_path(path, name, query, method)
    if os.path.isfile(make_name(name)):
        os.remove(make_name(name))
    dataset.dump(make_name(name))
    if os.path.isfile(make_name(name, 'entities')):
        os.remove(make_name(name, 'entities'))   
    f = open(make_name(name, 'entities'), 'wb')
    pickle.dump(entities, f)
    f.close()
    f = open(make_name(name, 'columns'), 'wb')
    pickle.dump(dataset._features, f)
    f.close()
    print 'Sucessfully dumped dataset.'

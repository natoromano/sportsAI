# -*- coding: utf-8 -*-
"""
Various short methods and scripts.

@author: Nathanael Romano and Daniel Levy
"""

import datetime
import time
import pickle

import scraping as scr
import dataset as dts
import training as trn
import test as tst


def simple_test(name, query, method='skip_1'):
    '''Builds, train, and interactively test a simple model with few games, 
    for debugging.'''
    urls = scr.getURLs('20151128')
    dts.build_and_dump(name, query, method=method, urls=urls)
    # dumps model
    trn.train_and_save(name, 'logistic_regression')
    tst.irun(name, query, 3)
    

def with_games(name, query, path, method='skip_1'):
    '''Trains a model games that have already been scraped.'''
    begin = time.time()
    dts.build_and_dump(name, query, method=method, path=path)
    #dumps model
    trn.train_and_save(name, 'logistic_regression')
    tst.irun(name, query, 3)
    print 'Time:', time.time()-begin   
    
    
def full_test(name, query, train_set, test_set, method):
    '''Performs a full automated test.
    
    @param name: test and model name, arbitrary
    @param query: question to train on
    @param train_set: name of the training set of games
    @param test_set: name of testing set of games
    @param method: feature extraction method
    '''
    path = 'games/{}'.format(train_set)
    begin = time.time()
    dts.build_and_dump(name, query, method=method, path=path)
    trn.train_and_save(name, 'logistic_regression')
    print time.time()-begin
    return tst.test(name, test_set, query, method)


def scrape_games(name, start_date, train=30, dev=20, test=0):
    '''Automatically a training, dev and test set.'''
    count = 0
    while count < train:
        end_date = start_date + datetime.timedelta(days=2)
        new_count = scr.automated_scraping(start_date, end_date, 
                                           name='train_{}'.format(name))
        count += new_count
        if new_count == 0:
            time.sleep(15)
        start_date = end_date
    print 'Created training set with %s games.' % str(count)
    count = 0
    while count < dev:
        end_date = start_date + datetime.timedelta(days=2)
        new_count = scr.automated_scraping(start_date, end_date, 
                                           name='dev_{}'.format(name))
        if new_count == 0:
            time.sleep(15)
        count += new_count
        start_date = end_date
    print 'Created dev set with %s games.' % str(count)
    count = 0
    while count < test:
        end_date = start_date + datetime.timedelta(days=2)
        new_count = scr.automated_scraping(start_date, end_date, 
                                           name='test_{}'.format(name))
        if new_count == 0:
            time.sleep(15)
        count += new_count
        start_date = end_date
    print 'Created test set with %s games.' % str(count)
    
    
def build_corpus(name='corpus', games_path='games/train_huge'):
    '''Builds a corpus of articles to train word2vec.'''
    f = open(games_path, 'rb')
    fw = open('games/{}.txt'.format(name), 'ab')
    count = 0
    while True:
        try:
            g = pickle.load(f)
            for t in g.text:
                new = t.replace(',', '')
                new = new.replace('.', '')
                for i in range(10):
                    new = new.replace(str(i), '')
                new = new.lower()
                fw.writelines(new)
                fw.write('\n')
                fw.write('\n')
            count += 1
            print 'Saved game {}.'.format(str(count))
        except EOFError:
            break
    print 'Saved {} games to corpus.'.format(str(count))
    f.close()
    fw.close()
    
    
def count_games(name):
    '''Small method to count the number of games in a given dataset.
    
    Only prints the number of games, does not return it.
    '''
    path = 'games/' + name
    f = open(path, 'rb')
    count = 0
    print 'Counting games in dataset {}.'.format(name)
    while True:
        try:
            pickle.load(f)
            count += 1
        except EOFError:
            break
    print 'Found {} games.'.format(count)
    f.close()
    
def testNER():
    import textUtil as txt
    import game as gme
    g = gme.Game(gme.URL_TESTS)
    text = ' '.join(g.text)
    begin = time.time()
    t, e = txt.anonymize(text)
    print time.time()-begin

# start_date = datetime.date(2015, 9, 10)
# scrape_games('small', start_date)

# build_corpus()

# full_test('skip_1_big', 'Who won?', 'train_big', 'train_dev', 'skip_1')
# full_test('skip_2_big', 'Who won?', 'train_big', 'train_dev', 'skip_2')
# full_test('word2vec', 'Who won?', 'train_big', 'train_dev', 'word2vec')

# -*- coding: utf-8 -*-
"""
Various scripts using our modules.

@author: Nathanael Romano and Daniel Levy
"""

import datetime
import time
import pickle

import scraping as scr

def scrape_games(name, start_date, train=30, dev=20, test=0):
    '''Creates a training, dev and test set.'''
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


start_date = datetime.date(2015, 9, 10)
#scrape_games('small', start_date)
build_corpus()
# -*- coding: utf-8 -*-
"""
Various scripts using our modules.

@author: Nathanael Romano and Daniel Levy
"""

import datetime

import scraping as scr

def scrape_games(name, start_date, train=200, dev=20):
    '''Creates a training, dev and test set.'''
    count = 0
    while count <= train:
        end_date = start_date + datetime.timedelta(days=10)
        new_count = scr.automated_scraping(start_date, end_date, 
                                           name='train_{}'.format(name))
        count += new_count
        if new_count == 0:
            raise scr.ScrapingException
        start_date = end_date
    print 'Created training set with %s games.' % str(count)
    count = 0
    while count <= dev:
        end_date = start_date + datetime.timedelta(days=10)
        new_count = scr.automated_scraping(start_date, end_date, 
                                           name='dev_{}'.format(name))
        if new_count == 0:
            raise scr.ScrapingException
        count += new_count
        start_date = end_date
    print 'Created dev set with %s games.' % str(count)
    count = 0
    while True:
        end_date = start_date + datetime.timedelta(days=10)
        new_count = scr.automated_scraping(start_date, end_date, 
                                           name='test_{}'.format(name))
        if new_count == 0:
            raise scr.ScrapingException
        count += new_count
        start_date = end_date
    print 'Created test set with %s games.' % str(count)


start_date = datetime.date(2015, 8, 1)
scrape_games('1', start_date)

# -*- coding: utf-8 -*-
"""
Method to build and dump the dataset. Hacky for now, should later be
automated.

@author: Nathanael Romano and Daniel Levy
"""

import pickle

import scraping
import game
import dataset as dt
import textUtil

DATE = '10/31/2015'

urls = scraping.getURLs(date=DATE, limit=30)
games = []
for url in urls:
    try:
        games.append(game.Game(url))
    except:
        continue

# Dataset for "Who won" question

def buildDataset(games, query, entities={}):
    '''Builds the data set for a list of games and a given query.
    
    TODO: modularize.
    '''
    t = []
    for g in games:
        text = g.text
     
        for i in range(len(text)):
            text[i], entities = textUtil.anonymize(text[i], entities)

        answer = g.query_dict[query]
        
        if answer == 'Draw':
            answer = g.home + ' ' + g.away

        inv_entities = {v: k for k, v in entities.items()}

        for s in text:
            s = '#BEGIN# ' + s + ' #END#'
            words = s.split(' ')
            
            for i in range(1, len(words)-1):
                if not textUtil.isToken(words[i]):
                    continue
                d = {}
                w_minus_1 = textUtil.removeToken(words[i-1])
                w_plus_1 = textUtil.removeToken(words[i+1])
                d['word'] = words[i]
                d['word_before_=_' + str(w_minus_1)] = 1
                d['word_after_=_' + str(w_plus_1)] = 1

                entityNumber = int(words[i][3:])
                if inv_entities[entityNumber] in answer.split(' '):
                    d['label'] = 1
                else:
                    d['label'] = 0
                t.append(d)

    d = dt.Dataset()
    d.append(t, fill=True)
    return d, entities

def run(name, query):
    '''Dumps the data set and entities to files.'''
    dataset, entities = buildDataset(games, query)
    dataset.toCSV('{}.csv'.format(name))
    dataset.saveColumns('{}.columns'.format(name))
    f = open('{}.entities'.format(name), 'w')
    pickle.dump(entities, f)
    f.close()

run('who_won_1031', 'Who won?')

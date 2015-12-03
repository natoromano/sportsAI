# -*- coding: utf-8 -*-
"""
Various scripts to test the algorithm and pipeline. NEEDS REFACTORING

@author: Nathanael Romano and Daniel Levy
"""

import sys
sys.path.append('liblinear/python/')

import pickle, copy
import liblinearutil as llb

import game
import dataset as dts
import textUtil as txt
import featureExtraction as ext
import training as trn
import scraping


def simple_test(name, query, method='skip_1'):
    '''Builds, train, and interactively test a simple model with few games, 
    for debugging.'''
    urls = scraping.getURLs('20151128')
    dts.build_and_dump(name, query, method=method, urls=urls)
    # dumps model
    trn.train_and_save(name, 'logistic_regression')
    irun(name, query, 3)
    

def with_dataset(name, query, path, method='skip_1'):
    '''Trains a model games that have already been scraped.'''
    dts.build_and_dump(name, query, method=method, path=path)
    #dumps model
    trn.train_and_save(name, 'logistic_regression')
    irun(name, query, 3)
    

def load(name):
    '''Loads the model and data.'''
    model = llb.load_model('models/{}.model'.format(name))
    return model


def predict(name, query, testGame, model, method='skip_1'):
    '''Predicts the answer to the query and returns an array of tuples (score,
    answer), as well as the correct answer.'''
    entities = {}
    # create Dataset object
    testSet = dts.Dataset(name)    
    text = testGame.text
    for i in range(len(text)):
        text[i], entities = txt.anonymize(text[i], entities)
    inv_entities = {v: k for k, v in entities.items()}
    # fetch answer
    answer = testGame.query_dict[query]
    text = testGame.text
    for i in range(len(text)):
        text[i], entities = txt.anonymize(text[i], entities)
    inv_entities = {v: k for k, v in entities.items()}
    # fetch answer
    answer = testGame.query_dict[query]
    # create feature vector for each entity in text
    for ent_id in inv_entities.iterkeys():
        ent_name = 'ent' + str(ent_id)
        feature_vector = ext.create_feature_vector(ent_name, text, method)
        label = label = (inv_entities[ent_id] in answer.split(' ')) * 1.0
        # add feature vector to dataset
        testSet.append((feature_vector, label), ent_name)
    scores = []
    words = testSet.entities
    _, _, probas = llb.predict(testSet.Y, testSet.X, model, '-b 1')
    for i, proba in enumerate(probas):
        scores.append((proba[1], inv_entities[int(words[i][3:])]))
    return scores, answer


def irun(name, query, debug=3):
    '''Interactive testing.
    
    If debug is given, it should be a number of scores to print.
    '''
    testUrl = ''
    model = load(name)
    
    while testUrl != 'stop':
        print 'Which URL? Enter stop to quit.'
        testUrl = raw_input()
        if testUrl == 'stop':
            break
        try:
            testGame = game.Game(testUrl)
        except:
            print 'Could not load game. Try again.'
            continue
        scores, answer = predict(name, query, testGame, model, 'skip_1')
        print 'Query:', query
        print 'I think the answer is {}.'.format(max(scores)[1])
        print 'It is actually {}.'.format(answer)
        if debug:
            scores.sort()
            print 'Top {}'.format(debug), [s[1] for s in scores][-debug:] 

     
def test(name, query, date, number=10, flexible=True):
    '''####### OBSOLETE #######'''
    output = []
    correct = 0
    print 'Testing ...'
    for url in scraping.getURLs(date, limit=2*number):
        try:
            testGame = game.Game(url)
        except:
            continue
        if len(output) >= number:
            break
        model, entities, columns = load(name)
        scores, answer = predict(name, query, testGame, 
                                 model, entities, columns)
        scores.sort()
        if scores:
            output.append((scores[-1][1], answer))
            if flexible:
                flag = False
                for score in scores[-3:]:
                    if score[1] in answer:
                        flag = True
                correct += flag * 1.0
            else:
                correct += (scores[-1][1] in answer) * 1.0
    if not output:
        raise ValueError('No output!')
    return correct / float(len(output))
        

#simple_test()
#irun('who_won_6', 'Who won?', 3)
#accuracy = test('who_won_1031', 'Who won?', '10/24/2015', 20, False)
#print 'Accuracy :', accuracy

# -*- coding: utf-8 -*-
"""
Script to test the algorithm. NEEDS REFACTORING

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


def simple_test():
    '''Trains and interactively test a simple model with few games, 
    for debugging.'''
    query = 'Who won?'
    urls = scraping.getURLs('11/28/2015', limit=30)
    dts.build_and_dump(query, urls)
    name = txt.queryName(query) + '_' + str(len(urls))
    # dumps model
    trn.train(name, 'logistic_regression')
    irun(name, query, 3)
    

def load(name):
    '''Loads the model and data.'''
    model = llb.load_model('models/{}.model'.format(name))
    oldEntities = pickle.load(open('data/{}.entities'.format(name), 'r')) 
    entities = copy.deepcopy(oldEntities)
    return model, entities


def predict(name, query, testGame, model, method='skip_1', entities=None):
    '''Predicts the answer to the query and returns an array of tuples (score,
    answer), as well as the correct answer. ONLY WORKS WITH 1-SKIP
    
    The three last inputs should be the output of the load() function.
    '''
    entities = entities or {}
    # create Dataset object
    testSet = dts.Dataset(name)    
    text = testGame.text
    for i in range(len(text)):
        text[i], entities = txt.anonymize(text[i], entities)
    inv_entities = {v: k for k, v in entities.items()}
    # fetch answer
    answer = testGame.query_dict[query]
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
            testSet.append((feature_vector, label), words[i])
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
    model, entities = load(name)
    
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
        scores, answer = predict(name, query, testGame, model, 'skip_1', 
                                 entities)
        print 'Query:', query
        print 'I think the answer is {}.'.format(max(scores)[1])
        print 'It is actually {}.'.format(answer)
        if debug:
            scores.sort()
            print 'Top {}'.format(debug), [s[1] for s in scores][-debug:] 

     
def test(name, query, date, number=10, flexible=True):
    '''Performs an automatic testing over a certain number of games on a given
    date and returns an array of (predicted answer, actual answer).
    
    The games will be randomly selected from this dates (see textUtil.getUrls.
    '''
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

# -*- coding: utf-8 -*-
"""
Script to test the algorithm. NEEDS REFACTORING

@author: Nathanael Romano and Daniel Levy
"""

import pickle, copy
import re

import game
import dataset
import textUtil
import scraping


def load(name):
    '''Loads the model and data.'''
    model = pickle.load(open('{}.model'.format(name),'r'))
    oldEntities = pickle.load(open('{}.entities'.format(name),'r')) 
    entities = copy.deepcopy(oldEntities)
    columns = pickle.load(open('{}.columns'.format(name),'r'))
    columns = columns[columns != 'label']
    columns = columns[columns != 'word']
    return model, entities, columns


def predict(name, query, testGame, model, entities, columns):
    '''Predicts the answer to the query and returns an array of tuples (score,
    answer), as well as the correct answer.
    
    The three last inputs should be the output of the load() function.
    '''
    testSet = dataset.Dataset.fromHeader('{}.columns'.format(name))
    text = testGame.text
    test = []
    for i,_ in enumerate(text):
        text[i], entities = textUtil.anonymize(text[i], entities)
    answer = testGame.query_dict[query]
    if answer == 'Draw':
        answer = testGame.home + ' ' + testGame.away
    inv_entities = {v: k for k,v in entities.items()}
    for s in text:
        s = '#BEGIN# '+s+' #END'
        words = s.split(' ')
        for i in range(1, len(words)-1):
            if re.match(ur'ent[1-9]+', words[i]) == None:
                continue
            d = {}
            w_minus_1 = words[i-1]
            w_plus_1 = words[i+1]
            d['word'] = words[i]
            d['word_before_=_'+str(w_minus_1)] = 1
            d['word_after_=_'+str(w_plus_1)] = 1
            entityNumber = int(words[i][3:])
            if inv_entities[entityNumber] in answer.split(' '):
                d['label'] = 1
            else:
                d['label'] = 0
            test.append(d)
    testSet.append(test, fill=True)  
    words = testSet.getY(labelColumn='word') 
    testing = testSet.df[columns]
    scores = []
    for i, r in enumerate(testing.iterrows()):
        entityNumber = int(words[i][3:])
        score = model.predict_log_proba(r[1])[0][1]
        scores.append((score, inv_entities[entityNumber]))
    return scores, answer


def irun(name, query, debug=None):
    '''Interactive testing.
    
    If debug is given, it should be a number of scores to print.
    '''
    testUrl = ''
    model, entities, columns = load(name)
    
    while testUrl != 'stop':
        print 'Which URL? Enter stop to quit.'
        testUrl = raw_input()
        if testUrl == 'stop':
            break
        testGame = game.Game(testUrl)
        scores, answer = predict(name, query, 
                                 testGame, model, entities, columns)
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
        

#irun('who_won_1031', 'Who won?', False)
accuracy = test('who_won_1031', 'Who won?', '10/24/2015', 20, False)
print 'Accuracy :', accuracy

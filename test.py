# -*- coding: utf-8 -*-
"""
Various scripts to test the algorithm and pipeline.

@author: Nathanael Romano and Daniel Levy
"""

import sys
import pickle
sys.path.append('liblinear/python/')

import liblinearutil as llb

import game as gme
import dataset as dts
import textUtil as txt
import featureExtraction as ext


def load(name):
    '''Loads the model and data.
    
    Columns is a dictionnary used when the feature keys were converted to 
    numbers, for liblinear.
    '''
    model = llb.load_model('models/{}.model'.format(name))
    columns = dts.Dataset.from_columns(name)._features
    return model, columns


def predict(name, query, testGame, model, method='skip_1'):
    '''Predicts the answer to the query and returns an array of tuples (score,
    answers), as well as the correct answer.
    
    In the tuples, answers is all the possible right answers e.g. ['Ronaldo',
    'Cristiano Ronaldo', 'Cristiano'].
    '''
    entities = {}
    # create Dataset object
    testSet = dts.Dataset.from_columns(name)    
    text = ' '.join([t.decode() for t in testGame.text])
    text, entities = txt.anonymize(text)
    #for i in range(len(text)):
        #text[i], entities = txt.anonymize(text[i], entities)
    inv_entities = {v: k for k, v in entities.items()}
    # fetch answer
    try:
        answer = testGame.query_dict[query]
    except KeyError:
        answer = 'N/A'
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
            testSet.append((feature_vector, label), ent_name)
        else:
            feature_vector = ext.create_feature_vector(ent_name, text,
                                                       method, model=model)
            try:
                label = (ent_id == inv_entities[answer]) * 1.0
            except KeyError:
                label = (inv_entities[ent_id] in answer) * 1.0 
            testSet.append((dict(zip(range(len(feature_vector)), 
                                     feature_vector)), label), ent_name)
    scores = []
    words = testSet.entities
    _, _, probas = llb.predict(testSet.Y, testSet.X, model, '-b 1')
    for i, proba in enumerate(probas):
        scores.append((proba[1], 
                       [k for k,v in entities.iteritems() \
                       if str(v) == words[i][3:]]))
    return scores, answer


def irun(name, query, debug=3):
    '''Interactive testing, using a trained model.
    
    If debug is given, it should be a number of scores to print.
    '''
    testUrl = ''
    model, _ = load(name)
    while testUrl != 'stop':
        print 'Which URL? Enter stop to quit.'
        testUrl = raw_input()
        if testUrl == 'stop':
            break
        try:
            testGame = gme.Game(testUrl)
        except Exception as e:
            print e
            print 'Could not load game. Try again.'
            continue
        scores, answer = predict(name, query, testGame, model, 'skip_1')
        print 'Query:', query
        print 'I think the answer is {}.'.format(max(scores)[1])
        print 'It is actually {}.'.format(answer)
        if debug:
            scores.sort()
            print 'Top {}'.format(debug), [s[1] for s in scores][-debug:] 
            
    
def get_weights(model_name):
    '''Returns a list of 'weight, feature) couples, for a specific model.'''
    model, columns = load(model_name)
    inv_columns = {v:k for k, v in columns.iteritems()}
    return [(model.get_decfun_coef(i, 1), inv_columns[i]) \
                        for i in inv_columns.iterkeys()]


def test(name, test_set, query, method='skip_1'):
    '''Tests the model with given name against the given test set, for the
    specific query and given method.
    
    test_set should be the name of the set, e.g. dev_big.
    '''
    def is_correct(scores, answer):
        '''Returns true if the answer given by scores is the correct answer.
        
        Answer is the correct answer, scores is a list of tuples in the form
        probability, list of entities.
        '''
        return answer in scores[-1][1]
    output = []
    correct = 0
    print 'Testing on {}...'.format(test_set)
    f = open('games/{}'.format(test_set), 'rb')
    while True:
        try:
            testGame = pickle.load(f)
        except EOFError:
            break
        model, columns = load(name)
        scores, answer = predict(name, query, testGame, model, method)
        scores.sort()
        if scores:
            output.append((scores[-1], answer))
        if is_correct(scores, answer):
            correct += 1
    if not output:
        raise ValueError('No output!')
    accuracy = 100.*float(correct)/len(output)
    print 'Accuracy on test set: {}%'.format(str(accuracy))
    return output, accuracy

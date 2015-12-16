# -*- coding: utf-8 -*-
"""
Various tools used on our text data. Some of them are from open sources
libraries.

@author: Nathanael Romano and Daniel Levy
"""

import re
import string

from nltk.tag import StanfordNERTagger
import nltk
st = StanfordNERTagger('NER/english.all.3class.distsim.crf.ser.gz', 
                       'NER/stanford-ner.jar')

ARTEFACTS = ['\n', '\t']
COUNTERS = ['0', 'first', 'second', 'third', 'fourth', 'fifth',
                'sixth', 'seventh', 'eigth', 'ninth']
ENTITY_TOKEN = 'ent'
STOP_WORDS = ['the', 'and', 'in', 'was', 'when', 'to' 'his', 'had', 'with']


def isClean(st):
    '''Checks that a given string is clean, i.e. does not have encoding
    artefacts.'''
    return all([artefact not in st for artefact in ARTEFACTS])


def cleanText(text):
    '''Cleans input text, with respect to the "artefacts" list.
    
    The [:-4] at the end removes the last three paragraphs, corresponding to
    the "share on Facebook" lines of the website.
    '''
    if isinstance(text, list):
        text = [str(st) for st in text if isClean(st)]
    if isinstance(text, str):
        for artefact in ARTEFACTS:
            text = text.replace(artefact, '')
    return text[:-4]

    
def nth(n):
    '''Returns the string associated with the english sentence 'nth'. Hacky.'''
    if n < len(COUNTERS):
        return COUNTERS[n]
    else:
        return '{}th'.format(str(n))
 
       
def is_entity(word):
    '''Returns true if the word is an entity.
    
    Now obsolete with the NER entity tagging.
    '''
    if word.upper() == word:
        return True
    if '\'' in word:
        return word.replace('\'', '').istitle()
    return word.istitle()
 

def anonymize(text):
    '''Anonymization and entity recognition using Stanford NER.
    
    Returns the text and a dictionnary entity:id.
    Also removes stop words and scores.
    '''
    def irrelevant(word):
        '''Returns True if the word is a score or a stop word.'''
        if word in STOP_WORDS:
            return True
        if len(word.split('-')) == 2:
            if all([w in string.digits for w in word.split('-')]):
                return True
        return False
    tokens = nltk.word_tokenize(text)
    tags = st.tag(tokens)
    res = []
    i = 0
    while i < len(tags):
        word, tag = tags[i]  
        if tag in ['PERSON','ORGANIZATION','LOCATION']:
            j = i+1
            while j < len(tags) and tags[j][1] == tag:
                word = word + ' ' + tags[j][0]
                j = j+1
            i = j
        else:
            i = i+1
        res.append((word, tag))
    d = set([w for w, t in res if t in ['PERSON','ORGANIZATION','LOCATION']])
    def rel(x,y):
        '''Checks if x and y can be the same entity.'''
        if x in y or y in x:
            return True
        if isAcronymOf(x,y) or isAcronymOf(y,x):
            return True
        return False
    def isAcronymOf(s,t):
        '''Checks if t is an actronym s.'''
        buff = ''
        for l in s:
            if l == l.upper():
                buff += l
        return buff == t
    def makeEquivalentSets(items, rel):
        '''Creates set of equivalent entities.'''
        association = {}
        sets = []
        i = 0
        while len(items) > 0:
            w = items.pop()
            s = set()
            for v in items:
                if rel(w,v):
                    s.add(v)
                    association[v] = i
            for v in s:
                items.remove(v)
            s.add(w)
            association[w] = i
            sets.append(s)
            i += 1
        return sets, association
    s, a = makeEquivalentSets(d, rel)
    for entity in a:
        text = text.replace(entity, ENTITY_TOKEN + str(a[entity]))
    text = ' '.join([t for t in text.split() if not irrelevant(t)])
    return text, a

    
def isToken(word):
    '''Returns true if the given word is of the form 'entX'.'''
    if not word:
        return False
    return re.match(ur'ent[0-9]+', word) is not None


def removeToken(word):
    '''Returns the word if its not a token, 'ent' otherwise.'''
    if isToken(word):
        return ENTITY_TOKEN
    else:
        return word.lower()

def queryName(query):
    '''Turns a query like 'Who won?' into 'who_won'.'''
    return '_'.join(query.lower()[:-1].split())

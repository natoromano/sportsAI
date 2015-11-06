# -*- coding: utf-8 -*-
"""
Various tools used on our text data. Some of them are from open sources
libraries.

@author: Nathanael Romano and Daniel Levy
"""

ARTEFACTS = ['\n', '\t']
COUNTERS = ['0', 'first', 'second', 'third', 'fourth', 'fifth',
                'sixth', 'seventh', 'eigth', 'ninth']

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
        text = [st for st in text if isClean(st)]
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

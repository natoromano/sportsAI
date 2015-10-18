# -*- coding: utf-8 -*-
"""
Various tools used on our text data. Some of them are from open sources
libraries.

@author: Nathanael Romano and Daniel Levy
"""

ARTEFACTS = ['\n', '\t']

def isClean(st):
    '''Checks that a given string is clean, i.e. does not have encoding
    artefacts.'''
    return all([artefact not in st] for artefact in ARTEFACTS)

def cleanText(text):
    '''Cleans input text, with respect to the "artefacts" list.'''
    if isinstance(text, list):
        text = [st for st in text if isClean(st)]
    if isinstance(text, str):
        for artefact in ARTEFACTS:
            text = text.replace(artefact, '')
    return text
    
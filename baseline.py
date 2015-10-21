# -*- coding: utf-8 -*-
"""
Methods used for a baseline evaluation of the problem, using a simple tf-idf
score.

@author: Nathanael Romano and Daniel Levy
"""

import sys
import math

from game import TrainingGame

def loop():
    '''Loop function for interactive testing.'''
    while True:
        sys.stdout.write('Enter game url: ')
        url = sys.stdin.readline()
        if not url:
            break
        try:
            print 'Fetching game report...'
            game = TrainingGame(url)
        except IndexError:
            break
            
        while True:
            sys.stdout.write('Question: ')
            query = sys.stdin.readline().strip().lower()
            if not query:
                break
            query.replace('?', '')
            print bestParagraph(game, query)
            print ''
        
def bestParagraph(game, question):
    '''Returns the best paragraph in game wrt to the given query.'''
    def tfIdf(query, paragraph, text):
        '''Computes the tfIdf score for query and paragraph in text.'''
        val = 0
        for word in query.split():
            if word in paragraph:
                tf = len([w for w in paragraph.split() if word in w])
                tf /= float(len(paragraph.split()))
                idf = math.log(float(len(text)) / \
                               (1 + len([p for p in text if word in p])))
                val += tf * idf
        return val
    text = [p.lower() for p in game.text]
    return max((tfIdf(question, p, text), p) for p in text if len(p) > 0)[1]
    
if __name__ == '__main__':
    loop()

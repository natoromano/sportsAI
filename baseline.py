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
    '''REPL: read, evaluate, print, loop'''

    while True:
        sys.stdout.write('Enter game url: ')
        url = sys.stdin.readline()
        if not url:
            break
        game = TrainingGame(url)
        
        sys.stdout.write('Question: ')
        query = sys.stdin.readline().strip().lower()
        query.replace('?', '')
        print bestParagraph(game, query)
        print ''
        
def bestParagraph(game, question):
    '''Returns the best paragraph in game wrt to the given query.'''
    def tfIdf(query, paragraph, text):
        val = 0
        d = paragraph.split()
        for word in query.split():
            d = paragraph.split()
            if len(d) == 0:
                continue
            f = len([w for w in d if w in word or word in w]) / float(len(d))
            tf = 1 + math.log(f) if f > 0 else 0
            idf = math.log(float(len(text)) / \
                           (1 + len([p for p in text if word in p])))
            val += tf * idf
        return val
    paragraphs = [p.lower() for p in game.text]
    return max((tfIdf(question, p, paragraphs), p) for p in paragraphs \
                                                            if len(p) > 0)[1]

def main():
    loop()
    
if __name__ == '__main__':
    loop()

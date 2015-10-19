# -*- coding: utf-8 -*-
"""
Classes and methods to handle the games.

@author: Nathanael Romano and Daniel Levy
"""

import scraping

URL_TESTS = 'http://www.espnfc.us/barclays-premier-league/' + \
            'match/422580/everton-manchester-united/report'

class Game(object):
    '''General class for games.
    
    init method now takes the report url as an argument, but could later take
    only the team names.
    
    It has many properties, that are used in the train set to analyze the
    comments, and automatically find the answer to the questions.
    '''
    
    def __init__(self, url):
        self.id = url.split('/')[self.ID_POSITION]
        self.url = url
        self.tree = scraping.getTree(url)
        self.text = scraping.getText(self.tree)
        self.home, self.away = scraping.getTeams(self.tree)


class TrainingGame(Game):
    '''A game used to train the algorithm.'''
    
    ID_POSITION = 5
    GOAL_BEACON = 'Goal!'
    
    def __init__(self, url):
        super(TrainingGame, self).__init__(url)
        self.comments = scraping.getComments(self.id)
    
    @property # FIXME: implement cached property decorator
    def goals(self): # FIXME: problem with own goals!!
        '''Returns the list of tuples 'minute, comment" for the game's goals,
        ordered by minute.'''
        return [(int(minute[:-1]), comment) for minute, 
                comment in self.comments if self.GOAL_BEACON in comment]
        
    @property
    def scores(self):
        '''Returns a list of tuples minute, score, where a score is a dict that
        maps teams to number of goals.'''
        def getScore(goal):
            '''Finds the resulting score of a goal comment.'''
            score = goal[len(self.GOAL_BEACON)+2:goal.index('.')].split(',')
            return dict([(score[0][:-2], score[0][-1]), 
                         (score[1][:-2], score[1][-1])])
        return [(goal[0], getScore(goal[1])) for goal in self.goals]

    def scorer(self, n):
        '''Returns the nth scorer of the game.'''
        pass

    @property
    def scoreAtHalfTime(self):
        '''Returns the score at half time.'''
        pass
    
    @property
    def finalScore(self):
        '''Returns the final score.'''
        pass

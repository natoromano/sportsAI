# -*- coding: utf-8 -*-
"""
Classes and methods to handle the games.

@author: Nathanael Romano and Daniel Levy
"""

import scraping
import textUtil

URL_TESTS = 'http://www.espnfc.us/barclays-premier-league/' + \
            'match/422580/everton-manchester-united/report'

class Game(object):
    '''General class for games.
    
    init method now takes the report url as an argument, but could later take
    only the team names.
    
    It has many properties, that are used in the train set to analyze the
    comments, and automatically find the answer to the questions.
    '''
    
    ID_POSITION = 5
    GOAL_BEACON = 'Goal!'
    OWN_GOAL = 'Own Goal'
    HALFTIME = 45
    
    def __init__(self, url, comments=True):
        self.id = url.split('/')[self.ID_POSITION]
        self.url = url
        self.tree = scraping.getTree(url)
        self.text = scraping.getText(self.tree)
        self.home, self.away = scraping.getTeams(self.tree)
        self.comments = scraping.getComments(self.id)
        self.goals = self.get_goals()
        self.queries = self.create_queries()
    
    def get_goals(self):
        '''Returns the list of tuples 'minute, comment" for the game's goals,
        ordered by minute.'''
        return sorted([(int(minute[:-1]), comment) for minute, 
                comment in self.comments if self.GOAL_BEACON in comment \
                                            or self.OWN_GOAL in comment])
                
    def team_goals(self, team):
        '''Returns the list of goals scored by the given team.'''
        def is_team(goal):
            return goal[goal.index('(')+1:goal.index(')')] == team
        return [goal for goal in self.goals if is_team(goal[1])]
        
    @property
    def scores(self):
        '''Returns a list of tuples minute, score, where a score is a dict that
        maps teams to number of goals.'''
        def getScore(goal):
            '''Finds the resulting score of a goal comment.'''
            if self.GOAL_BEACON in goal:
                score=goal[len(self.GOAL_BEACON)+2:goal.index('.')].split(',')
                return dict([(score[0][:-2], score[0][-1]), 
                             (score[1][1:-2], score[1][-1])])
            if self.OWN_GOAL in goal:
                score = goal[goal.index('.')+2:-1].split(',')
                return dict([(score[0][1:-2], score[0][-1]), 
                             (score[1][1:-2], score[1][-1])])
        return [(goal[0], getScore(goal[1])) for goal in self.goals]

    def scorer(self, n):
        '''Returns the nth scorer of the game.
        
        The function should never be callsed with n > len(self.goals).
        '''
        if n > len(self.goals):
            return None
        goal = self.goals[n-1][1]
        if self.GOAL_BEACON in goal:
            return goal[goal.index('.')+2:goal.index('(')-1]
        else:
            return goal[goal.index('by')+4:goal.index(',')]
    
    def team_scorer(self, n, team):
        '''Returns the nth scorer of the game for the given team.
        
        The function should never be called with n > len(team_goals(team)).
        '''
        if n > len(self.team_goals(team)):
            return None
        goal = self.team_goals(team)[n-1][1]
        if self.GOAL_BEACON in goal:
            return goal[goal.index('.')+2:goal.index('(')-1]
        else:
            return goal[goal.index('by')+4:goal.index(',')]

    @property
    def half_time_score(self):
        '''Returns the score at half time.'''
        try:
            return max(g for g in self.scores if int(g[0] <= 45))[1]
        except ValueError:
            return {self.home:0, self.away:0}
    
    @property
    def final_score(self):
        '''Returns the final score.'''
        try:
            return self.scores[-1][1]
        except IndexError:
            return {self.home:0, self.away:0}

    @property
    def winner(self):
        '''The game's loser.
        
        Will return 'Draw' if the game is a draw.
        '''
        final_score = self.final_score
        if final_score.values()[0] == final_score.values()[1]:
            return 'Draw'
        return max((v, k) for k,v in final_score.iteritems())[1]

    @property
    def loser(self):
        '''The game's winner.
        
        Will return 'Draw if the game is a draw.
        '''
        if self.winner == 'Draw':
            return 'Draw'
        if self.winner == self.home:
            return self.away
        else:
            return self.home

    def create_queries(self):
        '''Creates all the queries associated with self.'''
        queries = []
        # winner/loser queries
        queries.append(Query('Who won?', self.winner))
        queries.append(Query('Who lost?', self.loser))
        # score queries
        queries.append(Query('What was the score at half time?', 
                             self.half_time_score))
        queries.append(Query('What was the final score?', self.final_score))
        # scorer queries
        for i in range(1, len(self.goals) + 1):
            query = 'Who scored the {} goal?'.format(textUtil.nth(i))
            queries.append(Query(query, self.scorer(i)))
        # team scorer queries
        for team in [self.home, self.away]:
            for i in range(1, len(self.team_goals(team)) + 1):
                query = 'Who scored the {} goal for {}?'.format(\
                                                        textUtil.nth(i), team)
                queries.append(Query(query, self.team_scorer(i, team)))
        return queries      

    @property        
    def query_dict(self):
        '''Returns the game queries in the form of a map question:answer.'''
        return dict((q.query, q.answer) for q in self.queries)
        

class Query(object):
    '''A query object.
    
    Later on, query-matching methods (to allow some flexibility) will be 
    implemented here.
    '''
    
    def __init__(self, question, answer):
        self.query = question
        self.answer = answer
        
    def __repr__(self):
        '''Custom representation for queries.'''
        return '%s - %s' % (self.query, self.answer)

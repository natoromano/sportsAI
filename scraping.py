# -*- coding: utf-8 -*-
"""
Methods to retrieve game summaries and statistical data from sports websites.

@author: Nathanael Romano and Daniel Levy
"""

import random

from lxml import html
import requests

from textUtil import cleanText

COMMENTS_URL = 'http://www.espnfc.us/commentary/{}/commentary.html'
SCORES_URL = 'http://www.espnfc.us/scores?date={}'
VALID_LEAGUES = ['barclays', 'italian', 'spanish', 'german', 'french',
                 'championship', 'scottish', 'italian']

class ScrapingException(Exception):
    pass

def getTree(url):
    '''Gets the html element tree corresponding to given url.'''
    tree = html.fromstring(requests.get(url).text)
    return tree
    
def getText(tree):
    '''Returns the article's cleaned full text.
    
    For now, as a list of paragraphs. Might be better to simply return the full
    collapsed text.
    '''
    text = tree.xpath('//h1/text()')
    text.extend(tree.xpath('//p/text()'))
    return cleanText(text)

def getURLs(date, limit=None, league=None):
    '''Gets all game urls from a specific date.
    
    A limit in the number of urls can be set, in this case random games will
    be returned.
    Otherwise, a league can be specified from the following list : barclays,
    spanish, german, french, scottish, italian
    '''
    formatDate = date.split('/')[-1] + date.split('/')[0] + date.split('/')[1]
    tree = getTree(SCORES_URL.format(formatDate))
    query = '//div[@class="score-box"]//a[@class="primary-link"]/@href'
    urls = [url for url in tree.xpath(query) if 'report' in url]
    if limit:
        random.shuffle(urls)
        urls = urls[:limit]
    def valid_league(url, league):
        if league:
            return league in url
        for league in VALID_LEAGUES:
            if league in url:
                return True
        return False
    return [url for url in urls if valid_league(url, league)]

def getTeams(tree):
    '''Returns the two playing teams: home, away.'''
    path = '//div[@class="above-fold"]//div[@class="team-name"]/span/text()'
    teams = tree.xpath(path)
    return teams[0], teams[1]
    
def getComments(gameID):
    '''Returns the list of comments, in the form of tuples (minute, comment).
    
    To be used to automatically label the training data.
    '''
    url = COMMENTS_URL.format(gameID)
    tree = getTree(url)
    timestamps =  tree.xpath('//li/div[@class="timestamp"]/p/text()')
    comments = tree.xpath('//li/div[@class="comment"]/p/text()')
    return zip(timestamps, comments)[::-1]

# -*- coding: utf-8 -*-
"""
Methods to retrieve game summaries and statistical data from sports websites,
as well as methods to automatically scrape a large number of games from the
ESPN website.

@author: Nathanael Romano and Daniel Levy
"""

import random
import datetime

from lxml import html
import requests

from textUtil import cleanText
import game as gme

COMMENTS_URL = 'http://www.espnfc.us/commentary/{}/commentary.html'
SCORES_URL = 'http://www.espnfc.us/scores?date={}'
VALID_LEAGUES = ['barclays', 'italian', 'spanish', 'german', 'french', 
                 'scottish', 'championship']
PATH = 'games/'


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
    tree = getTree(SCORES_URL.format(date))
    query = '//div[@class="score-box"]//a[@class="primary-link"]/@href'
    urls = [url for url in tree.xpath(query) if 'report' in url]
    if limit:
        random.shuffle(urls)
        urls = urls[:limit]
    def valid_game(url, league):
        '''If a league was given, checks that the url is for the given url.
        Otherwise, checks that the word 'report' is in the url, meaning that
        there is a report for the given game.'''
        if league:
            return league in url
        return 'report' in url
    return [str(url) for url in urls if valid_game(url, league)]


def getTeams(tree):
    '''Returns the two playing teams: home, away.'''
    path = '//div[@class="above-fold"]//div[@class="team-name"]/span/text()'
    teams = tree.xpath(path)
    return str(teams[0]), str(teams[1])
 
   
def getComments(gameID):
    '''Returns the list of comments, in the form of tuples (minute, comment).
    
    To be used to automatically label the training data.
    '''
    url = COMMENTS_URL.format(gameID)
    tree = getTree(url)
    timestamps =  tree.xpath('//li/div[@class="timestamp"]/p/text()')
    comments = tree.xpath('//li/div[@class="comment"]/p/text()')
    return zip([str(t) for t in timestamps], [str(c) for c in comments])[::-1]

### AUTOMATED LARGE-SCALE SCRAPING ###

def interactive_scraping(name=None):
    '''Methods for interactively scraping selected dates.
    
    The try/except clauses are here because sometimes the scraping does not
    work, because of the EPSN website. In this case, the error is often a list
    index out of range, as most of the scraping methods will break when they
    reach specific areas of the HTML source code.
    '''
    name = name or 'main'
    path = PATH + name
    cmd = ''
    while cmd != 'stop':
        print 'Enter a date to scrape'
        cmd = raw_input()
        if cmd == 'stop':
            break
        try:
            urls = getURLs(cmd)
        except:
            print 'Input is not in valid format (yyyymmdd).'
            continue
        print 'Found {} games.'.format(len(urls))
        count = 0
        for url in urls:
            try:
                g = gme.Game(url)
                g.dump(path)
                count += 1
            except Exception as e:
                print e
                continue
        print 'Successfully saved {} games'.format(str(count))
        

def automated_scraping(start_date=None, stop_date=None, name=None):
    '''Automatically scrapes and saves multiples games, between given dates.
    
    Dates should be given in datetime format.
    The try/except clauses are here because sometimes the scraping does not
    work, because of the EPSN website. In this case, the error is often a list
    index out of range, as most of the scraping methods will break when they
    reach specific areas of the HTML source code.
    '''
    def make_date(date):
        '''Creates a date in a string format: yyyymmdd.'''
        return ''.join(str(date).split('-'))
    if not start_date:
        start_date = datetime.date(2015, 8, 1)
    if not stop_date or stop_date > datetime.date(2015, 12, 3):
        stop_date = datetime.date(2015, 12, 3)
    name = name or 'main'
    path = PATH + name
    date = start_date
    count = 0
    while date != stop_date:
        # for each date, fetch all valid URLs
        try:
            urls = getURLs(make_date(date))
        except:
            # try second time
            try:
                urls = getURLs(make_date(date))
            except:
                # try third and last time
                try:
                    urls = getURLs(make_date(date))
                except:
                    print 'Could not fetch URLs for {}.'.format(date)
                    continue
        print 'Found {} games for {}.'.format(len(urls),date)
        for url in urls:
            # for each URL, create and dump Game
            try:
                g = gme.Game(url)
                g.dump(path)
                count += 1
            except:
                continue
        # go to next day
        date += datetime.timedelta(days=1)
    print 'Successfully saved {} games'.format(str(count))
    return count
            
import scraping, game
import textUtil
import pandas as pd
import dataset
import re

urls = ['http://www.espnfc.us/barclays-premier-league/match/422548/aston-villa-manchester-city/report', 'http://www.espnfc.us/barclays-premier-league/match/422552/arsenal-tottenham-hotspur/report', 'http://www.espnfc.us/spanish-primera-division/match/433868/athletic-bilbao-espanyol/report', 'http://www.espnfc.us/spanish-primera-division/match/433876/barcelona-villarreal/report', 'http://www.espnfc.us/spanish-primera-division/match/433874/atletico-madrid-sporting-gijon/report', 'http://www.espnfc.us/major-league-soccer/match/437318/new-york-red-bulls-dc-united/report', 'http://www.espnfc.us/major-league-soccer/match/437319/columbus-crew-sc-montreal-impact/report', 'http://www.espnfc.us/major-league-soccer/match/437321/fc-dallas-seattle-sounders-fc/report', 'http://www.espnfc.us/german-bundesliga/match/427020/borussia-dortmund-schalke-04/report', 'http://www.espnfc.us/german-bundesliga/match/427025/fc-augsburg-werder-bremen/report', 'http://www.espnfc.us/italian-serie-a/match/432155/torino-internazionale/report', 'http://www.espnfc.us/italian-serie-a/match/432157/as-roma-lazio/report', 'http://www.espnfc.us/italian-serie-a/match/432156/empoli-juventus/report', 'http://www.espnfc.us/italian-serie-a/match/432152/palermo-chievo-verona/report', 'http://www.espnfc.us/italian-serie-a/match/432151/sassuolo-carpi/report', 'http://www.espnfc.us/italian-serie-a/match/432158/napoli-udinese/report', 'http://www.espnfc.us/italian-serie-a/match/432153/sampdoria-fiorentina/report', 'http://www.espnfc.us/french-ligue-1/match/424620/marseille-nice/report', 'http://www.espnfc.us/french-ligue-1/match/424618/bordeaux-as-monaco/report', 'http://www.espnfc.us/french-ligue-1/match/424622/lyon-st-etienne/report', 'http://www.espnfc.us/english-fa-cup/match/437280/didcot-town-fc-exeter-city/report', 'http://www.espnfc.us/english-fa-cup/match/437272/aldershot-town-bradford-city/report', 'http://www.espnfc.us/english-fa-cup/match/437275/brackley-town-newport-county/report', 'http://www.espnfc.us/english-fa-cup/match/437273/bristol-rovers-chesham-united/report', 'http://www.espnfc.us/english-fa-cup/match/437278/fc-halifax-town-wycombe-wanderers/report', 'http://www.espnfc.us/english-fa-cup/match/437277/gainsborough-trinity-shrewsbury-town/report', 'http://www.espnfc.us/english-fa-cup/match/437279/maidstone-united-yeovil-town/report', 'http://www.espnfc.us/english-fa-cup/match/437274/whitehawk-fc-lincoln-city/report', 'http://www.espnfc.us/english-fa-cup/match/437271/port-vale-maidenhead-utd/report', 'http://www.espnfc.us/scottish-premiership/match/425247/ross-county-celtic/report']

games = [game.Game(url) for url in urls]

# Dataset for "Who won" question

def buildDataset(games, query, entities={}):
    t = []
    for game in games:
        text = game.text
        
        for i in range(len(text)):
            text[i], entities = textUtil.anonymize(text[i], entities)

        answer = game.query_dict[query]
        
        if answer == 'Draw':
            answer = game.home+' '+game.away

        inv_entities = {v: k for k, v in entities.items()}

        for s in text:
            s = '#BEGIN# '+s+' #END#'
            words = s.split(' ')
            
            for i in range(1,len(words)-1):
                if re.match(ur'ent[1-9]+', words[i]) == None:
                    continue
                d = {}
                w_minus_1 = words[i-1]
                w_plus_1 = words[i+1]
                d['word'] = words[i]
                d['word_before_=_'+str(w_minus_1)] = 1
                d['word_after_=_'+str(w_plus_1)] = 1

                entityNumber = int(words[i][3:])
                if inv_entities[entityNumber] in answer.split(' '):
                    d['label'] = 1
                else:
                    d['label'] = 0
                t.append(d)

    d = dataset.Dataset()
    d.append(t, fill=True)
    return d, entities


dataset, entities = buildDataset(games, 'Who won?')
dataset.toCSV('who_won_30.csv')
dataset.saveColumns('who_won_30.columns')

import pickle

f = open('who_won_30.entities','w')
pickle.dump(entities, f)
f.close()


import scraping, game

import pandas as pd

urls = ['http://www.espnfc.us/barclays-premier-league/match/422548/aston-villa-manchester-city/report', 'http://www.espnfc.us/barclays-premier-league/match/422552/arsenal-tottenham-hotspur/report', 'http://www.espnfc.us/spanish-primera-division/match/433868/athletic-bilbao-espanyol/report', 'http://www.espnfc.us/spanish-primera-division/match/433876/barcelona-villarreal/report', 'http://www.espnfc.us/spanish-primera-division/match/433874/atletico-madrid-sporting-gijon/report', 'http://www.espnfc.us/major-league-soccer/match/437318/new-york-red-bulls-dc-united/report', 'http://www.espnfc.us/major-league-soccer/match/437319/columbus-crew-sc-montreal-impact/report', 'http://www.espnfc.us/major-league-soccer/match/437321/fc-dallas-seattle-sounders-fc/report', 'http://www.espnfc.us/german-bundesliga/match/427020/borussia-dortmund-schalke-04/report', 'http://www.espnfc.us/german-bundesliga/match/427025/fc-augsburg-werder-bremen/report', 'http://www.espnfc.us/italian-serie-a/match/432155/torino-internazionale/report', 'http://www.espnfc.us/italian-serie-a/match/432157/as-roma-lazio/report', 'http://www.espnfc.us/italian-serie-a/match/432156/empoli-juventus/report', 'http://www.espnfc.us/italian-serie-a/match/432152/palermo-chievo-verona/report', 'http://www.espnfc.us/italian-serie-a/match/432151/sassuolo-carpi/report', 'http://www.espnfc.us/italian-serie-a/match/432158/napoli-udinese/report', 'http://www.espnfc.us/italian-serie-a/match/432153/sampdoria-fiorentina/report', 'http://www.espnfc.us/french-ligue-1/match/424620/marseille-nice/report', 'http://www.espnfc.us/french-ligue-1/match/424618/bordeaux-as-monaco/report', 'http://www.espnfc.us/french-ligue-1/match/424622/lyon-st-etienne/report', 'http://www.espnfc.us/english-fa-cup/match/437280/didcot-town-fc-exeter-city/report', 'http://www.espnfc.us/english-fa-cup/match/437272/aldershot-town-bradford-city/report', 'http://www.espnfc.us/english-fa-cup/match/437275/brackley-town-newport-county/report', 'http://www.espnfc.us/english-fa-cup/match/437273/bristol-rovers-chesham-united/report', 'http://www.espnfc.us/english-fa-cup/match/437278/fc-halifax-town-wycombe-wanderers/report', 'http://www.espnfc.us/english-fa-cup/match/437277/gainsborough-trinity-shrewsbury-town/report', 'http://www.espnfc.us/english-fa-cup/match/437279/maidstone-united-yeovil-town/report', 'http://www.espnfc.us/english-fa-cup/match/437274/whitehawk-fc-lincoln-city/report', 'http://www.espnfc.us/english-fa-cup/match/437271/port-vale-maidenhead-utd/report', 'http://www.espnfc.us/scottish-premiership/match/425247/ross-county-celtic/report']

games = [game.Game(url) for url in urls]

# Dataset for "Who won" question

dataset = []

for game in games:
    text = game.text
    answer = game.query_dict['Who won?']
    
    if answer == 'Draw':
        answer = game.home+' '+game.away
    for s in text:
        s = '#BEGIN# '+s+' #END#'
        words = s.split(' ')
        
        for i in range(1,len(words)-1):
            d = {}
            w_minus_1 = words[i-1]
            w_plus_1 = words[i+1]
            d['word_before_=_'+str(w_minus_1)] = 1
            d['word_after_=_'+str(w_plus_1)] = 1
            if words[i] in answer.split(' '):
                d['label'] = 1
            else:
                d['label'] = 0
            dataset.append(d)

df = pd.DataFrame(dataset)
df.fillna(0, inplace=True)

df.to_csv('dataset_who_won_urls_1108.csv')


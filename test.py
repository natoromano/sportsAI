
import game, dataset
import pickle, copy
import textUtil
import re

testUrl = ''

model = pickle.load(open('who_won_30.model','r'))
oldEntities = pickle.load(open('who_won_30.entities','r'))

entities = copy.deepcopy(oldEntities)

columns = pickle.load(open('who_won_30.columns','r'))
columns = columns[columns != 'label']
columns = columns[columns != 'word']

while testUrl != 'stop':
    print 'Url a tester? (stop pour quitter)'
    testUrl = raw_input()

    testGame = game.Game(testUrl)

    testSet = dataset.Dataset().fromHeader('who_won_30.columns')


    text = testGame.text

    query = 'Who won?'

    test = []

    for i,_ in enumerate(text):
        text[i], entities = textUtil.anonymize(text[i], entities)

    answer = testGame.query_dict[query]

    if answer == 'Draw':
        answer = testGame.home+' '+testGame.away

    inv_entities = {v: k for k,v in entities.items()}

    for s in text:
        s = '#BEGIN# '+s+' #END'
        words = s.split(' ')

        for i in range(1, len(words)-1):
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
            test.append(d)

    testSet.append(test, fill=True)

    words = testSet.getY(labelColumn='word')


    testing = testSet.df[columns]

    scores = []
    for i,r in enumerate(testing.iterrows()):
        entityNumber = int(words[i][3:])
        score = model.predict_log_proba(r[1])[0][1]
        scores.append((score, inv_entities[entityNumber]))

    scores.sort()

    print 'Reponse: ', answer, 'Top 3', [s[1] for s in scores][-3:]



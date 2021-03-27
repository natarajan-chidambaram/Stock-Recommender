from . import data
from . import utilities as util
from . import dbmanager as dbm
import json
import uuid
import datetime


def getMatchesFromAVSearchAPI(inputStr):
    url = util.getAPIURLBase('AlphaVantage')
    queryOptions = {'function':'SYMBOL_SEARCH','keywords':inputStr,'apikey':'PTEGOCHNAABHYBIL'}
    matchesResp = util.makeRESTCall('GET', url, urlParams = queryOptions )
    matchesJson = json.loads(matchesResp.text)
    matchesArray = matchesJson['bestMatches']
    stockSymbolsList = []
    for i in range(len(matchesArray)):
        matchElement = matchesArray[i]
        stockSymbolsList.append({'symbol':matchElement['1. symbol'],'name': matchElement['2. name'], 'score':matchElement['9. matchScore']})
        
    uuidStr = str(uuid.uuid4())
    
    persistInputRequest(inputStr, matchesResp.text, uuidStr)
    return stockSymbolsList, uuidStr

def persistInputRequest(inputStr, responseStr, uuidStr):
    dt = datetime.datetime.now()
    
    conn = dbm.createDBConn()
    cursor = conn.cursor()
    cursor.execute("insert into input_requests (id, inputstr, time, responsestr) values (%s, %s, %s, %s)", (uuidStr, inputStr, dt, responseStr))
    conn.commit()
    print('Committed input value')
    dbm.closeDBConnAndCursor(conn, cursor)

def getSourcesForNewsAPI():
    url = util.getAPIURLBase('NewsApi') + '/sources'
    headerOptions = {'X-Api-Key':util.getAPIKeysForServices('NewsApi')}
    
#     https://newsapi.org/v2/sources?apiKey=API_KEY
    sourceJson = util.makeRESTCall('GET', url, headers = headerOptions)
    print(sourceJson.url)
    print(sourceJson.text)
    sourceJsonArray = json.loads(sourceJson.text)['sources']
    sourceJsonList = []
    for i in range(len(sourceJsonArray)):
        sourceJsonElement = sourceJsonArray[i]
        sourceJsonList.append(sourceJsonElement['id'])
    return sourceJsonList


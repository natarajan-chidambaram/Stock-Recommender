from . import utilities as util
from . import data as dt
from . import dbmanager as dbm
from textblob import TextBlob
import datetime as dt
from datetime import timedelta
import json
import re
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot
import pandas as pd


def performTimeSeriesAnalysisAndPersistPredictions(stocksConfig, uuid):
    symbolName = stocksConfig['symbolName']
    functionType = stocksConfig['interval']
    dataType = stocksConfig['dataToUse']
    timeArray = []
    valueArray = []
#   dt.datetime.strptime(d,'%Y-%m-%d').date()
    conn, cursor = dbm.createDBConnWithCursor()
#   TimeSeries prediction to be performed through Prophet.
    cursor.execute('SELECT timestamp, value FROM stock_historical_data where function_type = %s and data_type = %s and symbol_name = %s order by timestamp desc', (functionType, dataType, symbolName))
    for record in cursor:
#         print(record[0] + '-' + record[1])
        timeArray.append(dt.datetime.strptime(record[0],'%Y-%m-%d').date())
        valueArray.append(record[1])
    
    m = Prophet()
    
    propFb = pd.DataFrame({'ds': timeArray,'y': valueArray})
    m.fit(propFb)
    future = m.make_future_dataframe(periods=1)
    future.tail()
    forecast = m.predict(future)
    temp = forecast[['ds', 'yhat']]
    
    print(temp.tail())
    cursor.execute("select timestamp from stock_historical_data where function_type = %s and data_type = %s and symbol_name = %s order by timestamp desc fetch first 1 rows only", (functionType, dataType, symbolName))
    
    for record in cursor:
        print(record[0])
        tempDate = dt.datetime.strptime(record[0],'%Y-%m-%d').date()
#         print(record[1])
        predictedDate = tempDate +timedelta(days=1) 
    
    print(temp[(temp.ds == predictedDate)])
    
    temp2 = temp[(temp.ds == predictedDate)]
    
    temp2dsStr = temp2['ds'].to_string(index=False)
    temp2yhatStr = temp2['yhat'].to_string( index=False)
    print(type(temp2dsStr))
    print(type(temp2yhatStr))
    
    cursor.execute("insert into stock_predicted_data(uuid, timestamp, value , function_type, data_type, symbol_name) values (%s, %s, %s, %s, %s, %s)", (uuid, temp2dsStr, temp2yhatStr, functionType, dataType, symbolName))
    
    conn.commit()
#   Must add dates, and then finally do the transformation to update the prediction in the input component table
    
    
    dbm.closeDBConnAndCursor(conn,cursor)

def retrievePersistAndAnalyzeFromStockApi(stocksConfig, uuid):
    functionType = stocksConfig['interval']
    interval = ''
    symbolName = stocksConfig['symbolName']
    dataType = stocksConfig['dataToUse']
    if "INTRADAY" in functionType: 
        functionType = 'TIME_SERIES_INTRADAY'
        interval = stocksConfig['interval'][-4:]
        outputsize = 'full'
    else:
        outputsize = verifyIfDataPresent(functionType, symbolName, dataType)
    
    
    if interval == '':
        queryParams = {'symbol':symbolName ,'function':functionType, 'apikey': util.getAPIKeysForServices('AlphaVantage'), 'outputsize':outputsize}
    else:
        queryParams = {'symbol':symbolName ,'function':functionType,'interval':interval, 'apikey': util.getAPIKeysForServices('AlphaVantage'), 'outputsize': outputsize}
    
    print(queryParams)
    
    stockData = util.makeRESTCall('GET', util.getAPIURLBase('AlphaVantage'), urlParams = queryParams)
#     print(stockData.text)
    persistStockData(json.loads(stockData.text), uuid, stocksConfig['interval'], symbolName,dataType)
    
    
    performTimeSeriesAnalysisAndPersistPredictions(stocksConfig, uuid)
    
    return stockData.text

def verifyIfDataPresent(functionType, symbolName, dataType):
    conn, cursor = dbm.createDBConnWithCursor()
    cursor.execute("SELECT * FROM stock_historical_data where function_type = %s and data_type = %s and symbol_name = %s", (functionType, dataType, symbolName))
    if(cursor.fetchone() == None):
        return 'full'
    else:
        return 'compact'
    dbm.closeDBConnAndCursor(conn,cursor)

def persistStockData(stockData, uuid, functionType, symbolName,dataType):
    conn, cursor = dbm.createDBConnWithCursor()
    cursor.execute("insert into stock_complete_response (uuid, stock_complete_response) values (%s, %s)", (uuid, json.dumps(stockData)))
    conn.commit()
    for child in stockData:
        if child != 'Meta Data':
            data = stockData[child]
            for time in data:
                
                internalData = data[time]
                for valuation in internalData:
                    if dataType == valuation[3:]:
                        value = internalData[valuation]
#                         print(value + '-' + time + '-' + dataType + '-' + functionType)
                        cursor.execute("insert into stock_historical_data(function_type, data_type, value, timestamp, symbol_name) values (%s, %s, %s, %s, %s)", (functionType, dataType, value, time, symbolName))
                        
                
                
    conn.commit()
    dbm.closeDBConnAndCursor(conn,cursor)

def retrievePersistAndAnalyzeFromNewsApi(newsConfig, uuid):
    queryParams = {'q':newsConfig['queryString'], 'from':newsConfig['fromDate'], 'to':newsConfig['toDate'], 'language':'en','sources': newsConfig['csvSources']}
    headerParam = {'X-Api-Key':util.getAPIKeysForServices('NewsApi')}
    newsData = util.makeRESTCall('GET', util.getAPIURLBase('NewsApi') + '/everything', headers = headerParam, urlParams = queryParams)
    print(queryParams)
    print(newsData.text)
    persistNewsData(json.loads(newsData.text), uuid)
    return newsData.text

def persistNewsData(newsData, uuid):
    conn, cursor = dbm.createDBConnWithCursor()
    articles = newsData['articles']
    cursor.execute("insert into news_complete (uuid, news_response_complete) values (%s, %s)", (uuid, json.dumps(newsData)))
#     conn.commit()
    for article in articles:
        cleanedText =  preprocessText(article['description'])
        sentimentValue = sentiAnalyse(cleanedText)
        url = article['url']
        cursor.execute("insert into news_individual(uuid, status_text_processed, sentiment_value, url) values (%s, %s, %s, %s)", (uuid, cleanedText, sentimentValue, url))
    conn.commit()
    dbm.closeDBConnAndCursor(conn,cursor)

def retrievePersistAndAnalyzeFromTwitter(twitterConfig, uuid):
    print(uuid)
    queryParams = {'q':twitterConfig['queryString'], 'lang' :'en', 'geocode': twitterConfig['geocode'], 'until':twitterConfig['until'], 'result_type':twitterConfig['resultType'], 'since_id':twitterConfig['fromID'], 'max_id':twitterConfig['toID']}
    headerParam = {'Authorization':util.getAPIKeysForServices('Twitter')}
    print(queryParams)
    tweetData = util.makeRESTCall('GET', util.getAPIURLBase('TwitterSearch'), headers = headerParam, urlParams =  queryParams)
    print(tweetData.text)
    tweetTextJson = json.loads(tweetData.text)
    
    persistTwitterData(tweetTextJson, uuid)
    return tweetTextJson


def persistTwitterData(tweetTextJSON, uuid):
    conn, cursor = dbm.createDBConnWithCursor()
    statuses = tweetTextJSON['statuses']
    cursor.execute("insert into tweet_complete (uuid, tweet_text) values (%s, %s)", (uuid, json.dumps(tweetTextJSON)))
#     conn.commit()
#     print('Committed input value')
    statuses = tweetTextJSON['statuses']
    for status in statuses:
        cleanedText = preprocessText(status['text'])
        sentimentValue = sentiAnalyse(cleanedText)
#         print(cleanedText)
#         print(sentimentValue)
        tweetID = status['id_str']
        cursor.execute("insert into tweet_individual(uuid, status_text_processed, sentiment_value, tweet_id) values (%s, %s, %s, %s)", (uuid, cleanedText, sentimentValue, tweetID))
    
    conn.commit()
    dbm.closeDBConnAndCursor(conn,cursor)

def preprocessText(inputText):
    filteredText = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", inputText).split())
    return filteredText
    
def sentiAnalyse(cleanedText):
    if(cleanedText != None):
        Sentiment = TextBlob(cleanedText)
        sentimentValue = Sentiment.sentiment.polarity
    else:
        sentimentValue = 0.0
    return sentimentValue

# def makeRESTCall(type, urlString, inputString = '', headers = {}, urlParams = {}):
#     '''
#     The POST input must be a string directly. The headers must be a JSON object, and the urlParams must not be in the URL string
#     '''
#     
#     if type == 'GET':
#         response = requests.get(urlString, headers = headers, params = urlParams)
#     elif type == 'POST':
#         response = requests.post(urlString, headers= headers, params = urlParams, data = inputString)
#     
#     if(response.status_code != 200):
#         response.raise_for_status()
#         
#     return response


def Alpha_Vantage(function,symbol,outputSize,interval):
    url = url_site('Alpha Vantage')
    if function == 'TIME_SERIES_INTRADAY':
        query = {'function':function,'symbol':symbol,'outputsize':outputSize,'interval':interval+'mins',
                 'apikey':'PTEGOCHNAABHYBIL'}
    else:
        query = {'function':function,'symbol':symbol,'outputsize':outputSize,'apikey':'PTEGOCHNAABHYBIL'}
    lData = dataExtractionWithQuery(url,query)
    return lData
    
    

def NewsApi(news_type,sources,company):
    url = url_site('NewsApi')
    urlSeek = url+news_type
    query = {'sources':sources,'q':company,'apiKey':'9ad90e41f4404cb7a510213dbe93875f'}
    lData = dataExtractionWithQuery(urlSeek,query)
    return lData.text
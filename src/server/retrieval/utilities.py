import requests
import json
import base64

def testFunction():
    return 1
    
def getAPIURLBase(website):
    if website == 'TwitterAuth':
        lUrl = 'https://api.twitter.com/oauth2/token?grant_type=client_credentials'
    elif website =='TwitterSearch':
        lUrl = 'https://api.twitter.com/1.1/search/tweets.json'
    elif website == 'AlphaVantage':
        lUrl = 'https://www.alphavantage.co/query'
#     elif website == 'Quandl':
#         lUrl = 'https://www.quandl.com/api/v3/datasets/WIKI/'
    elif website == 'NewsApi':
        lUrl = 'https://newsapi.org/v2/'
    else:
        raise Exception('API not yet supported')
    return lUrl
    
def makeRESTCall(type, urlString, inputString = '', headers = {}, urlParams = {}):
    '''
    The POST input must be a string directly. The headers must be a JSON object, and the urlParams must not be in the URL string
    '''
    
    if type == 'GET':
        response = requests.get(urlString, headers = headers, params = urlParams)
    elif type == 'POST':
        response = requests.post(urlString, headers= headers, params = urlParams, data = inputString)
    
#     if(response.status_code != 200):
#         response.raise_for_status()
        
    return response

def obtainNewTokenForTwitter():
    consumerKey = 'JYVaXXknmG4LPSQp1Eb9zRZFA'
    consumerSecret = '5AczNx86wwp5Tp3XOaZQy4UWcGvmBWcqZTbi9aJWTcVVJNZ5fd'
    concatStr = consumerKey + ':' + consumerSecret
    print(concatStr)
    print(str.encode(concatStr))
    encodeStr = base64.b64encode(str.encode(concatStr))
    print(encodeStr)
    header = {'Authorization':'Basic ' +encodeStr.decode()}
    print(encodeStr.decode())
    responseJSON = makeRESTCall('POST', getAPIURLBase('TwitterAuth'), headers = header)
    print(responseJSON.text)
    token = 'Bearer ' + json.loads(responseJSON.text)['access_token']
    return token
    
def getAPIKeysForServices(serviceName):
    apiKey = ''
    if serviceName == 'Twitter':
        apiKey = obtainNewTokenForTwitter()
    elif serviceName == 'AlphaVantage':
        apiKey = 'PTEGOCHNAABHYBIL'
    elif serviceName == 'NewsApi':
        apiKey = '9ad90e41f4404cb7a510213dbe93875f'
#         ea1c1ef857284d048eba5734ff4cffcf
    else:
        raise Exception('API not yet supported')
        
    return apiKey
    
# listOfTimeIntervalsForAlphaVantage = ['TIME_SERIES_INTRADAY_1MIN','TIME_SERIES_INTRADAY_5MIN','TIME_SERIES_INTRADAY_15MIN','TIME_SERIES_INTRADAY_30MIN','TIME_SERIES_INTRADAY_60MIN','TIME_SERIES_DAILY','TIME_SERIES_DAILY_ADJUSTED','TIME_SERIES_WEEKLY','TIME_SERIES_WEEKLY_ADJUSTED','TIME_SERIES_MONTHLY','TIME_SERIES_MONTHLY_ADJUSTED']
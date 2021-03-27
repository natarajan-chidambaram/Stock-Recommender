from apscheduler.schedulers.background import BackgroundScheduler
from . import dbmanager as dbm
from numpy import exp

def triggerFlowOfMachineLearningComponent(uuid):
    inputsInOrder = calculateValueOfInputElementsToMachineLearningEquation(uuid)
    inputsInOrder.append(1)
    weightsInOrder = retrieveWeightsFromDB()
    predictedLabel = calculatePredictedLabel(weightsInOrder, inputsInOrder)
#     triggerSchedulerToDetermineActualLabelAfterTimeInterval(predictedLabel)
    
    return predictedLabel

def calculateValueOfInputElementsToMachineLearningEquation(uuid):
    print(type(uuid))
    conn, cursor = dbm.createDBConnWithCursor()
    
    cursor.execute("select avg(cast(sentiment_value as float)) from tweet_individual where uuid = %s", (uuid,))
    tweetInp = 0.0
    
    for rec in cursor:
        tweetInp = rec[0]
    
    newsInp = 0.0
    
    cursor.execute("select avg(cast(sentiment_value as float)) from news_individual where uuid = %s", ( uuid,))
    for rec in cursor:
        newsInp = rec[0]
    
    stockInp = 0.0
    symbolName = ''
    
    cursor.execute("select symbol_name, value from stock_predicted_data where uuid = %s", (uuid,))
    for rec in cursor:
        symbolName = rec[0]
        stockPredValue = rec[1]
    
    cursor.execute("select value from stock_historical_data where symbol_name = %s order by timestamp desc fetch first 1 rows only  ", (symbolName,))
    for rec in cursor:
        stockLastTrueValue = rec[0]
        
    temp = float(stockPredValue)/ float(stockLastTrueValue)
    temp = temp - 1
    
    stockInp = temp
#     print(tweetInp + '-' + newsInp + '-' + stockInp)
    inputsInOrder = []
    inputsInOrder.append(tweetInp)
    inputsInOrder.append(newsInp)
    inputsInOrder.append(stockInp)
    
    
    dbm.closeDBConnAndCursor(conn,cursor)
    return inputsInOrder


def retrieveWeightsFromDB():
    conn, cursor = dbm.createDBConnWithCursor()
    cursor.execute("select value from system_params where type = 'weight' order by key")
    weightsInOrder = []
    for record in cursor:
        weightsInOrder.append(record[0])
    dbm.closeDBConnAndCursor(conn,cursor)
    print(weightsInOrder)
    return weightsInOrder


def calculatePredictedLabel(weightsInOrder, inputsInOrder):
    #all operations included, also sigmoid
    finalSum = 0
    
    for i in range(len(weightsInOrder)):
        finalSum += float(weightsInOrder[i]) * float(inputsInOrder[i])
    
    finalSum = (1  / (1 + exp(finalSum)))
    
    return finalSum


def triggerSchedulerToDetermineActualLabelAfterTimeInterval(predictedLabel, uuid):
    # Creating a scheduled process so that after current prediction, an appropriate amount of time
    # is waited and then the global weights are updated accordingly
    sched = Scheduler()
    sched.start()
    job = sched.add_date_job(lossCalculationWorkflow, '2013-08-05 23:47:05', [predictedLabel, uuid])
    return 0


def lossCalculationWorkflow(predictedLabel, uuid):
    # Triggering a sequence of steps towards verifying that the prediction works accurately and
     # triggering a weight update in the database.
    findDateCorrespondingToUUIDForVerification(uuid)
    
    triggerDataRetrievalWithSameParams(uuid)
    determineValueToVerifyAgainstPredictionWithUUIDinHistoricalTable()
    updateWeightsBasedOnCalculatedLoss()
    
    return 0

def findDateCorrespondingToUUIDForVerification(uuid):
    # Checking object data, find latest date
    return 0

def updateWeightsBasedOnCalculatedLoss():
    # Final updating weights to optimize further predictions
    return 0
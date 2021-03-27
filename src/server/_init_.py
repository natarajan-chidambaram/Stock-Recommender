from retrieval import data as dt
from retrieval import inputHandler as ih
from retrieval import retriever as retr
from flask import Flask, request
from flask_cors import CORS
import json
from retrieval import machinelearning
app = Flask(__name__)
CORS(app)




@app.route('/test/value/', methods=['GET'])
def testFunc():
    bar = request.args.to_dict()
    
    print("Test")
    print(dt.testFunction())
    print(bar)
    return 'success', 200


@app.route('/test/value/<string:task_id>', methods=['GET'])
def get_task(task_id):
    
    print("Reached")
    return task_id, 200


@app.route('/getSuggestions/<string:inputString>', methods=['GET'])
def getMatchesForInput(inputString):
    output, id = ih.getMatchesFromAVSearchAPI(inputString)
    outputWithID = {'id' : id, 'output' : output}
    
    print("Reached")
    return json.dumps(outputWithID), 200

@app.route('/setEntityParamsAndRetrieve/<string:uuid>', methods=['POST'])
def setEntityParamsAndRetrieve(uuid):
    print(uuid)
    print("Input to method")
    req_data = request.get_json()
#     print(json.dumps(req_data))
#     print(req_data['twitter'])
#     print(json.dumps(retr.retrieveFromTwitter(req_data['twitter'], uuid)))
#     print(json.dumps(retr.retrievePersistAndAnalyzeFromStockApi(req_data['stock'], uuid)))

    retr.retrievePersistAndAnalyzeFromTwitter(req_data['twitter'], uuid)
    
    retr.retrievePersistAndAnalyzeFromNewsApi(req_data['newsapi'], uuid)
    retr.retrievePersistAndAnalyzeFromStockApi(req_data['stock'], uuid)

#     print(req_data['stock'])
#     print(dt.testFunction())
#     print(bar)
    return 'success', 200



@app.route('/obtainRecommendationFromSystem/<string:uuid>', methods=['GET'])
def obtainRecommendationFromSystem(uuid):
#     bar = request.args.to_dict()
     
    predictedLabel = machinelearning.triggerFlowOfMachineLearningComponent(uuid)
#     print(bar)

    print(predictedLabel)
    return str(predictedLabel), 200
# 
# @app.route('/getNewsSamples/', methods=['GET'])
# def getNewsSamples():
#     bar = request.args.to_dict()
#     
#     print("Test")
#     print(dt.testFunction())
#     print(bar)
#     return 'success', 200
# 
# @app.route('/retrieveData/', methods=['GET'])
# def pullEntityDataIntoDatabase():
#     bar = request.args.to_dict()
#     
#     print("Test")
#     print(dt.testFunction())
#     print(bar)
#     return 'success', 200

@app.route('/getNewsSources/', methods=['GET'])
def getNewsSources():
    var = ih.getSourcesForNewsAPI()
    return json.dumps(var), 200

if __name__ == '__main__':   
    app.run(port='2312',debug=True)
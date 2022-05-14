from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

request_id = 0

def responseHandler(data):
    response = jsonify(data)
    response.statusCode = 200
    return response

@app.route("/", methods = ['GET'])
def getIndex():

    data = {
        "author": "Jan Pelicon",
        "date": "13.05.2022",
        "API-description": "A design gallery for transfer functions.\
        Handles volume feature vectors in order to generate a set of good transfer functions from which user picks one and optionaly epxlores further",
        "routes": [
            {
                "name": "/",
                "method": "GET",
                "description": "Index page and information about API."
            },
            {
                "name": "/generate-tf",
                "method": "POST",
                "description": "user posts volume feature vector - server generates 9 transfer functions"
            },
            {
                "name": "/explore-tf",
                "method": "POST",
                "description": "user posts transfer function - server generates new transfer functions that are similar to the recieved one"
            }     
        ]}

    return responseHandler(data)

@app.route("/generate-tf", methods = ['POST'])
@cross_origin()
def postGenerateTF():

    print(request.data)

    data = {
        "transfer_functions": [
            {"name": "tf1", "value": "feature-tf"}, 
            {"name": "tf2", "value": "feature-tf"},
            {"name": "tf3", "value": "feature-tf"}, 
            {"name": "tf4", "value": "feature-tf"},
            {"name": "tf5", "value": "feature-tf"}, 
            {"name": "tf6", "value": "feature-tf"},
            {"name": "tf7", "value": "feature-tf"}, 
            {"name": "tf8", "value": "feature-tf"},
            {"name": "tf9", "value": "feature-tf"}
        ]
    }

    return responseHandler(data)

@app.route("/explore-tf", methods = ['POST'])
@cross_origin()
def postExploreTF():

    print(request.data)

    data = {"transfer_functions": [
        {"name": "tf1", "value": "explore-tf"}, 
        {"name": "tf2", "value": "explore-tf"},
        {"name": "tf3", "value": "explore-tf"}, 
        {"name": "tf4", "value": "explore-tf"},
        {"name": "tf5", "value": "explore-tf"}, 
        {"name": "tf6", "value": "explore-tf"},
        {"name": "tf7", "value": "explore-tf"}, 
        {"name": "tf8", "value": "explore-tf"},
        {"name": "tf9", "value": "explore-tf"}]
        }

    return responseHandler(data)

@app.route("/generate-random-tf", methods = ['GET'])
@cross_origin()
def postGenerateRandomTF():

    print(request.data)

    data = {
        "transfer_functions": [
            {"name": "tf1", "value": "random-tf"}, 
            {"name": "tf2", "value": "random-tf"},
            {"name": "tf3", "value": "random-tf"}, 
            {"name": "tf4", "value": "random-tf"},
            {"name": "tf5", "value": "random-tf"}, 
            {"name": "tf6", "value": "random-tf"},
            {"name": "tf7", "value": "random-tf"}, 
            {"name": "tf8", "value": "random-tf"},
            {"name": "tf9", "value": "random-tf"}
        ]
    }

    return responseHandler(data)

if __name__ == "__main__":
    app.run(debug=True)
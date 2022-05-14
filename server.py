from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from transferFunctionGenerator import TransferFunctionGenerator

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def responseHandler(data):
    response = jsonify(data)
    response.statusCode = 200
    return response

@app.route("/explore-tf", methods = ['POST'])
@cross_origin()
def postExploreTF():

    return responseHandler(data)

@app.route("/random-tf", methods = ['GET'])
@cross_origin()
def postGenerateRandomTF():
    TFG = TransferFunctionGenerator()
    data = TFG.generateInitialTransferFunctions()
    return responseHandler(data)

@app.route("/", methods = ['GET'])
def getIndex():
    data = {
        "author": "Jan Pelicon",
        "mentor": "Žiga Lesar",
        "API-description": "A tool for creating a random transfer functions",
        "routes": [
            {
                "name": "/",
                "method": "GET",
                "description": "Information about tool and routes."
            },
            {
                "name": "/random-tf",
                "method": "GET",
                "description": "Returns 9 random transfer functions which have unique feature vectors."
            },
            {
                "name": "/explore-tf",
                "method": "POST",
                "data": "feature vector consisting of: bins (3-30), dropout probability (0.0-0.3), polynomial power (2, 4, 6, 8, 10).",
                "description": "Given 1 feature vector returns 8 other random transfer functions that are near in feature space."
            }     
        ]}
    return responseHandler(data)

if __name__ == "__main__":
    app.run(debug=True)
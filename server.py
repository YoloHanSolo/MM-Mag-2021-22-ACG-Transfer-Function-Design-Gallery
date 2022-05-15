import json
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS, cross_origin
from transferFunctionGenerator import TransferFunctionGenerator

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def responseHandler(data):
    response = jsonify(data)
    response.statusCode = 200
    return response

def parsePostData(data):
    return json.loads(data.decode())

@app.route("/explore-tf", methods = ['POST'])
@cross_origin()
def postExploreTF():
    data = parsePostData(request.data)
    filename = data["filename"]
    feature_vector = data["feature_vector"]
    TFG = TransferFunctionGenerator(filename)
    data = TFG.exploreTransferFunctions(feature_vector)
    TFG.generateTransferFunctionsPreview(data)
    return responseHandler(data)

@app.route("/random-tf", methods = ['POST'])
@cross_origin()
def postRandomTF():
    data = parsePostData(request.data)
    filename = data["filename"]
    TFG = TransferFunctionGenerator(filename)
    data = TFG.generateInitialTransferFunctions()
    TFG.generateTransferFunctionsPreview(data)
    return responseHandler(data)

@app.route("/preview-tf/<index>", methods = ['GET'])
@cross_origin()
def getPreviewTF(index):
    return send_file("temp/tf" + index + "_preview.png", mimetype='image/png')

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
                "method": "POST",
                "data": "dataset filename",
                "description": "Returns 9 random transfer functions with previews that have unique feature vectors."
            },
            {
                "name": "/explore-tf",
                "method": "POST",
                "data": "dataset filename, feature vector consisting of: bins (3-30), dropout probability (0.0-0.3), polynomial power (2, 4, 6, 8, 10).",
                "description": "Given 1 feature vector returns 8 other random transfer functions that are near in feature space."
            }     
        ]}
    return responseHandler(data)

if __name__ == "__main__":
    app.run(debug=True)
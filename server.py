from flask import Flask, redirect, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def index():
  return redirect("/transfer-function", code=302)

@app.route("/transfer-function")
@cross_origin()
def getTransferFunctions():
    data = {"transfer_functions": [
        {"name": "tf1", "value": "tf1-new"}, 
        {"name": "tf2", "value": "tf2-new"},
        {"name": "tf3", "value": "tf3-new"}, 
        {"name": "tf4", "value": "tf4-new"},
        {"name": "tf5", "value": "tf5-new"}, 
        {"name": "tf6", "value": "tf6-new"},
        {"name": "tf7", "value": "tf7-new"}, 
        {"name": "tf8", "value": "tf8-new"},
        {"name": "tf9", "value": "tf9-new"}]}

    response = jsonify(data)
    response.status_code = 200
    return response




if __name__ == "__main__":
    app.run(debug=True)
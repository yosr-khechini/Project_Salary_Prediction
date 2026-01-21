#Imports
from flask import Flask, render_template, request
import requests
from flask_bootstrap import Bootstrap
app = Flask(__name__, static_folder='static')
#bootstrap initialization
bootstrap = Bootstrap(app)
#routing
@app.route("/")
@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template("home.html")
@app.route("/history")
@app.route("/history/")
def history():
    return render_template("history.html")
@app.route("/predict/", methods=["POST", "GET"])
@app.route("/predict", methods=["POST", "GET"])
def predict():
    return render_template("predict.html")

@app.route("/test")
def test():
    return "<h1>Test route works!</h1>"

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request, jsonify
import Lemming
app = Flask(__name__)

lemming = Lemming.LemmingService()

@app.route("/")
def hello_world():
    return "<p>Hello, Welcome to LEMMING 0.1</p>"

@app.post("/generate_sentences")
def generate_sentences_api():
    data = request.get_json()
    result = lemming.generate_sentences(data["words"])
    return {
        "outputs": result,
    }

@app.post("/echo")
def echo_api():
    words = request.get_json()["words"]
    print(words)
    return jsonify({
        "outputs": words,
    })
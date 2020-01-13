from flask import Flask
app = Flask(__name__)
from flask import request
from dao.db import init_db

@app.route('/')
def hello_world():
    return 'Hello, Benny!'

@app.route('/api/v0/trainfromscratch', methods=['POST'])
def train_from_scratch():
    return 'Train from Scratch'

@app.route('/api/v0/finetune', methods=['POST'])
def fine_tune():
    return 'Fine Tune'

if __name__ == "__main__":
    init_db('116.56.138.220', 'root', 'root', 'neurolearn')
    app.run(host='0.0.0.0', port=80, debug=True)
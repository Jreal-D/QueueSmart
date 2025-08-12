import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        'message': 'Hello world, welcome to Railway!',
        'service': 'QueueSmart API',
        'status': 'running'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'OK'})

# Don't include if __name__ == '__main__' block for Railway

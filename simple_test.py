from flask import Flask, jsonify
import os

print("=== STARTING ON PORT 5 ===")

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'service': 'QueueSmart Simple Test',
        'status': 'running',
        'message': 'Flask running on port 5!',
        'port': 5
    })

@app.route('/health')
def health():
    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    print("Starting Flask on port 5...")
    app.run(host='0.0.0.0', port=5, debug=False)

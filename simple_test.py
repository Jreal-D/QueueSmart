from flask import Flask, jsonify
import os

print("Starting simple Flask test...")

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'service': 'QueueSmart Simple Test',
        'status': 'running',
        'message': 'Basic Flask is working on Railway!'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    print("Simple test starting...")
    port = int(os.environ.get("PORT", 5000))
    print(f"Port: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

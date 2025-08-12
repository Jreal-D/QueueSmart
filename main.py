# main.py
print("QueueSmart Development Environment Ready!")
import pandas as pd
import numpy as np
print("All libraries imported successfully!")

# Import and run the Flask app
from api.app import app
import os

if __name__ == '__main__':
    print("Starting QueueSmart API...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

from flask import Flask
from flask_cors import CORS
from routes import register_routes

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Allow frontend requests

# Register routes from routes.py
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

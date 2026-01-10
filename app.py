from flask import Flask, jsonify
from flask_cors import CORS
from routes.npc import npc_bp
from utils.logger import setup_logging
import os

setup_logging()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB for audio uploads

# CORS
frontend_origin = os.getenv('FRONTEND_ORIGIN', '*')
CORS(app, origins=frontend_origin)

# Register blueprints
app.register_blueprint(npc_bp, url_prefix='/api/npc')

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/data')
def data():
    return jsonify({"message": "Hello from backend"})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
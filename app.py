from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/data')
def data():
    return jsonify({"message": "Hello from backend"})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
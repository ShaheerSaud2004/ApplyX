from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Test server is running'})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Test endpoint working'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    print(f"Starting test server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port) 
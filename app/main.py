from flask import Flask, jsonify, request, redirect, url_for, abort
from app.utils import generate_short_code, is_valid_url
from app.models import URLMapping
import threading

app = Flask(__name__)

url_store = {}
store_lock = threading.Lock()

@app.route('/')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "URL Shortener API"
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        "status": "ok",
        "message": "URL Shortener API is running"
    })

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    long_url = data['url']

    if not is_valid_url(long_url):
        return jsonify({"error": "Invalid URL provided"}), 400

    with store_lock:
        for short_code_in_store, mapping_obj in url_store.items():
            if mapping_obj.original_url == long_url:
                return jsonify({
                    "short_code": short_code_in_store,
                    "short_url": f"http://localhost:5000/{short_code_in_store}"
                }), 200

        short_code = generate_short_code()
        while short_code in url_store:
            short_code = generate_short_code()

        url_mapping = URLMapping(original_url=long_url, short_code=short_code)
        url_store[short_code] = url_mapping

        return jsonify({
            "short_code": short_code,
            "short_url": f"http://localhost:5000/{short_code}"
        }), 201

@app.route('/<short_code>', methods=['GET'])
def redirect_to_long_url(short_code):
    with store_lock:
        url_mapping = url_store.get(short_code)

        if not url_mapping:
            abort(404)

        url_mapping.clicks += 1
        return redirect(url_mapping.original_url)

@app.route('/api/stats/<short_code>', methods=['GET'])
def get_url_stats(short_code):
    with store_lock:
        url_mapping = url_store.get(short_code)

        if not url_mapping:
            abort(404)

        return jsonify({
            "url": url_mapping.original_url,
            "clicks": url_mapping.clicks,
            "created_at": url_mapping.created_at
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

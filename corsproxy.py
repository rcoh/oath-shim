from flask import Flask, render_template, request, jsonify, redirect
import requests
import random
from urlparse import urlparse
app = Flask(__name__)

@app.route("/corsproxy", methods=['GET', 'OPTIONS'])
def proxy():
    url = request.args.get('url')
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = request.headers['Access-Control-Request-Headers']
    else:
        proxied_request = requests.get(url, headers = request.headers)
        response = jsonify(proxied_request.json())
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

if __name__ == "__main__":
    app.debug = True
    app.run(port = 5002)

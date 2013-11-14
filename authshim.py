from flask import Flask, render_template, request, jsonify, redirect
import requests
import random
from urlparse import urlparse
app = Flask(__name__)

from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('server.key')
context.use_certificate_file('server.crt')

CLIENT_ID = "5fmnuoxq79novlted3hvo7jcc51a5zi6"
CLIENT_SECRET = "waPXTZ4x1BI2C9PPGGNQ9D6cOWcIyiWn"

CLIENTS = {
    CLIENT_ID: {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "allowed_redirects": ["http://www.testapp.com:5001/"],
        "service": "box"
    }
}

STATE_CACHE = {}

SERVICES = {
        "box": {
            "url": "https://www.box.com/api/oauth2/authorize",
            "params": {"response_type": "code"}
        }
}

@app.route("/debug")
def hello():
    return render_template('hello.html', redir_url = "https://inklocal.com:5000/authed", client_id =
            CLIENT_ID)

@app.route("/oauth2/<servicename>/auth")
def do_auth(servicename):
    client_id = request.args.get('client_id')
    final_redirect_uri = request.args.get('redirect_uri')
    # TODO handle lack of client_id
    client_info = CLIENTS.get(client_id)
    if not client_info:
        return "no client", 500
    # verify redirect
    # TODO more flexibility
    if not final_redirect_uri in client_info['allowed_redirects']:
        return "bad redirect", 500

    service_obj = SERVICES[client_info['service']]
    redirect_uri = service_obj["url"]

    # lol fix
    state = str(random.randint(0, 10000))
    STATE_CACHE[state] = {
            "reply_state": request.args.get('state'),
            "redirect_uri": final_redirect_uri,
            "client": client_info
    }


    params = {
            "redirect_uri": "https://www.authshim.com:5000/redirect",
            "client_id": client_id,
            "state": state
    }
    params.update(service_obj['params'])

    return redirect(add_params(redirect_uri, params))

    
def add_params(url, params):
    import urllib
    import urlparse
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urllib.urlencode(query)

    return urlparse.urlunparse(url_parts)
    

@app.route("/redirect")
def redir():
    incoming_state = request.args.get('state')
    state = STATE_CACHE[incoming_state]
    client = state['client']
    if client["service"] == "box":
        token = doauth_box(state['client'])
    # LOL should return everything
    return redirect(state["redirect_uri"] + "#access_token=" + token)

def doauth_box(client):
    params = {
        "grant_type": "authorization_code", 
        "code":  request.args.get('code', ''),
        "client_id": client['client_id'],
        "client_secret": client['client_secret']
    }
    resp = requests.post("https://www.box.com/api/oauth2/token", data = params)
    json_res = resp.json()
    access_token = json_res['access_token']
    return access_token


if __name__ == "__main__":
    app.debug = True
    app.run(ssl_context = context)

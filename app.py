from flask import Flask, redirect, url_for, render_template, request, jsonify
from flask_dance.contrib.twitch import make_twitch_blueprint, twitch
from dotenv import load_dotenv
import os
import requests
from oauthlib.oauth2.rfc6749.errors import MissingTokenError
from create_logger import create
from flask_cors import CORS, cross_origin
from datetime import timedelta


load_dotenv()
os.environ['FLASK_ENV'] = 'testing'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


logger = create()

app = Flask(__name__)

# CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}}, methods=["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"])
# @app.after_request
# def add_cors_headers(response):
#     response.headers['Access-Control-Allow-Origin'] = 'http://localhost:63343'
#     response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
#     response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
#     response.headers['Access-Control-Allow-Credentials'] = 'true'
#     return response
#
app.secret_key = os.getenv("SECRET_KEY")
app.config['TWITCH_OAUTH_CLIENT_ID'] = os.getenv("TWITCH_CLIENT_ID")
app.config['TWITCH_OAUTH_CLIENT_SECRET'] = os.getenv("TWITCH_CLIENT_SECRET")
# app.config['SESSION_PERMANENT'] = False
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # adjust the value as per your need
#
twitch_blueprint = make_twitch_blueprint(
     scope=["user:read:email", "user:read:follows"], redirect_to="oauth_done"
 )
app.register_blueprint(twitch_blueprint)


@app.route('/')
def index():
    try:
        if twitch.authorized:
            resp = twitch.get("user")  # make an API call
            if resp.status_code == 200:
                # API call was successful, so the token is valid
                return redirect(url_for("fetch_data"))
    except MissingTokenError:
        return redirect(url_for("twitch.login"))

    return redirect(url_for("twitch.login"))

@app.route('/is_authenticated')
def is_authenticated():
    if twitch.authorized:
        return jsonify(authorized=True)
    else:
        return jsonify(authorized=False)

@app.route('/oauth_done')
def oauth_done():
    return render_template('index.html')

@app.route('/fetch_data')
def fetch_data():
    if twitch.authorized:
        try:
            username, email, user_id = get_user_info(twitch)
            streamer_names = get_followed_streamers(twitch, user_id)

            # create a dictionary to hold your data
            data = {
                "username": username,
                "email": email,
                "streamer_names": streamer_names,
            }

            # use jsonify to return your data as a JSON response
            return jsonify(data)
        except Exception as e:
            logger.debug(e)
            return jsonify(error=str(e))  # return the error message as JSON
    else:
        return redirect(url_for("index"))

def get_user_info(twitch):
    headers = {
        "Authorization": f"Bearer {twitch.access_token}",
        "Client-ID": app.config['TWITCH_OAUTH_CLIENT_ID']
    }
    user_data_url = "https://api.twitch.tv/helix/users/"
    resp = requests.get(user_data_url, headers=headers)
    if resp.ok:
        resp = resp.json()
        display_name = resp["data"][0]["display_name"]
        email = resp["data"][0]["email"]
        user_id = resp["data"][0]["id"]
        return display_name, email, user_id
    else:
        logger.debug(resp.status_code)
        return []


def get_followed_streamers(twitch, user_id):
    headers = {
        "Authorization": f"Bearer {twitch.access_token}",
        "Client-ID": app.config['TWITCH_OAUTH_CLIENT_ID']
    }

    followed_streamers_url = f'https://api.twitch.tv/helix/channels/followed?user_id={user_id}'
    resp = requests.get(followed_streamers_url, headers=headers)
    if resp.ok:
        resp = resp.json()
        streamer_names = []
        for item in resp['data']:
            streamer_names.append(item['broadcaster_name'])
        return streamer_names
    else:
        logger.debug(resp)
        return []



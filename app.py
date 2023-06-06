from flask import Flask, redirect, url_for, flash, render_template, request
from flask import session
from flask_dance.contrib.twitch import make_twitch_blueprint, twitch
from dotenv import load_dotenv
import os
import requests
from oauthlib.oauth2.rfc6749.errors import MissingTokenError
from create_logger import create

load_dotenv()
os.environ['FLASK_ENV'] = 'testing'



logger = create()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['TWITCH_OAUTH_CLIENT_ID'] = os.getenv("TWITCH_CLIENT_ID")
app.config['TWITCH_OAUTH_CLIENT_SECRET'] = os.getenv("TWITCH_CLIENT_SECRET")

twitch_blueprint = make_twitch_blueprint(
    scope=["user:read:email", "user:read:follows"], redirect_to="dashboard"
)
app.register_blueprint(twitch_blueprint)


@app.route('/')
def index():
    logger.debug("You are in index.")
    try:
        if twitch.authorized:
            resp = twitch.get("user")  # make an API call
            if resp.status_code == 200:
                # API call was successful, so the token is valid
                return redirect(url_for("dashboard"))
    except MissingTokenError:
        return redirect(url_for("twitch.login"))

    return redirect(url_for("twitch.login"))


@app.route('/dashboard')
def dashboard():
    if twitch.authorized:
        try:
            username, email, user_id = get_user_info(twitch)
            streamer_names = get_followed_streamers(twitch, user_id)

            return render_template("dashboard.html", username=username, email=email,
                                   streamer_names=streamer_names)
        except Exception as e:
            logger.debug(e)
            return []
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

def get_cookies():
    cookies = request.cookies
    return f"Cookies: {cookies}"


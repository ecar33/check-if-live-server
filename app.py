from flask import Flask, redirect, url_for, flash
from flask_dance.contrib.twitch import make_twitch_blueprint, twitch
from flask_dance.consumer import oauth_authorized
from dotenv import load_dotenv
import os

load_dotenv()

#Change this in prod
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['TWITCH_OAUTH_CLIENT_ID'] = os.getenv("TWITCH_CLIENT_ID")
app.config['TWITCH_OAUTH_CLIENT_SECRET'] = os.getenv("TWITCH_CLIENT_SECRET")

twitch_blueprint = make_twitch_blueprint(scope=["user:read:email", "user:read:follows"])
app.register_blueprint(twitch_blueprint, url_prefix="/login")

@app.route('/')
def index():
    if not twitch.authorized:
        return redirect(url_for("twitch.login"))
    else:
        return "You are logged in!"

@oauth_authorized.connect_via(twitch_blueprint)
def twitch_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Twitch.", category="error")
        return False

    # Optionally, you could do something with the token here, such as storing it
    # in your database for later use.

    flash("Successfully logged in with Twitch!")
from flask import Flask, redirect, url_for, flash
from flask import session
from flask_dance.contrib.twitch import make_twitch_blueprint, twitch
from dotenv import load_dotenv
import os
import logging
import requests

load_dotenv()
os.environ['FLASK_ENV'] = 'testing'
#logging.basicConfig(level=logging.WARNING)


# Create a logger
logger = logging.getLogger('my_logger')

# Set the level of this logger to DEBUG. This means it will handle messages of severity DEBUG and above.
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler('my_log_file.log')

# Set the level of the file handler to DEBUG. This means it will handle messages of severity DEBUG and above.
file_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the formatter to the file handler
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

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
    if twitch.authorized:
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("twitch.login"))


@app.route('/twitch/authorized')
def twitch_callback():
    logger.debug("You reached callback")
    response = twitch.authorized_response()
    if response is None or response.get('access_token') is None:
        print("Response_failed")
        logger.debug('Failed to log in: %s', response)
        flash("Failed to log in.", category="error")
        return redirect(url_for("index"))


    logger.debug('Logged in successfully: %s', response)
    # Save the user's logged-in state to their session here
    session['logged_in'] = True
    session['access_token'] = response.get('access_token')
    return redirect(url_for("dashboard"))

@app.route('/dashboard')
def dashboard():
    if twitch.authorized:
        headers = {
            "Authorization": f"OAuth {twitch.access_token}"
        }
        response = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers)
        logger.debug(response.text)
        if response.status_code == 200:
            # Token is valid
            headers = {
                "Authorization": f"Bearer {twitch.access_token}",
                "Client-ID": app.config['TWITCH_OAUTH_CLIENT_ID']
            }
            user_data_url = "https://api.twitch.tv/helix/users/"
            resp = requests.get(user_data_url, headers=headers)
            if resp.ok:
                return resp.json()
            else:
                logger.debug(resp.status_code)
                return "Something went wrong"
        else:
            # Token is invalid or expired
            logger.debug(response.status_code)
            return redirect(url_for("twitch.login"))
    else:
        return redirect(url_for("index"))


if __name__ == '__main__':
    app.run()
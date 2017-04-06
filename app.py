import datastore
import os
import requests

from flask import Flask, request, session, redirect, url_for, render_template
from flask_oauth import OAuth

app = Flask(__name__)

# Import app settings from a configuration file.
# Execute with app.py with APP_SETTINGS=path/to/config
# Sample config file included in app.cfg.sample
app.config.from_envvar('APP_SETTINGS')

# Flask-OAuth library to easily connect to Twitter via OAuth.
twitter = OAuth().remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET']
)

@app.route('/')
def show_index():
    """Displays the landing page for the reference app."""
    auth_error = request.args.get('auth_error')
    yext_auth_url = get_yext_auth_url()
    return render_template('index.html',
        yext_auth_url=yext_auth_url,
        auth_error=auth_error)

@app.route('/yext_auth_callback')
def handle_yext_auth_callback():
    """Handles the Yext OAuth2 callback.

    Contains an authorization code if the resource owner authorizes app access.
    Contains an error message if the resource owner denies app access.
    """
    auth_code = request.args.get('code')
    error = request.args.get('error')
    error_description = request.args.get('error_description')

    if error:
        # Redirect user to landing page with error if authorization fails.
        return render_template('auth_callback.html',
            redirect=url_for('show_index', auth_error=error_description))

    try:
        yext_account_id, yext_access_token = exchange_yext_auth_code(auth_code)
    except:
        return render_template('auth_callback.html',
            redirect=url_for(
                'show_index',
                auth_error='Unable to link to Yext'))

    # Save user's Yext account information.
    session['yext_account_id'] = yext_account_id
    datastore.save_yext_access_token(yext_account_id, yext_access_token)

    # Redirect user to Twitter OAuth flow.
    callback_url = url_for('handle_twitter_auth_callback', _external=True)
    return twitter.authorize(callback=callback_url)

@app.route('/twitter_auth_callback')
@twitter.authorized_handler
def handle_twitter_auth_callback(resp):
    """Handles the Twitter OAuth callback."""
    if resp is None:
        # Redirect user to landing page with error if authorization fails.
        return render_template('auth_callback.html',
            redirect=url_for(
                'show_index',
                auth_error='You denied the request to sign in to Twitter'))

    # Save user's Twitter account information.
    twitter_token = resp['oauth_token']
    twitter_token_secret = resp['oauth_token_secret']
    datastore.save_twitter_oauth_token(
        session['yext_account_id'], twitter_token)
    datastore.save_twitter_oauth_token_secret(
        twitter_token, twitter_token_secret)

    return render_template('auth_callback.html',
        redirect=url_for('show_confirmation'))

@app.route('/confirmation')
def show_confirmation():
    """Displays the installation confirmation page."""
    return render_template('confirmation.html')

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handles location webhook events.

    Posts a Twitter message indicating that a location was updated in Yext.
    """
    webhook_json = request.get_json()
    yext_account_id = webhook_json['meta']['appSpecificAccountId']
    name = webhook_json['location']['locationName']
    twitter_access_token = datastore.get_twitter_oauth_token(yext_account_id)
    r = twitter.post('statuses/update.json',
        data={
            'status': '%s has changed their location data on Yext!' % (name)
        },
        token=twitter_access_token)
    return 'Twitter Response: %s' % (r.data)

def get_yext_auth_url():
    """Returns URL to Yext authorization page to start OAuth2 flow."""
    redirect_uri = get_yext_redirect_uri()
    return 'https://www.yext.com/oauth2/authorize?' \
        'client_id=%s' \
        '&response_type=code' \
        '&redirect_uri=%s' % (app.config['YEXT_CLIENT_ID'], redirect_uri)

def get_yext_redirect_uri():
    """Returns URL to the app's Yext authorization redirect endpoint"""
    return url_for('handle_yext_auth_callback', _external=True)

def exchange_yext_auth_code(auth_code):
    """Exchanges Yext authorization code for Yext access token

    Returns an identifier and access token for the account that authorized with
    the app.
    """
    request_body = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': get_yext_redirect_uri(),
        'client_id': app.config['YEXT_CLIENT_ID'],
        'client_secret': app.config['YEXT_API_KEY']
    }
    response = requests.post('https://api.yext.com/oauth2/accesstoken',
        data=request_body)
    
    response_json = response.json()
    yext_account_id = response_json['appSpecificAccountId']
    yext_access_token = response_json['access_token']
    return yext_account_id, yext_access_token

@twitter.tokengetter
def get_twitter_token(token=None):
    """Returns Twitter OAuth token and secret

    This function is required to make requests using the Flask-OAuth library.
    """
    token_secret = datastore.get_twitter_oauth_token_secret(token)
    if token_secret:
        return (token, token_secret)
    else:
        return None

if __name__ == '__main__':
    app.run()

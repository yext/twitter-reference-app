"""An in-memory datastore for Yext and Twitter OAuth tokens

Note: In practice, these tokens would be persisted in a database or similar.
"""

YEXT_ACCESS_TOKENS = dict()
TWITTER_OAUTH_TOKENS = dict()
TWITTER_OAUTH_TOKEN_SECRETS = dict()

def save_yext_access_token(yext_account_id, yext_access_token):
    """Saves the access token for the user's Yext account."""
    YEXT_ACCESS_TOKENS[yext_account_id] = yext_access_token

def save_twitter_oauth_token(yext_account_id, twitter_oauth_token):
    """Saves the Twitter OAuth token for the user's Yext account."""
    TWITTER_OAUTH_TOKENS[yext_account_id] = twitter_oauth_token

def save_twitter_oauth_token_secret(twitter_token, twitter_token_secret):
    """Saves the Twitter OAuth token secret for the user's Twitter account."""
    TWITTER_OAUTH_TOKEN_SECRETS[twitter_token] = twitter_token_secret

def get_yext_access_token(yext_account_id):
    """Retrieves the access token given a Yext account identifier."""
    if yext_account_id in YEXT_ACCESS_TOKENS:
        return YEXT_ACCESS_TOKENS[yext_account_id]

def get_twitter_oauth_token_secret(twitter_token):
    """Retrieves the Twitter OAuth token secret given a Twitter OAuth token."""
    if twitter_token in TWITTER_OAUTH_TOKEN_SECRETS:
        return TWITTER_OAUTH_TOKEN_SECRETS[twitter_token]

def get_twitter_oauth_token(yext_account_id):
    """Retrieves the Twitter OAuth token given a Yext account identifier."""
    if yext_account_id in TWITTER_OAUTH_TOKENS:
        return TWITTER_OAUTH_TOKENS[yext_account_id]
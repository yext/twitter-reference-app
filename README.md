# twitter-reference-app
Reference app that posts to Twitter when a Yext location updates.

## Prerequisites
1. [Create a Yext developer account and add an app.](http://developer.yext.com/docs/guides/get-started/)
2. [Create a Twitter developer account and add an app.](https://apps.twitter.com/)

## Setup
1. Clone this repository.

```
git clone https://github.com/yext/twitter-reference-app.git
```

2. Install Python requirements using pip. Using a Python environment tool like [virtualenv](https://virtualenv.pypa.io/) is recommended.

```
virtualenv /path/to/env
/path/to/env/bin/pip install -r requirements.txt
```

3. Create a configuration file containing Yext and Twitter credentials. See app.cfg.sample for reference.
4. Run the app.

```
APP_SETTINGS=/path/to/config /path/to/env/bin/python app.py
```

5. Navigate to http://127.0.0.1:5000/ to view app.

Note: To successfully go through the OAuth flow, the Yext OAuth redirect domain and Twitter OAuth redirect URI must both be set to point to your app.

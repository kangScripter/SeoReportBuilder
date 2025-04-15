# core/auth.py
from flask import Blueprint, session, redirect, url_for, request
import google_auth_oauthlib.flow
import google.oauth2.credentials
from google.auth.transport.requests import Request
import requests
from .utils import credentials_to_dict, check_granted_scopes
from .logger import logger
import os

SCOPES = [
    'https://www.googleapis.com/auth/webmasters.readonly']
CLIENT_SECRETS_FILE = "client_secrets.json"

auth_bp = Blueprint('auth', __name__)

def get_credentials():
    """Get and validate credentials from the session."""
    if 'credentials' not in session:
        return None
    logger.info(session['credentials'])
    try:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                session['credentials'] = credentials_to_dict(credentials)
        return credentials
    except Exception as e:
        print(f"Error getting credentials: {str(e)}")
        return None

@auth_bp.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = os.getenv("REDIRECT_URI")
    logger.info(flow.redirect_uri)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state
    return redirect(authorization_url)


@auth_bp.route('/oauth2callback')
def oauth2callback():
    if "state" in session:
        state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = os.getenv("REDIRECT_URI")

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    session['credentials'] = credentials_to_dict(credentials)
    session['features'] = check_granted_scopes(session['credentials'])

    return redirect('/')


@auth_bp.route('/logout')
def logout():
    """Logout the user by clearing the session."""
    session.clear()
    return redirect("/")


@auth_bp.route('/revoke')
def revoke():
    if 'credentials' not in session:
        return 'You need to <a href="/authorize">authorize</a> first.'

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    revoke = requests.post(
        'https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        headers={'content-type': 'application/x-www-form-urlencoded'})

    if revoke.status_code == 200:
        return 'Credentials successfully revoked.'
    else:
        return 'An error occurred during revocation.'


@auth_bp.route('/clear')
def clear_credentials():
    session.pop('credentials', None)
    return 'Credentials cleared.'

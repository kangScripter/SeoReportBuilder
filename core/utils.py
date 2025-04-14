# app/utils.py

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'granted_scopes': credentials.granted_scopes,
    }

def check_granted_scopes(credentials_dict):
    features = {
        'searchconsole': 'https://www.googleapis.com/auth/webmasters.readonly' in credentials_dict.get('granted_scopes', []),
        'calendar': 'https://www.googleapis.com/auth/calendar.readonly' in credentials_dict.get('granted_scopes', [])
    }
    return features

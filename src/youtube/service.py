import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from src.youtube.logger import YoutubeLogger

class YoutubeService:
    def __init__(self, client_file: str, secret_key: str, scopes: str, logger: YoutubeLogger, feature_redirect=None):
        if not client_file:
            raise Exception("client_file parameters passed.")
        if not secret_key:
            raise Exception("secret_key parameters passed.")
        if not scopes:
            raise Exception("scopes parameters passed.")
        
        if not isinstance(logger, YoutubeLogger):
            raise Exception("No log instance provided.")
        
        # Logging setup
        self.log = logger
        
        # API settings
        self.client_file = client_file
        self.API_SERVICE_NAME = 'youtube'
        self.API_VERSION = 'v3'
        self.scopes = scopes
        
        # Setup flask
        self.app = flask.Flask(__name__)
        self.app.secret_key = secret_key
        
        # request feature
        self._feature_redirect = feature_redirect
        
        # Pipeline
        self.setup_routes()
        
    @property
    def feature_redirect(self):
        return self._feature_redirect
    
    @feature_redirect.setter
    def feature_redirect(self, name):
        if not isinstance(name, (int, str)):
            raise ValueError("feature_name_request must be a VALID string.")
        self._feature_redirect = name

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return 'Pagina inicial' 
        self.auth()
    
    # Authorization and Authentication
    def auth(self):
        @self.app.route('/authorize')
        def authorize():
            self.log.register(0, "Autorizando...")
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(self.client_file, scopes=self.scopes)
            flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
            authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
            flask.session['state'] = state
            return flask.redirect(authorization_url)
        
        @self.app.route('/oauth2callback')
        def oauth2callback():
            self.log.register(0, "Autenticando...")
            state = flask.session['state']
            print("flask state: ", state)
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self.client_file, scopes=self.scopes, state=state)
            flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
            authorization_response = flask.request.url
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials
            flask.session['credentials'] = credentials_to_dict(credentials)
            return flask.redirect(flask.url_for(self._feature_redirect))
    
        @self.app.route('/user_channel')
        def user_channel():
            if 'credentials' not in flask.session:
                return flask.redirect('authorize')
            # Carrega as credenciais da sessão
            credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
            youtube = googleapiclient.discovery.build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)
            try:
                self.log.register(0, "request: user_channel")
                channel = youtube.channels().list(mine=True, part='snippet').execute()
                flask.session['credentials'] = credentials_to_dict(credentials)
                self.log.save_response(channel)
                return flask.jsonify(**channel)
            except Exception as e:
                self.log.register(2, "Erro:" + e)
                return flask.jsonify({'error': str(e)})
        
        @self.app.route('/like/<video_id>')
        def like_video(video_id):
            if 'credentials' not in flask.session:
                return flask.redirect('/authorize')
            credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
            youtube = googleapiclient.discovery.build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)
            try:
                self.log.register(0, f"request: /like/<video_id>, id = {video_id}")
                rate = youtube.videos().rate(id=video_id, rating='like').execute()
                flask.session['credentials'] = credentials_to_dict(credentials)
                self.log.save_response(rate)
                return flask.jsonify({'message': f'Video {video_id} liked successfully.'})
            except Exception as e:
                self.log.register(2, "Erro:" + e)
                return flask.jsonify({'error': str(e)})
            
        @self.app.route('/dislike/<video_id>')
        def dislike_video(video_id):
            if 'credentials' not in flask.session:
                return flask.redirect('/authorize')
            credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
            youtube = googleapiclient.discovery.build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)
            try:
                self.log.register(0, f"request: /dislike/<video_id>, id = {video_id}")
                rate = youtube.videos().rate(id=video_id, rating='dislike').execute()
                flask.session['credentials'] = credentials_to_dict(credentials)
                self.log.save_response(rate)
                return flask.jsonify({'message': f'Video {video_id} disliked successfully.'})
            except Exception as e:
                self.log.register(2, "Erro:" + e)
                return flask.jsonify({'error': str(e)})
            
        @self.app.route('/comment/<video_id>/text=<text>', methods=['POST'])
        def comment(video_id, text):
            if 'credentials' not in flask.session:
                return flask.redirect('/authorize')
           
            if not video_id or not text:
                self.log.register(2, "Erro: video_id or text not passed.")
                return flask.jsonify({"error": "video_id and text are required"}), 400
            
            credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
            youtube = googleapiclient.discovery.build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)

            try:
                request = youtube.commentThreads().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "topLevelComment": {
                                "snippet": {
                                    "textOriginal": text
                                }
                            }
                        }
                    }
                )
            except Exception as e:
                self.logger.error(f"Erro ao comentar no vídeo {video_id}: {e}")
                return flask.jsonify({"error": str(e)}), 500
            
        @self.app.route('/revoke')
        def revoke():
            if 'credentials' not in flask.session:
                return ('You need to <a href="/authorize">authorize</a> before ' +
                        'testing the code to revoke credentials.')

            credentials = google.oauth2.credentials.Credentials(
                **flask.session['credentials'])

            revoke = requests.post('https://oauth2.googleapis.com/revoke',
                params={'token': credentials.token},
                headers = {'content-type': 'application/x-www-form-urlencoded'})

            status_code = getattr(revoke, 'status_code')
            if status_code == 200:
                return('Credentials successfully revoked.' + print_index_table())
            else:
                return('An error occurred.' + print_index_table())
            
        @self.app.route('/clear')
        def clear_credentials():
            if 'credentials' in flask.session:
                del flask.session['credentials']
            return ('Credentials have been cleared.<br><br>' +
                    print_index_table())

        def credentials_to_dict(credentials):
            return {'token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'granted_scopes': credentials.granted_scopes}

        def print_index_table():
            return ('<table>' +
                    '<tr><td><a href="/test">Test an API request</a></td>' +
                    '<td>Submit an API request and see a formatted JSON response. ' +
                    '    Go through the authorization flow if there are no stored ' +
                    '    credentials for the user.</td></tr>' +
                    '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
                    '<td>Go directly to the authorization flow. If there are stored ' +
                    '    credentials, you still might not be prompted to reauthorize ' +
                    '    the application.</td></tr>' +
                    '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
                    '<td>Revoke the access token associated with the current user ' +
                    '    session. After revoking credentials, if you go to the test ' +
                    '    page, you should see an <code>invalid_grant</code> error.' +
                    '</td></tr>' +
                    '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
                    '<td>Clear the access token currently stored in the user session. ' +
                    '    After clearing the token, if you <a href="/test">test the ' +
                    '    API request</a> again, you should go back to the auth flow.' +
                    '</td></tr></table>')
    def run(self):
        print(self._feature_redirect)
        if not self._feature_redirect:
            raise Exception("You need to set a feature to collect.")
        self.app.run(debug=True)
        
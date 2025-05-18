"""
Caio Madeira * PUCRS
"""
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
import time
import os

# # public data read
# scopes1 = ['https://www.googleapis.com/auth/youtube.readonly']

# write and read scope
scopes2 = ['https://www.googleapis.com/auth/youtube.force-ssl']

class YoutubeAPI:
    def __init__(self, api_key, client_file):
        if not api_key:
            raise Exception("Invalid API KEY.")
        if not client_file:
            raise Exception("Invalid client file.")
        self.client_file = client_file
        self.api_key = api_key
        
        self.api_service_name = 'youtubeAnalytics'
        self.api_version = 'v3'
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        # self.yt = self.setup_api()
        
    @property
    def set_api_service_name(self, name: str):
        if not name:
            raise Exception("error")
        self.api_service_name = name
        
    def setup_api(self, scope=scopes2):
        flow = InstalledAppFlow.from_client_secrets_file(self.client_file, scopes=scope)
        flow.run_local_server(port=8081)
        yt = build('youtube', 'v3', developerKey=self.api_key)
        return yt
    
    def get_channel_statistics(self, name:str):
        yt = self.setup_api(scope='https://www.googleapis.com/auth/youtube.force-ssl')
        if name:
            request = yt.channels().list(part='statistics', forHandle=name)
            return request.execute()
        else:
            raise Exception("Name parameter is empty.")

    
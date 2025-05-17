"""
Caio Madeira * PUCRS
"""
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
import time

# public data read
scopes1 = ['https://www.googleapis.com/auth/youtube.readonly']

# write and read scope
scopes2 = ['https://www.googleapis.com/auth/youtube.force-ssl']

class Youtube:
    def __init__(self, api_key, client_file):
        if not api_key:
            raise Exception("Invalid API KEY.")
        if not client_file:
            raise Exception("Invalid client file.")
        self.client_file = client_file
        self.yt = self.setup(api_key)
        
    def setup(self, api_key):
        self.authenticate_user()
        return build('youtube', 'v3', developerKey=api_key)
    
    def authenticate_user(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.client_file, scopes=scopes2)
        flow.run_local_server(port=8081)
        session = flow.authorized_session()
        profile_info = session.get('https://www.googleapis.com/youtube/v3').json()
        print(profile_info)
    
    def get_channel_statistics(self, name:str):
        if name:
            request = self.yt.channels().list(part='statistics', forHandle=name)
            return request.execute()
        else:
            raise Exception("Name parameter is empty.")
        
    def rate_videos(self, list_id: str, rating: str):
        results = []
        if list_id or rating:
            for id in list_id:
                try:
                    request = self.yt.videos().rate(id=id, rating=rating).execute()
                    results.append(request.execute())
                except HttpError:
                    raise Exception("You need to authenticate your account.")
        else:
            raise Exception("List_id or rating parameter is empty.")
import os
from dotenv import load_dotenv
from src.youtube.service import YoutubeService
from src.youtube.logger import YoutubeLogger
import secrets

load_dotenv()

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    service = YoutubeService(client_file=os.getenv("CLIENT_FILE"), 
                             secret_key=secrets.token_hex(32), 
                             scopes='https://www.googleapis.com/auth/youtube.force-ssl',
                             logger=YoutubeLogger())
    
    service.feature_redirect = 'user_channel'
    service.run()

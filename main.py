import os
from dotenv import load_dotenv
from youtube import Youtube

load_dotenv()

yt_instance = Youtube(api_key=os.getenv("API_KEY"), client_file=os.getenv("CLIENT_FILE"))
print(yt_instance.get_channel_statistics(name="BBCNews"))

list_id = ["d5SCEysotFY", "FLFKWDEvibw"]
print(yt_instance.rate_videos(list_id=list_id, rating='dislike'))

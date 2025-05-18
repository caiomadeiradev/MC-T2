import logging
from datetime import datetime
import json
import os

class YoutubeLogger:
    def __init__(self):
        self.log_file = f'log/youtube_service_{datetime.now()}.log'
        logging.basicConfig(filename=self.log_file, 
                            level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(name)s : %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.info("Logger iniciado.")
        
    def save_response(self, info, indent:int=2):
        self.logger.info("Resposta: \n%s", json.dumps(info, indent=indent))
    
    def register(self, type:int, msg:str, error_exec_info=True):
        if not msg or type:
            raise Exception("Type or Message not valid.")
        match type:
            case 0:
                self.logger.info(msg)
            case 1:
                self.logger.warning(msg)
            case 2:
                self.logger.error(msg, exc_info=error_exec_info)
            case _:
                self.logger.info(msg)
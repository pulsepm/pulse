import logging
from pulse.config.config import load

log_format = "%(levelname)s: %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logging.addLevelName(logging.DEBUG, 'Debug')

info = load()

def debug(text: str) -> None: 
    if info['debug']:
        logging.debug(text)

def info(text: str) -> None: 
    if info['info']:
        logging.info(text)
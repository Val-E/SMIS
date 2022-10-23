import logging 

from settings import LOG_FILE, ENCODING

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=LOG_FILE, 
    encoding=ENCODING, 
    level=logging.DEBUG
)


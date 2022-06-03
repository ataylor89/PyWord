import os
import configparser
import logging

# Get configuration options from file
config = configparser.ConfigParser()
config.read('wordprocessor.ini')

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s;%(module)s;%(funcName)s;%(levelname)s;%(message)s")
logger.propagate = False
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
HOME_DIR = os.environ['HOME']
LOG_DIR = HOME_DIR + '/Logs'
LOG_FILE = LOG_DIR + '/pyword.log'
try:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
except OSError as error:
    logger.error(f'An error occurred: {error}')
except:
    logger.error('Error creating log file')
logger.info("Setup logging")
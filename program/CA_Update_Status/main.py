import sys
import os
path_app = os.getcwd()
sys.path.append(path_app)

#Logger setup
from loguru import logger
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("program/CA_Update_Status/log/Log.log", level="INFO")
# logger.add("program/CA_Update_Status/log/Log_full.log", level="DEBUG")
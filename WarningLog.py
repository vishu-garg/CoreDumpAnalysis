from ConsoleLogs import logConsole
import logging

logger= logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

def setWarningLogger(path):
    
    logConsole("Warning Logs can be viewed at: "+path+"warning.log")
    # print("Warning Logs can be viewed at: ",path+"warning.log")

    formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
    file_handler= logging.FileHandler(path+'warning.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def logWarning(err):
    logger.warning(err)

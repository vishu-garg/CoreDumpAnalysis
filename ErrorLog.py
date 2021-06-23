from ConsoleLogs import logConsole
import logging

logger= logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

def setErrLogger(path):
    
    logConsole("Error Logs can be viewed at: "+path+"errors.log")
    # print("Error Logs can be viewed at: ",path+"errors.log")

    formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
    file_handler= logging.FileHandler(path+'errors.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def logErr(err):
    logger.error(err)

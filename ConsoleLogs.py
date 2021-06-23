import logging

logger= logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def setConsoleLogger(path):
    

    # print("Console Logs can be viewed at: ",path+"warning.log")

    formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
    file_handler= logging.FileHandler(path+'console.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def logConsole(info):
    logger.info(info)

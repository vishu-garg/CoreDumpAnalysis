import logging


def getWarningLogger(path,name):
    logger= logging.getLogger(name+"warn")
    logger.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
    file_handler= logging.FileHandler(path+'warning.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def logwarning(warn,name):
    logger=logging.getLogger(name+"warn")
    logger.warning(warn)    


def getConsoleLogger(path,name):
    logger= logging.getLogger(name+"info")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
    file_handler= logging.FileHandler(path+'console.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def logconsole(info,name):
    logger=logging.getLogger(name+"info")
    logger.info(info)


def getErrLogger(path,name):
    logger= logging.getLogger(name+"err")
    logger.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
    file_handler= logging.FileHandler(path+'errors.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def logerr(err,name):
    logger=logging.getLogger(name+"err")
    logger.error(err)

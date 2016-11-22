import sys
import logging


######
# FEATURE TODOS:
# - Create new logger class, with force write to log file only option (or designated stream)
# - create a way to log parameters/values with standard bracketed format (i.e. |:<pname>=<value>:|) idea: think bind params in cx_Oracle
#

class LogHelper(object):
    '''
    #############################
    # Class Vars
    #############################

    #############################
    '''

    def __init__(self):

        '''
        Constructor
        '''

    def addNullHandler(self):
        # Set default logging handler to avoid "No handler found" warnings.
        try:
            from logging import NullHandler
        except ImportError:
            class NullHandler(logging.Handler):
                def emit(self, record):
                    pass

        rootLogger = logging.getLogger()
        rootLogger.addHandler(NullHandler())

    def getLogger(self, logFile, logLevel='INFO'):

        Logger = logging.getLogger()

        if logLevel.upper() == 'DEBUG':
            Logger.setLevel(logging.DEBUG)
        elif logLevel.upper() == 'INFO':
            Logger.setLevel(logging.INFO)
        elif logLevel.upper() == 'WARNING':
            Logger.setLevel(logging.WARNING)
        elif logLevel.upper() == 'ERROR':
            Logger.setLevel(logging.ERROR)
        else:
            Logger.setLevel(logging.CRITICAL)

        fileHandler = logging.FileHandler(logFile)
        fileFormat = logging.Formatter('%(levelname)-8s|%(name)-15s|%(lineno)-3d|%(asctime)s.%(msecs)-3d| %(message)s',
                                       '%m.%d.%y %H:%M:%S')
        fileHandler.setFormatter(fileFormat)
        consoleHandler = logging.StreamHandler()
        consoleFormat = logging.Formatter('::| %(message)s')
        consoleHandler.setFormatter(consoleFormat)
        if logLevel.upper() == 'DEBUG':
            consoleHandler.setFormatter(fileFormat)
        Logger.addHandler(fileHandler)
        Logger.addHandler(consoleHandler)

        return Logger


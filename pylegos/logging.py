""" The pylegos core logging module

This module will aide in logging efforts for your applications.  It is a
thin wrapper around the python standard logging library.
"""

import logging
from decorators import Singleton

@Singleton
class LogFactory(object):
    """ Singleton class that will return a logger with the name of the caller

    This class will retrieve a number of different loggers for you.  It can also be used safely
    by library type classes that want to log safely. Simply, if the calling application to a
    library does not setup a logger, then the libraries log statements will cause it to fail.  Libraries
    can call the "addNullHandler" routine to prevent this as it will create a "/dev/null" type logger so
    the library logging statements run without a logger.
    """

    def addNullHandler(self):
        """ Call from library code to ensure that there is a parent logger

        :return: None
        """
        try:
            from logging import NullHandler
        except:
            class NullHandler(logging.Handler):
                def emit(self, record): pass

        rootLogger = logging.getLogger()
        rootLogger.addHandler(NullHandler())


    def getFileLogger(self, logFile, logLevel='INFO'):
        ''' Use this routine to get a standard file logger, non-rotating

        :param logFile: the path the the logfile where the logger will write
        :param logLevel: the level
        :return: python standard logging object
        '''

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


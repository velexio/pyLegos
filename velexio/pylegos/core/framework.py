import inspect
import logging
import re
import platform
import traceback
import random
import sys
import os
import fcntl

from collections import OrderedDict
from ConfigParser import RawConfigParser
from fnmatch import fnmatch
from subprocess import check_output,CalledProcessError,STDOUT
from datetime import datetime

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
class Inspector(object):

    def getCallerFilePath(self, callLevel=2):
        return inspect.stack()[callLevel][1]


    def getCallerMod(self, callLevel=2):
        fileName = inspect.stack()[callLevel][1]
        modName = inspect.getmodulename(fileName)
        return modName


    def getCallerFunc(self, callLevel=2):
        iStack = inspect.stack()
        func = str(inspect.stack()[callLevel][3]).strip("'")
        return func


    '''
    def getCallerClass(self, callLevel=2):
        iStack = inspect.stack()
        callingClass = None
        fullClassName = None
        try:
            fullClassName = str(inspect.stack()[callLevel][0].f_locals["self"].__class__)
        except KeyError:
            try:
                fullClassName = str(inspect.stack()[callLevel][0].f_locals["cls"])
            except KeyError:
                pass

        callingClass = re.match(r"(<class ')([\w.]+)\.([\w]+)('>)", fullClassName).group(3)
        return callingClass
     '''


    def getCallerFQN(self, callLevel=2):
        ''' Function to get the FQN of caller (FQN = module.class.function or module.function)

        :return: The name of the calling function
        '''

        moduleName = str(self.getCallerMod(callLevel=callLevel + 1)) + '.'
        # className = str(str(self.getCallerClass(callLevel=callLevel + 1)) + '.').replace("None.", '')
        funcName = self.getCallerFunc(callLevel=callLevel + 1)

        # caller = moduleName + className + funcName
        caller = moduleName+funcName
        return caller


class DictionaryUtil(object):

    def __init__(self):
        self.KeyLevel = 0
        self.RootKey = None
        self.ParentKey = None
        self.PrevParent = None

    def toFormattedString(self, dictObj):
        return RuntimeError('Not yet implemented')
        '''
        formattedString=''
        for k,v in dictObj.iteritems():
            if self.KeyLevel == 0:
                self.RootKey = str(k)
            else:
                self.KeyLevel += 1
            formattedString += ('\t' * self.KeyLevel)+str(k)#+' : '
            if type(v) is dict:
                formattedString += ' :\n'
                #formattedString += '\n'+('\t' * self.KeyLevel)
                formattedString += self.toFormattedString(dictObj=v)
            else:
                #formattedString += str(v)+'\n'+('\t'*self.KeyLevel)
                formattedString += ' = '+str(v)+'\n'
            if self.RootKey == str(k):
                self.KeyLevel = 0
                # formattedString = formattedString[:len(formattedString)-1]
        return formattedString
        '''

    def formatToString(self, dictObj):
        return RuntimeError('Not yet implemented')
        '''
        formattedString = ''
        for k,v in dictObj.iteritems():
            if self.ParentKey is None:
                formattedString = str(k)
            else:
                formattedString += ('\t' * self.KeyLevel)+str(k)
            if type(v) is dict:
                self.PrevParent = self.ParentKey
                self.ParentKey = str(k)
                self.KeyLevel += 1
                formattedString += ' :\n'
                formattedString += self.formatToString(dictObj=v)
            else:
                formattedString += ' = '+str(v)+'\n'
            if self.ParentKey == str(k):
                self.KeyLevel -= 1

        return formattedString
        '''


class LogUtil(object):

    Logger = None

    def __init__(self, logger):
        self.Logger = logger

    def getLogfileList(self):
        filelist = []
        for h in self.Logger.handlers:
            if type(h) is logging.FileHandler:
                filelist.append(h.baseFilename)
        return filelist


    def appendToLog(self, messageObj):
        headerLine = ('*'*120)+'\n'
        footerLine = ('-'*120)+'\n\n'
        logTimeMessage = '| '+str(datetime.now())+' |\n'
        logHeader = '\n'+headerLine+logTimeMessage+headerLine
        logMessage = str(messageObj)
        '''
        if type(messageObj) is str or type(messageObj) is int:
            logMessage = str(messageObj)
        elif type(messageObj) is dict:
            # Need to format , for now until DictionaryUtil is complete, just convert to string
            logMessage = str(messageObj)
        elif type(messageObj) is list:
            print('process list')
        '''
        for fn in self.getLogfileList():
            lf = open(fn,'a')
            fcntl.flock(lf, fcntl.LOCK_EX)
            lf.write(logHeader)
            lf.write(logMessage+'\n')
            lf.write(footerLine)
            lf.flush()
            fcntl.flock(lf, fcntl.LOCK_UN)
            lf.close()


class LogFactory(object):
    """ Singleton class that will return a logger with the name of the caller

    This class will retrieve a number of different loggers for you.  It can also be used safely
    by library type classes that want to log safely. Simply, if the calling application to a
    library does not setup a logger, then the libraries log statements will cause it to fail.  Libraries
    can call the "addNullHandler" routine to prevent this as it will create a "/dev/null" type logger so
    the library logging statements run without a logger.
    """

    CodeInspector = Inspector.Instance()

    class LogLevel(object):

        CRITICAL = logging.CRITICAL
        ERROR    = logging.ERROR
        WARNING  = logging.WARNING
        INFO     = logging.INFO
        DEBUG    = logging.DEBUG

        def convert(self,levelString):
            if levelString.upper() == 'DEBUG':
                return self.DEBUG
            elif levelString.upper() == 'INFO':
                return self.INFO
            elif levelString.upper() == 'WARNING':
                return self.WARNING
            elif levelString.upper() == 'ERROR':
                return self.ERROR
            elif levelString.upper() == 'CRITICAL':
                return self.CRITICAL
            else:
                return self.DEBUG

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

    def __getDefaultFileFormatter(self):
        return logging.Formatter('%(levelname)-8s|%(name)-15s|%(lineno)-3d|%(asctime)s.%(msecs)-3d| %(message)s', '%m.%d.%y %H:%M:%S')

    def __getDefaultConsoleFormatter(self):
        return logging.Formatter('::| %(message)s')

    def __getBaseLogger(self, loggerName, logLevel=LogLevel.DEBUG):
        logger = logging.getLogger(loggerName)
        #logger.setLevel(self.LogLevel.DEBUG)
        logger.setLevel(logLevel)
        return logger

    def __setHandleFormat(self, logHandler, formatterString=None, defaultFunc=None):
        if formatterString is None:
            handleFormat = defaultFunc
        else:
            handleFormat = logging.Formatter(formatterString)
        logHandler.setFormatter(handleFormat)
        return logHandler

    def __addConsoleHandler(self,logger, formatString=None):
        defaultFormatFunc = self.__getDefaultConsoleFormatter()
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(level=logging.INFO)
        self.__setHandleFormat(logHandler=consoleHandler, formatterString=formatString, defaultFunc=defaultFormatFunc)
        logger.addHandler(consoleHandler)
        return logger

    def __addTimeRotatedFileHandler(self, logger, logFile, logLevel=LogLevel.DEBUG, formatString=None, whenRotate='D', interval=1, keepCount=10):
        h = logging
        handler = logging.handlers.TimedRotatingFileHandler(filename=logFile,
                                                                  when=whenRotate,
                                                                  interval=interval,
                                                                  backupCount=keepCount)
        self.__setHandleFormat(logHandler=handler, formatterString=formatString, defaultFunc=self.__getDefaultFileFormatter())
        logger.setLevel(level=logLevel)
        logger.addHandler(handler)
        return logger

    def __addFileHandler(self,logger,logFile, logLevel=LogLevel.DEBUG, formatString=None):
        fileHandler = logging.FileHandler(logFile)
        fileHandler.setLevel(level=logLevel)
        self.__setHandleFormat(logHandler=fileHandler, formatterString=formatString, defaultFunc=self.__getDefaultFileFormatter())
        logger.addHandler(fileHandler)
        return logger

    def getLibLogger(self):
        self.addNullHandler()
        return logging.getLogger(self.CodeInspector.getCallerMod())

    def getLogger(self, appName, appBase, logLevel=None):
        '''
        This class is meant to initialize a set of default loggers for an application.
        :param logFile:
        :param logLevel:
        :return:
        '''
        calledLogLevel = logLevel
        appConfig = IniConfig().getConfigMap(appBase+PlatformProps.FilePathSeparator+'conf'+PlatformProps.FilePathSeparator+appName+'.ini')
        logFilename = appBase + PlatformProps.FilePathSeparator + 'logs' + PlatformProps.FilePathSeparator + appName + '.log'
        if calledLogLevel is None:
            configValue = appConfig['LOGGING']['LogLevel']
            calledLogLevel = self.LogLevel().convert(configValue)
        logger = self.__getBaseLogger(loggerName=appName,  logLevel=calledLogLevel)
        logger = self.__addConsoleHandler(logger=logger)
        # logger = self.__addTimeRotatedFileHandler(logger=logger, logFile=logFilename, logLevel=logLevel)
        logger = self.__addFileHandler(logger=logger, logFile=logFilename)
        return logger

    def changeLoggingLevel(self,logLevel,logger=None):
        '''
        This module is for changing the logging level on the fly.  For example, changing the logging level
        via  a command line switch.  For vx_pylegos programs, the logger argument is optional as the logger
        will be looked up dynamically.
        :param logLevel: Level as specified with a value from pylegos.logging.LogFactory.LogLevel
        :param logger: The logger object that the program is using to log.
        :return: None
        '''
        modLogger = logger
        if logger is None:
            callerMod = self.Inspector.getCallerMod()
            modLogger = logging.getLogger(callerMod)

        handlers = modLogger.handlers

        for h in handlers:
            h.setLevel(level=logLevel)

    def getConsoleLogger(self,loggerName=None,logLevel=LogLevel.INFO,formatString=None):
        '''
        This will return a logger for logging messages to the console.
        :param logLevel:
        :param formatString:
        :return:
        '''
        logger = self.__getBaseLogger(loggerName=loggerName,logLevel=logLevel)
        logger = self.__addConsoleHandler(logger=logger,logLevel=logLevel,formatString=formatString)
        return logger

    def getFileLogger(self, logFile=None, loggerName=None, logLevel=LogLevel.DEBUG, formatString=None):
        ''' Use this routine to get a standard file logger, non-rotating

        :param logFile: the path the the logfile where the logger will write
        :param logLevel: the level of logging you want to be logged.  Default is LogLevel.INFO
        :return: python standard logging object
        '''
        logger = self.__getBaseLogger(loggerName=loggerName,logLevel=logLevel)
        logger = self.__addFileHandler(logger=logger,logFile=logFile,logLevel=logLevel,formatString=formatString)
        return logger

    def getTimedRotateFileLogger(self,loggerName=None,logFile=None,logLevel=LogLevel.DEBUG,formatString=None,whenRotate='D',interval=1,keepCount=10):
        '''
        This will return a logger with a time based rotating file handler.  This will log to the specified file and will rotate
        the file on the specified schedule.  The default schedule for rotation is every day and keep previous 10 days of logs.
        Use the optional parameters to change the schedule.  The values to pass are the same values found in the standard python
        logging library documentation.

        :param loggerName: The name of the logger.  If left at None (Recommended) the name of the logger will be the app name or calling module.
        :param logFile: The full path to the log file.  No need to pass if using pylegos.app_legos.App.init()
        :param logLevel: The pylegos.logging.LogFactory.LogLevel value to set for what messages to log.  Default LogLevel.INFO
        :param formatString: Custom format string.  If left to default value of None, the framework default will be used.
        :param whenRotate: When should rotation occur.  Default is 'D' for daily.
        :param interval: How often to rotate.  Default is 1.
        :param keepCount: How many files to keep after file is rotated.  Default is 10
        :return: Returns a standard python logger with the logging.handlers.TimedRotatingFileHandler configured.
        '''
        logger = self.__getBaseLogger(logLevel=logLevel,loggerName=loggerName)
        logger = self.__addTimeRotatedFileHandler(logger=logger,
                                                  logFile=logFile,
                                                  logLevel=logLevel,
                                                  formatString=formatString,
                                                  whenRotate=whenRotate,
                                                  interval=interval,
                                                  keepCount=keepCount)
        return logger


class FileUtils(object):

    Logger = None
    Inspector = Inspector.Instance()

    def __init__(self):
        self.Logger = LogFactory().getLibLogger()

    def getParentDir(self,filePath):
        return os.path.dirname(os.path.realpath(filePath))

    def getAppBase(self):
        callingFile = self.Inspector.getCallerFilePath()
        basePath = os.path.dirname(self.getParentDir(filePath=callingFile))
        return basePath

    def dirExists(self,directoryPath):
        '''
        Use to check if a directory exists.  This will only return true
        if it exists and is also a directory (as opposed to a file)
        :param directoryPath: The full path to the directory
        :return: Boolean (True|False)
        '''
        return os.path.isdir(directoryPath)

    def fileExists(self,filePath):
        '''
        Used to check if file exists.  It will return true if the file
        exists and it is a file, not a directory
        :param filePath: Full path to the file
        :return: Boolean (True|False)
        '''
        return os.path.isfile(filePath)

    def fileMatchExist(self,baseDir,pattern,strictCheck=True):
        '''
        Use to check if a file exists based on a pattern. The pattern that is used is
        simple unix style wildcard. (i.e. conf* will batch config, configs, configuration).
        It will only return True if the file is a file, not a directory.  If do not care if
        it is a file or directory, set optional parameter useStrictCheck to False
        :param baseDir: The directory to look in
        :param pattern: The pattern to use for match
        :param strictCheck: Indicates if it should make sure the match is a file Default is True
        :return: Boolean
        '''
        matchExists=False
        fileMatches=[]
        for file in os.listdir(baseDir):
            if fnmatch(file,pattern):
                fileMatches.append(file)

        if strictCheck:
            for match in fileMatches:
                if self.fileExists(filePath=baseDir+PlatformProps.FilePathSeparator+match):
                    matchExists=True
                    break
        else:
            if len(fileMatches > 0):
                matchExists = True

        return matchExists

    def dirMatchExist(self,baseDir,pattern,strictCheck=True):
        '''
        Used to check to see if a directory that matches a pattern exists.  The pattern is
        a unix style directory match pattern. (i.e. Conf* will match Conf,Config,Configuration,etc)
        It will only return true if the object that matches is a directory, not a file.  If you
        do not care if match is a directory, but also want to return if a file is found that matches
        the pattern, set the optional parameter strict check to False.
        :param baseDir:  The base directory to look in
        :param pattern: The unix style pattern to check
        :param strictCheck: Indicates if only a directory will be considered a match. Default is True
        :return: Boolean
        '''
        matchFound=False
        matchedDirs=[]
        for dir in os.listdir(baseDir):
            if fnmatch(dir,pattern):
                matchedDirs.append(dir)

        if strictCheck:
            for match in matchedDirs:
                if self.dirExists(directoryPath=baseDir+PlatformProps.FilePathSeparator+match):
                    matchFound=True
                    break
        else:
            if len(matchedDirs > 0):
                matchFound = True

        return matchFound

    def getFileMatches(self,baseDir,pattern,strictCheck=True):
        '''
        This will return true if a list of files that match the pattern.  If there are
        no matching files, then an empty list is returned
        :param baseDir: The directory to search in.
        :param pattern: Pattern to search for (ie conf*)
        :param strictCheck: Indicates to only include file objects (not directories) that match
        :return: List<String>
        '''
        matches=[]
        fileMatches=[]
        for file in os.listdir(baseDir):
            if fnmatch(file,pattern):
                matches.append(file)
        if strictCheck:
            for match in matches:
                if self.fileExists(filePath=baseDir+PlatformProps.FilePathSeparator+match):
                    fileMatches.append(match)
        else:
            fileMatches=matches

        return fileMatches

    def getDirMatches(self,baseDir,pattern,strictCheck=True):
        '''
        This will return true if a list of directories that match the pattern.  If there are
        no matching directories, then an empty list is returned
        :param baseDir: The directory to search in.
        :param pattern: Pattern to search for (ie conf*)
        :param strictCheck: Indicates to only include directory objects (not files) that match
        :return: List<String>
        '''
        matches=[]
        dirsFound=[]
        for dir in os.listdir(baseDir):
            if fnmatch(dir,pattern):
                matches.append(dir)
        if strictCheck:
            for match in matches:
                if self.dirExists(directoryPath=baseDir+PlatformProps.FilePathSeparator+match):
                    dirsFound.append(match)
        else:
            dirsFound=matches

        return dirsFound


    def mkdir(self,dirPath):
        '''
        Simple wrapper to os.mkdir
        :param dirPath: Full path of directory to create
        :return: None
        '''
        os.mkdir(dirPath)

    def rmdir(self,dirPath):
        os.rmdir(dirPath)

    def rmDirMatch(self,dirPath,pattern):
        dirMatches=[]
        for d in os.listdir(dirPath):
            if fnmatch(d,pattern):
                dirMatches.append(d)

        for match in dirMatches:
            self.rmdir(dirPath=dirPath+PlatformProps.FilePathSeparator+match)


class UnixOSHelper(object):
    Logger = None

    def __init__(self):
        self.Logger = LogFactory().getLibLogger()

    def getHostname(self,shortName=False):
        hostname = platform.node()
        if shortName:
            hostname=platform.node().split('.')[0]
        return hostname

    def getOSName(self):
        osName=None
        systemName = platform.system()
        if systemName == 'Linux':
            osName = platform.linux_distribution()[0]
        elif systemName == 'Darwin':
            osName = 'MacOS'
        return osName

    def getOSVersion(self):
        osName = self.getOSName()
        osVer = None
        if osName == 'Linux':
            osVer = platform.linux_distribution()[1]
        elif osName == 'Darwin':
            osVer = platform.mac_ver()[0]
        return osVer

    def checkFile4Errors(self, filename, errorMatchPattern='ERROR:'):
        self.Logger.debug('Checking output file ['+filename+'] for error match ['+errorMatchPattern+']')
        errLines = self.run('egrep '+errorMatchPattern+' '+filename)
        return errLines

    def run(self, command, useReturnCode=True, simMode=False):
        self.Logger.debug('Running command: ' + command)
        if not simMode:
            try:
                stdout = check_output(command,stderr=STDOUT)
                self.Logger.debug('Returned: ' + str(stdout))
                return stdout
            except CalledProcessError as e:
                self.Logger.error('Caught a non-zero return from running command ['+command+']')
                if useReturnCode:
                    raise OSRunException(command=command, stderr=e.output)
            except OSError as e:
                raise OSRunException(command=command, stderr=str(e))
        else:
            print('If live run, the following command would have been run on host ['+self.getHostname()+']')
            print(command)


class PlatformProps(object):
    '''

    '''
    #__metaclass__ = Singleton
    FilePathSeparator=os.path.sep
    PathSeparator=os.pathsep


class IniConfig(object):
    ###############
    # CLASS VARS
    ###############
    Config = None
    Logger = None

    ###############

    def __init__(self):
        self.Logger = LogFactory().getLibLogger()

    def getConfig(self, configFile):
        config = RawConfigParser()
        config.optionxform = str
        self.Logger.debug('Reading configuration file [' + configFile + ']')
        config.read(configFile)
        return config

    def getConfigValue(self, configFile, sectionName, propertyName):
        config = self.getConfig(configFile)
        self.Logger.debug('Returning value from section [' + sectionName + '], property [' + propertyName + ']')
        return config.get(sectionName, propertyName)

    def getConfigKeys(self, configFile, sectionName):
        config = self.getConfig(configFile)
        self.Logger.debug('Getting all properties for section [' + sectionName + ']')
        return config.options(sectionName)

    def getConfigMap(self, configFile):
        configMap = OrderedDict()
        config = self.getConfig(configFile)

        self.Logger.debug('Building config map')

        for s in config.sections():
            self.Logger.debug('Building section [' + s + ']')
            sectionMap = {}
            for k in config.options(s):
                self.Logger.debug('Getting value for key [' + k + ']')
                sectionMap[k] = config.get(s, k)

            self.Logger.debug('Adding section map ||' + str(sectionMap) + '|| to the config map')
            configMap[s] = sectionMap

        self.Logger.debug('Returning config map ||' + str(configMap) + '||')
        return configMap

    def setConfigValue(self, configFile, section, key, value):
        config = self.getConfig(configFile)
        self.Logger.debug(
            'Setting config value [' + value + '] for section [' + section + '] and property [' + key + ']')
        config.set(section, key, value)
        file = open(configFile, 'w')
        self.Logger.debug('Writing changes to file')
        config.write(file)
        file.close()

    def writeConfigMap(self, configMap, fileName):
        config = self.getConfig(fileName)

        self.Logger.debug('Building the config from map object')
        for s in configMap:
            self.Logger.debug('Building section [' + s + ']')
            config.add_section(s)
            for k in configMap[s]:
                self.Logger.debug('Adding property [' + k + '] with value [' + configMap[s][k] + ']')
                config.set(s, k, configMap[s][k])

        self.Logger.debug('Opening config file [' + fileName + '] for write')
        file = open(fileName, 'w')
        self.Logger.debug('Writing config to the file')
        config.write(file)
        file.close()


@Singleton
class App(object):
    '''
    This class has methods to setup an application.
       The standard application setup is based on the following file structure
        AppBase
          |
           -- bin
           -- conf
           -- logs
           -- lib
           -- libexec

        AppBase - Where app is installed
          bin:  Where the main application file(s) are stored
          conf: This is where configuration files are stored
          logs: Where log files are placed
          lib: Location for all libraries used by application that are not part of python installation
          libexec: optional directory for placing executable libraries

    The primary purpose of this class is to populate the AppContext class variable.  This varialbe is
    a "shareable" memory context that can be used in various parts of th pylegos libraries as well as
    the program that is using the framework.  It is an in memory representation of the App.ini configuration
    file.  Anything that is defined in the ini file will be available to any process via calls to
    the AppContext. The app context is a dictionary object, with two dimensions

    The pattern of the call is app.AppContext['SECTION NAME']['PropertyName'], where "app" is the instance
    of this class.

    Example:

    from pylegos.app_legos import App

    app = App()
    logFile = app.AppContext['LOGGING']['LogFile']
    or
    logFile = App().AppContext['LOGGING']['LogFile']

    This will load from the following example ini file

    [LOGGING]
    LogLevel=DEBUG
    LogFile=MyApp.log
'''
    #__metaclass__ = Singleton
    AppContext = {}
    log=None   # This class var violates naming convention by design.  Because logging is used so often
               # the goal is to make the call to the app logger as convenient as possible

    def __init__(self):
        '''
        This will do the following:
           - Create any required directories missing from app base
           - Build application configuration file if it is missing
           - Load the AppContext class
        :return: None
        '''
        self.AppName = self.getAppName()
        self.AppBase = self.getAppBase()
        confDirs = FileUtils().getDirMatches(baseDir=self.AppBase, pattern='conf')
        logDirs = FileUtils().getDirMatches(baseDir=self.AppBase, pattern='logs')
        '''
          We first check to see if there is an application ini file that has base level settings.  Which currently
          is just that it has a minimal logging configuration.  If no file or conf(ig) directory exists, then a
          default configuration will be created.

          In addition, if a log(s) directory is not present in the "AppBase", then a directory will be created
          so that a log file can be created.
        '''
        confDir = self.AppBase+PlatformProps.FilePathSeparator+'conf'
        logDir = self.AppBase+PlatformProps.FilePathSeparator+'logs'
        appConfFile=confDir+PlatformProps.FilePathSeparator+self.AppName+'.ini'
        if len(confDirs) < 1:
            FileUtils().mkdir(confDir)
        if not FileUtils().fileExists(appConfFile):
            self.__createStarterConfigFile(appBase=self.AppBase, appName=self.AppName, confFile=appConfFile)
        if len(logDirs) < 1:
            FileUtils().mkdir(logDir)
        self.AppContext = IniConfig().getConfigMap(configFile=appConfFile)
        self.log = LogFactory().getLogger(appName=self.AppName, appBase=self.AppBase)
        logUtil = LogUtil(logger=self.log)
        sys.path.append(self.AppBase+'/lib')
        self.AppVersion = self.getAppVersion()
        appInitMessage = """
         Application Initialized Successfully
                Name: %s
             Version: %s
            BasePath: %s
         """ % (self.AppName, self.AppVersion, self.AppBase)
        logUtil.appendToLog(appInitMessage)



    def __createStarterConfigFile(self, appName, appBase, confFile):
        defaultConfig={}
        defaultConfig['LOGGING'] = {'LogLevel': 'DEBUG', 'LogFile': appName+'.log'}
        defaultConfig['APP_INFO'] = {'AppName': appName, 'AppBasePath': appBase}
        IniConfig().writeConfigMap(configMap=defaultConfig,fileName=confFile)

    def getAppBase(self):
        inspector = Inspector.Instance()
        callingFile = inspector.getCallerFilePath(callLevel=4)
        basePath = FileUtils().getParentDir(FileUtils().getParentDir(filePath=callingFile))
        return basePath

    def getAppName(self):
        inspector = Inspector.Instance()
        callerMod = inspector.getCallerMod(callLevel=4)
        return callerMod

    def getAppVersion(self):
        modName = self.AppName+'_manifest'
        locals()['manifest_mod'] = __import__(modName)
        version = manifest_mod.VersionInfo['MAJOR']+'.'+manifest_mod.VersionInfo['MINOR']
        return version

    def appendToLog(self,messageObj):
        logUtil = LogUtil(logger=self.log)
        logUtil.appendToLog(messageObj=messageObj)


class QuoteMachine(object):
    ErrorQuotes = [
       'I blame this error on you!',
       'One of these days this will work...just not today!'
    ]
    SuccessFinishPhrases = [
        'Nice work, donuts on me!',
        'Good job, I knew you had it in you!'
    ]
    InvalidInputSayings = [
        'Hmm, are your fingers tired? That input is incorrect',
        'Is it Monday, or do you just like giving invalid input?'
    ]

    def getErrorMessage(self):
        randNum = random.randint(0,len(self.ErrorQuotes)-1)
        return 'Awe SNAP! '+self.ErrorQuotes[randNum]

    def getFinishSuccessMessage(self):
        randNum = random.randint(0,len(self.ErrorQuotes)-1)
        return self.SuccessFinishPhrases[randNum]

    def getInvalidInputMessage(self):
        randNum = random.randint(0,len(self.ErrorQuotes)-1)
        return self.InvalidInputSayings[randNum]


class AppNotInitializedException(Exception):
    def __int__(self,errorMessage='This feature cannot be used unless you have used the pylegos.app_legos.App.init() call at the start of your program'):
        self.message = errorMessage


class PyLegosFrameworkException(Exception):
    def __init__(self,msg):
        self.message = msg


class ExceptionHelper(object):
   # __metaclass__ = Singleton

    ###############################################
    # Class Vars
    ###############################################
    Logger = None

    ###############################################

    def __init__(self):
        self.Logger = LogFactory().getLibLogger()

    def handleInputError(self, errorMessage):
        ieQuote = QuoteMachine().getRandonQuote(quoteType='INPUT_ERROR')
        self.Logger.info(ieQuote)
        raise ValueError(errorMessage)

    def handleError(self, errorMessage):
        errorQuote = QuoteMachine().getRandomQuote(quoteType='ERROR')
        self.Logger.info(errorQuote)
        self.Logger.error(errorMessage)
        raise RuntimeError(errorMessage)

    def getOffender(self, sysExecptionInfo):
        eType, eObj, eTable = sys.exc_info()
        eFrame = eTable.tb_frame
        eLine = str(eTable.tb_lineno)
        eFileName = eFrame.f_code.co_filename
        eFileName = str(eFileName).strip('.').strip('/')
        return '[' + eFileName + '][' + eLine + ']'

    def printSimpleStacktrace(self):
        stack = traceback.format_exc().split('\n')
        for line in stack:
            if line.strip(' ').startswith('File'):
                rawName = line.strip('File ').split(',')[0].strip('"').split('/')
                modName = rawName[len(rawName) - 1].strip('.py')
                lineNum = line.strip('File ').split(',')[1].strip('line ')
                print('[' + modName + '][' + lineNum + ']')


class OSRunException(Exception):
    def __init__(self, command, stderr):
        errMsg = 'The following command return a non-zero return value, indicating an error.\n'
        errMsg += 'Command: ' + str(command) + '\n'
        errMsg += 'Here is the error output \n'
        if len(stderr) == 0:
            errMsg += 'Command wrote no error message'
        else:
            for line in stderr:
                errMsg += line
        self.message = errMsg



from pylegos.core import Singleton

class App(Singleton):
    """
    This class has methods to setup an application.
       The standard application setup is based on the following file structure
        AppBase
          |
           -- app
              |
               -- applibs
               -- conf
               -- modules
               -- xlibs
           -- bin
           -- logs

        AppBase - Where app is installed
           app:  Holds all application code and libraries
              applibs: libraries that are developed specifically for modules of the app
                 conf: This is where configuration files are stored
              modules: Code modules that can be independently developed, deployed
                 xlib: Location for all libraries used by application that are not part of python installation
           bin:  Where the main application file(s) are stored
          logs: Where log files are placed

    The primary purpose of this class is to populate the AppSettings class variable.  This variable is
    a "shareable" memory context that can be used in various parts of th pylegos libraries as well as
    the program that is using the framework.  It is an in memory representation of the App.ini configuration
    file.  Anything that is defined in the ini file will be available to any process via calls to
    the AppSettings. The app settings context is a dictionary object, with two dimensions

    The pattern of the call is app.AppSettings['SECTION NAME']['PropertyName'], where "app" is the instance
    of this class.

    Example:

    from pylegos.app_legos import App

    app = App()
    logFile = app.AppSettings['LOGGING']['LogFile']
    or
    logFile = App().AppSettings['LOGGING']['LogFile']

    This will load from the following example ini file

    [LOGGING]
    LogLevel=DEBUG
    LogFile=MyApp.log
    
    Another useful feature of the app singleton class is the class variable AppContext.  It too is shareable memory context
    useful for storing shared information across all components of the application.  This is dictionary. There is no strict structure
    to this dictionary. It can be used for a variety of purposes (i.e. poor mans IPC).
    
    The framework will only populate one key 'MODULES' with the list of modules found under app/modules
    
    """
    AppSettings = {}
    AppContext = {'MODULES': []}
    ''' This class var violates naming convention by design.  Because logging is used so often
        the goal is to make the call to the app logger as convenient as possible
    '''
    log = None

    def __init__(self):
        """
        This will do the following:
           - Create any required directories missing from app base
           - Build application configuration file if it is missing
           - Load the AppContext class
        :return: None
        """
        Singleton.__init__(self)
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
            FileUtils().createDirectory(confDir)
        if not FileUtils().fileExists(appConfFile):
            self.__createStarterConfigFile(appBase=self.AppBase, appName=self.AppName, confFile=appConfFile)
        if len(logDirs) < 1:
            FileUtils().createDirectory(logDir)
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
        f, filename, description = imp.find_module(modName)
        try:
            manifest_mod = imp.load_module(modName, f, filename, description)
            version = manifest_mod.VersionInfo['MAJOR']+'.'+manifest_mod.VersionInfo['MINOR']
            return version
        finally:
            f.close()

    def getAppLogFilename(self):
        logDir = self.AppBase+PlatformProps.FilePathSeparator+'logs'
        return logDir+PlatformProps.FilePathSeparator+self.AppName+'.log'


    def appendToLog(self, messageObj):
        logUtil = LogUtil(logger=self.log)
        logUtil.appendToLog(messageObj=messageObj)

class AppModule:

    def

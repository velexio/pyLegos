import argparse
import os
import sys
from traceback import print_exc
from velexio.pylegos.core.framework import ConfigManager
from velexio.pylegos.core.framework import PlatformProps
from velexio.pylegos.core.framework import FileUtils


class CommonUtils:

    @staticmethod
    def getBaseDir():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CliArgs(object):

    def __init__(self):
        fsp = PlatformProps.FilePathSep
        manifestFile = 'velexio'+fsp+'pylegos'+fsp+'pylegos_manifest.ini'
        self.AppName = 'pylegos'
        confMgr = ConfigManager(CommonUtils.getBaseDir()+fsp+manifestFile)
        self.Version = str(confMgr.getValue('VERSION', 'PylegosVersion'))
        self.runParser = argparse.ArgumentParser(description=self.AppName)

    def parse(self):

        globalArgs = argparse.ArgumentParser(add_help=False)
        projTypeArgs = argparse.ArgumentParser(add_help=False)
        self.runParser.add_argument('--version', '-v', action="version", version="Version: " + self.Version,
                                    help='Displays the version of the program')
        objectParsers = self.runParser.add_subparsers(title='Target Objects', dest='objectName',
                                                      description='The available actions/operations that can be performed')
        projectTypeGroup = projTypeArgs.add_mutually_exclusive_group(required=True)
        projectTypeGroup.add_argument('--simple', '-s', action='store_true', dest='projectSimple',
                                      help='Will create simple project (no modules/web components)')
        projectTypeGroup.add_argument('--modular', '-m', action='store_true', dest='projectModular',
                                      help='Will create modular project that supports modules/web components)')
        # GLOBAL OPTIONS
        globalArgs.add_argument('--debug', '-d', action='store_true', dest='debug')
        # SETUP ACTION PARSERS
        projectParser = objectParsers.add_parser("project", parents=[globalArgs], description="This allows you to perform project level actions")
        projectVerbs = projectParser.add_subparsers(title='Project Actions', dest='projectAction')
        projectInitParser = projectVerbs.add_parser("init", parents=[globalArgs, projTypeArgs], description="Initialize a new pylegos project")
        projectBuildParser = projectVerbs.add_parser("build", parents=[globalArgs], description="Will perform any defined build operations")
        projectUpdateParser = projectVerbs.add_parser("update", parents=[globalArgs], description="Updates/Installs any dependency modules defined")
        projectTestParser = projectVerbs.add_parser("test", parents=[globalArgs], description="Runs all unit tests defined under the test directory")
        projectRunParser = projectVerbs.add_parser("run", parents=[globalArgs], description="Runs the api server if used/configured for the project")
        moduleParser = objectParsers.add_parser("module", parents=[globalArgs], description="This allows you to perform module level operations")
        moduleActions = moduleParser.add_subparsers(title='Module Actions', dest='moduleAction')
        moduleInitParser = moduleActions.add_parser('init', parents=[globalArgs], description='Will initialize a new module within the named project')

        # HERE IS WHERE VERB PARSER ARGUMENTS GO
        projectInitParser.add_argument('--name', '-n', action="store", dest='projectName', required=True,
                                       help='This is the name of the project')
        moduleInitParser.add_argument('--name', '-n', action="store", dest='moduleName', required=True,
                                       help='This is the name of the module')
        moduleInitParser.add_argument('--project', '-p', action="store", dest='projectName', required=True,
                                      help='This is the name of the project that holds the module')
        return self.runParser.parse_args()

    @staticmethod
    def printUsage():
        print('Run pylegos -h for usage')
        print('')
        print('Example: pylegos project init --name Foo')
        sys.exit(1)


class Project:

    def __init__(self, name):
        self.ProjectName = name
        self.ProjectBaseDir = self.ProjectName+PlatformProps.FilePathSep

    def __validate(self):
        if os.path.exists(self.ProjectName):
            raise RuntimeError('A project by that name already exists')

    def __buildDirTree(self, isModular):
        s = PlatformProps.FilePathSep
        containerDirs = ['build', 'src', 'test']
        sourceDir = self.ProjectBaseDir+'src'+s
        testDir = self.ProjectBaseDir+'test'+s
        srcDirs = ['app'+s+'applibs',
                   'app'+s+'conf',
                   'app'+s+'modules',
                   'app'+s+'xlibs',
                   'bin',
                   'logs']
        os.makedirs(self.ProjectName, exist_ok=True)
        for pcd in containerDirs:
            os.makedirs(self.ProjectBaseDir+pcd, exist_ok=True)
        for psd in srcDirs:
            if psd.endswith('modules'):
                if isModular:
                    os.makedirs(sourceDir+psd, exist_ok=True)
                    os.makedirs(testDir+psd, exist_ok=True)
            else:
                os.makedirs(sourceDir+psd, exist_ok=True)
                if not psd.endswith('xlibs'):
                    os.makedirs(testDir+psd, exist_ok=True)

    def __buildManifest(self):
        sep = PlatformProps.FilePathSep
        tplDir = CommonUtils.getBaseDir()+sep+'dev'+sep+'assets'+sep
        sourceFile = tplDir+'project_base_manifest.tpl'
        targetFile = self.ProjectBaseDir+'src'+sep+'app'+sep+'conf'+sep+self.ProjectName.lower()+'_manifest.ini'
        FileUtils.copyFile(sourceFile, targetFile)
        configManager = ConfigManager(targetFile)
        configManager.setValue('APP', 'AppName', self.ProjectName)
        configManager.setValue('APP', 'Version', '0.1.0')
        configManager.setValue('PYTHON', 'RuntimeVersion', PlatformProps.getPythonVersion())
        configManager.save()

    def __buildConfFile(self):
        sep = PlatformProps.FilePathSep
        appDir = self.ProjectBaseDir+'src'+sep+'app'+sep
        templateDir = CommonUtils.getBaseDir()+sep+'dev'+sep+'assets'+sep
        appName = self.ProjectName.lower()
        FileUtils.copyFile(templateDir+'app.ini', appDir+'conf'+sep+appName+'.ini')

    def __buildCodeFiles(self):
        sep = PlatformProps.FilePathSep
        appDir = self.ProjectBaseDir+'src'+sep+'app'+sep
        templateDir = CommonUtils.getBaseDir()+sep+'dev'+sep+'assets'+sep
        appName = self.ProjectName.lower()
        templateFiles = FileUtils().getFileMatches(templateDir, 'app*.tpl')
        for tf in templateFiles:
            FileUtils.copyFile(templateDir+tf, appDir+tf.replace('app', appName).replace('.tpl', '.py'))

    def __buildBinFile(self):
        pass

    def __buildTestFiles(self):
        sep = PlatformProps.FilePathSep
        appDir = self.ProjectBaseDir+'test'+sep+'app'+sep
        templateDir = CommonUtils.getBaseDir()+sep+'dev'+sep+'assets'+sep
        appName = self.ProjectName.lower()
        templateFiles = FileUtils().getFileMatches(templateDir, 'app*.tpl')
        for tf in templateFiles:
            FileUtils.copyFile(templateDir+tf, appDir+tf.replace('app', appName).replace('.tpl', '.py'))

    def initProject(self, modularProject):
        self.__validate()
        self.__buildDirTree(modularProject)
        self.__buildManifest()
        self.__buildCodeFiles()
        self.__buildConfFile()
        self.__buildBinFile()
        self.__buildTestFiles()


class ProjectModule:

    def __init__(self, moduleName, projectName):
        self.ProjectName = projectName
        self.ModuleName = moduleName

    def __verifyProject(self):
        if not os.path.isdir(self.ProjectName):
            raise RuntimeError('The project directory does not exist.  This command must be run from your "project base" directory')

    def __buildDirTree(self):
        s = PlatformProps.FilePathSep
        projectBaseDir = self.ProjectName+s
        moduleSourceBaseDir = projectBaseDir+s+'src'+s+'app'+s+'modules'+s+self.ModuleName+s
        moduleTestBaseDir = projectBaseDir+s+'test'+s+'app'+s+'modules'+s+self.ModuleName+s
        moduleDirectories = ['assets']
        os.makedirs(moduleSourceBaseDir, exist_ok=True)
        os.makedirs(moduleTestBaseDir, exist_ok=True)
        for modDir in moduleDirectories:
            os.makedirs(moduleSourceBaseDir+modDir, exist_ok=True)
            os.makedirs(moduleTestBaseDir+modDir, exist_ok=True)

    def __buildManifest(self):
        pass

    def __buildCodeFiles(self):
        pass

    def __buildTestFiles(self):
        pass

    def __buildBinFile(self):
        pass

    def initModule(self):
        self.__verifyProject()
        self.__buildDirTree()
        self.__buildManifest()
        self.__buildCodeFiles()
        self.__buildTestFiles()
        self.__buildBinFile()


def main():

    cliArgs = CliArgs()
    args = cliArgs.parse()
    try:

        if args.objectName is None:
            cliArgs.printUsage()

        if args.objectName.lower() == 'project':
            project = Project(args.projectName)

            if args.projectAction.lower() == 'init':
                project.initProject(args.projectModular)
        else:
            cliArgs.printUsage()
    except Exception as e:
        if not args.debug:
            print('ERROR: '+str(e))
        else:
            print_exc()

main()

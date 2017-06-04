import argparse
import os
import sys
from ast import literal_eval
from traceback import print_exc
from argparse import Namespace
from pylegos.core import ConfigManager
from pylegos.core import PlatformProperty
from pylegos.cli.pycli_controllers import ProjectController
from pylegos.cli.pycli_controllers import ModuleController
from pylegos.cli.pycli_controllers import ModelController
from pylegos.cli.pycli_controllers import BuildController


class CommonUtils:

    @staticmethod
    def getBaseDir():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CliArgs(object):

    def __init__(self):
        fsp = PlatformProperty.FileSep
        manifestFile = 'pylegos_manifest.ini'
        self.AppName = 'pylegos'
        confMgr = ConfigManager(CommonUtils.getBaseDir()+fsp+manifestFile)
        ver = literal_eval(confMgr.getValue('VERSION', 'Version'))
        majVer = ver['MAJOR']
        minVer = ver['MINOR']
        self.Version = majVer+minVer
        self.runParser = argparse.ArgumentParser(description=self.AppName)
        self.Args = self.parse()

    def parse(self):

        globalArgs = argparse.ArgumentParser(add_help=False)
        projTypeArgs = argparse.ArgumentParser(add_help=False)
        self.runParser.add_argument('--version', '-v', action="version", version="Version: " + self.Version,
                                    help='Displays the version of the program')
        objectParsers = self.runParser.add_subparsers(title='Target Objects', dest='objectName',
                                                      description='The objects that can be maintained by cli tool')
        # GLOBAL OPTIONS
        globalArgs.add_argument('--debug', '-d', action='store_true', dest='debug')
        # SETUP ACTION PARSERS
        projectParser = objectParsers.add_parser("project", parents=[globalArgs],
                                                 description="This allows you to perform project level actions")
        projectVerbs = projectParser.add_subparsers(title='Project Actions', dest='projectAction')
        projectInitParser = projectVerbs.add_parser("init", parents=[globalArgs, projTypeArgs],
                                                    description="Initialize a new pylegos project")
        projectBuildParser = projectVerbs.add_parser("build", parents=[globalArgs],
                                                     description="Will perform any defined build operations")
        projectUpdateParser = projectVerbs.add_parser("update", parents=[globalArgs],
                                                      description="Updates/Installs any dependency modules defined")
        projectTestParser = projectVerbs.add_parser("test", parents=[globalArgs],
                                                    description="Runs all unit tests defined under the test directory")
        projectRunParser = projectVerbs.add_parser("run", parents=[globalArgs],
                                                   description="Runs the api server if used/configured for the project")
        projectModularizeParser = projectVerbs.add_parser("modularize", parents=[globalArgs],
                                                          description="Runs the api server if used/configured for the project")
        moduleParser = objectParsers.add_parser("module", parents=[globalArgs],
                                                description="This allows you to perform module level operations")
        moduleActions = moduleParser.add_subparsers(title='Module Actions', dest='moduleAction')
        moduleAddParser = moduleActions.add_parser('add', parents=[globalArgs],
                                                   description='Will add a new module within the named project')
        modelParser = objectParsers.add_parser("model", parents=[globalArgs])
        modelVerbs = modelParser.add_subparsers(title='Model Actions', dest='modelAction')
        modelAddParser = modelVerbs.add_parser('add', parents=[globalArgs])
        modelDefParser = modelVerbs.add_parser('def', parents=[globalArgs])


        # HERE IS WHERE VERB PARSER ARGUMENTS GO
        projectInitParser.add_argument('--name', '-n', action="store", dest='projectName', required=True,
                                       help='This is the name of the project')
        projectInitParser.add_argument('--simple', '-s', action='store_true', dest='projectSimple',
                                       help='Will create simple project (no modules/web components)')
        #
        projectModularizeParser.add_argument('--name', '-n', action="store", dest='projectName', required=True,
                                             help='This is the name of the project')
        #
        moduleAddParser.add_argument('--name', '-n', action="store", dest='moduleName', required=True,
                                       help='This is the name of the module')
        #
        modelAddParser.add_argument('--def-file', '-df', action="store", dest='modelAddDefFile', required=True,
                                    help='The definition file in the moddefs dir or full path if located elsewhere')
        modelAddParser.add_argument('--persistent', '-p', action="store_true", dest='modelAddPersistent',
                                    required=False,
                                    help='Optional. Indicates a persistent (database) objects should also be created')
        modelAddParser.add_argument('--force', '-f', action="store_true", dest='modelAddForce', required=False,
                                    help='Optionally force the creation even if the model already exists')
        modelDefParser.add_argument('--name', '-n', action='store', dest='modelDefName', required=True,
                                    help='The name of the defgen file to create')
        return self.runParser.parse_args()

    @staticmethod
    def printUsage():
        print('Run pylegos -h for usage')
        print('')
        print('Example: pylegos project init --name Foo')
        sys.exit(1)


def main():

    cliArgs = CliArgs()
    runInIDE = False
    if runInIDE:
        cliArgs.Args = Namespace(objectName='project', projectName='xdot', projectAction='init', projectModular=False, projectInitModuleList=None, debug=True)

    try:

        if cliArgs.Args.objectName is None:
            cliArgs.printUsage()
        if cliArgs.Args.objectName.lower() == 'project':
            controller = ProjectController(projectName=cliArgs.Args.projectName)
            if cliArgs.Args.projectAction.lower() == 'init':
                controller.initProject(isSimple=cliArgs.Args.projectSimple)
            elif cliArgs.Args.projectAction.lower() == 'modularize':
                controller.modularize()
        elif cliArgs.Args.objectName.lower() == 'module':
            controller = ModuleController(moduleName=cliArgs.Args.moduleName)
            if cliArgs.Args.moduleAction == 'add':
                controller.addModule()
        elif cliArgs.Args.objectName.lower() == 'model':
            controller = ModelController()
            if cliArgs.Args.modelAction.lower() == 'add':
                controller.addModel(defFilename=cliArgs.Args.modelAddDefFile,
                                    persistent=cliArgs.Args.modelAddPersistent,
                                    forceAdd=cliArgs.Args.modelAddForce)
            elif cliArgs.Args.modelAction.lower() == 'def':
                controller.createDef(moduleName=cliArgs.Args.modelDefName)
        elif cliArgs.Args.objectName.lower() == 'build':
            BuildController.run()
        else:
            cliArgs.printUsage()
    except Exception as e:
        if not cliArgs.Args.debug:
            print('ERROR: '+str(e))
        else:
            print_exc()

if __name__ == '__main__':
    main()

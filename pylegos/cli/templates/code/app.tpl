
import argparse
from sys import exit
from pylegos.core import App
from pylegos.core import AppLogger
from pylegos.core import AppException


class CLIArgs:

    def __init__(self, programTitle, programVersion):
        self.ProgramTitle = programTitle
        self.ProgramVersion = programVersion

    def parse(self):
        globalArgs = argparse.ArgumentParser(add_help=False)
        runParser = argparse.ArgumentParser(description=self.ProgramTitle)
        runParser.add_argument('--version', '-v', action="version", version="Version: " + self.ProgramVersion, help='Displays version')
        # GLOBAL OPTIONS
        globalArgs.add_argument('--debug', '-d', action="store_true", dest='debug',
                                help='Flag to indicate that logging data will be displayed to the console')

        objectParsers = runParser.add_subparsers(title="Objects", dest='objectName',
                                                 description='The object names that can take actions')
        targetParser = objectParsers.add_parser('target', parents=[globalArgs])
        targetActions = targetParser.add_subparsers(title="Target Actions", dest='targetAction',
                                                    description='Available actions for target object')
        targetRunParser = targetActions.add_parser('run', parents=[globalArgs])
        targetRunParser.add_argument('--option', '-o', action='store', dest='targetRunOption', help='Example')

        try:
            args = runParser.parse_args()
        except Exception as e:
            print('CLI PARSE ERROR: '+str(e))
            exit(1)


class {{APPNAME_OBJECT}}:

    def __init__(self):
        self.app = App()
        self.logger = AppLogger(self.app.AppName)

    def main(self):
        cliArgs = CLIArgs(programTitle=self.app.AppName, programVersion=self.app.AppVersion).parse()

        try:
            # PROCESS CLI ARGS AND OPTIONS
            cliObjectName = cliArgs.objectName

            if cliObjectName.lower == 'target':
                if cliArgs.targetAction.lower() == 'run':
                    runOpt = cliArgs.targetRunOption
                    # call controller
                    # i.e.
                    # controller = TestController()
                    # response = json.loads(controller.getSomeData())
                    # ControllerUtil.checkResponse(response)
            else:
                raise RuntimeException('cli args not recognized')

        except AppException as ae:
            print('ERROR ('+ae.ErrorCode+'): '+ae.ErrorMessage)
        except Exception as e:
            print('ERROR: '+str(e))
            exit(1)


if __name__ == '__main__':
    app = {{APPNAME_OBJECT}}()
    app.main()
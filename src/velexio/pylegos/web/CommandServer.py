import time
import shlex
from pycnic.core import WSGI, Handler
from subprocess import check_output, CalledProcessError, STDOUT


class RootHander(Handler):
    def get(self):
        return {'Usage:': 'http://<host>:<port>/os/run'}


class CommandRunner(Handler):

    def __run(self, command, useReturnCode=True, secureLog=False):
        """
        Use this to run an os command.  If the command itself is secure in nature or it could
        output data that is considered secure (i.e. passwords), make sure to turn the secureLog
        parameter to True.
        :param command: The full command that is to be run
        :param useReturnCode: Boolean flag to indicate if non-zero return value of command dictates failure
        :param secureLog: Boolean flag to turn logging off for any command references or logging output
        :return: None
        """
        runCmd = shlex.split(command)
        try:
            stdout = check_output(runCmd, stderr=STDOUT).split('\n')
            print('StdOut: '+str(stdout))
            stdRet = []
            for l in stdout:
                if len(l) > 0:
                    stdRet.append(l)
            print('stdRet: '+str(stdRet))
            return stdRet
        except CalledProcessError as e:
            if useReturnCode:
                raise OSRunException(command=command, stderr=e.output)
        except OSError as e:
            raise OSRunException(command=command, stderr=str(e))

    def post(self):
        cmd = self.request.data['command']
        print("Running command: "+cmd)
        try:
            cmdOut = self.__run(command=cmd)
            return {'CommandOut':cmdOut,
                    'Result': 'Success'}
        except OSRunException as e:
            return {'Command': cmd,
                    'CommandOut': e.message,
                    'Result': 'Failed'}


class app(WSGI):
    routes = [('/', RootHander()),
              ('/os/run', CommandRunner())]


class OSRunException(Exception):
    def __init__(self, command, stderr):
        errMsg = ''
        if len(stderr) == 0:
            errMsg += 'Command wrote no error message'
        else:
            for line in stderr:
                errMsg += line
        self.message = errMsg
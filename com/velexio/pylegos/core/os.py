import os
import logging

from vxlogging import LogHelper
from vxpatternlego import Singleton


class CommandRunner(object):
    __metaclass__ = Singleton
    ###############################################
    # Class Vars
    ###############################################
    Logger = None

    ###############################################

    def __init__(self):
        LogHelper().addNullHandler()
        self.Logger = logging.getLogger(__name__)

    def checkError(self, stdErr):
        errorOut = []
        self.Logger.debug('Checking for errors during command run')
        for errLine in stdErr:
            errVal = errLine.strip('\n')
            self.Logger.debug(
                'Checking output line from ssh command [' + errVal + '] for expected values present during login')
            if len(errVal) > 0:
                self.Logger.debug('Found error [' + errVal + '], appending to error list')
                errorOut.append(errVal)

        if len(errorOut) > 0:
            errorMessage = "An error occurred running the remote command.  Below is full error message(s)\n"
            for l in errorOut:
                errorMessage += l
            self.Logger.error(errorMessage)
            raise RuntimeError(errorMessage)

    def run(self, command, simMode=False):
        returnOut = []
        self.Logger.debug('Running command: ' + command)
        if not simMode:
            cmdArgs = shlex.split(command)
            cmd = subprocess.Popen(cmdArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            errout = cmd.stderr.readlines()
            self.checkError(errout)
            self.Logger.debug('Getting command output')
            output = cmd.stdout.readlines()
            del returnOut[:]
            for l in output:
                v = str(str(l).split('\n')[0])
                if len(v) > 0:
                    self.Logger.debug('Adding  [' + v + '] to the output list')
                    returnOut.append(v)

            self.Logger.debug('Returned: ' + str(output))
            return returnOut
        else:
            print('Simulated run')
            print(command)

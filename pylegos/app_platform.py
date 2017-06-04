import shlex
import re
import subprocess
from subprocess import CalledProcessError
from core import AppLogger


class SSHCommand(object):

    def __init__(self, host, user):
        self.logger = AppLogger().getAppLibLogger(className='SSHCommand')
        self.Hostname = host
        self.Username = user

    def run(self, command, secureLog=False):
        self.logger.debug('Running command ['+command+']')
        try:
            FNULL = open('/dev/null', 'w')
            stdout = subprocess.check_output(["ssh", "%s" % self.Username + "@" + self.Hostname, command],
                                             shell=False,
                                             stderr=FNULL)
            if not secureLog:
                self.logger.debug('Response: |:|'+str(stdout.decode())+'|:|')
            FNULL.close()
            return str(stdout.decode())
        except CalledProcessError as cpe:
            self.logger.warn('ERROR: '+str(cpe))
            self.logger.exception('STACKTRACE')
            raise SSHCommandError(str(cpe))

    def fileExists(self, fileName):
        fileFound = False
        self.logger.debug('checking to see if remote file [' + fileName + '] exists')
        cmdOut = self.run('if [ -f ' + fileName + ' ]; then echo Found; fi')
        if str(cmdOut)[0].strip() == "Found":
            self.logger.debug('Found the file')
            fileFound = True

        return fileFound

    def dirExists(self, dirName):
        dirFound = False
        self.logger.debug('Checking to see if remote directory [' + dirName + '] exists')
        cmdOut = self.run('if [ -d ' + dirName + ' ]; then echo Found; fi')
        self.logger.debug('Returned output [' + str(cmdOut).strip() + ']')
        formattedValue = str(cmdOut).strip()
        if len(formattedValue) > 0:
            if formattedValue == "Found":
                self.logger.debug('Directory exists')
                dirFound = True
        return dirFound

    def sendFile(self, localFile, remoteFile):
        self.logger.debug(
            'SCP local file [' + localFile + '] to remote file [' + self.Hostname + ':' + remoteFile + ']')
        scp = subprocess.Popen(["scp", "%s" % localFile, "%s" % self.Username + "@" + self.Hostname + ':' + remoteFile],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdErrOut = scp.stderr.readlines()
        self.checkError(stdErr=stdErrOut)
        self.logger.debug('SCP operation complete')

    def getFile(self, remoteFile, localFile):
        scp = subprocess.Popen(["scp", "%s" % self.Username + "@" + self.Hostname + ':' + remoteFile, "%s" % localFile],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdErrOut = scp.stderr.readlines()
        self.checkError(stdErr=stdErrOut)

    def rsyncRemoteDir(self, localDir, remoteDir):
        self.logger.debug('Performing rsync of local dir [' + localDir + '] with remote dir [' + remoteDir + ']')
        toNull = " 2>/dev/null"
        try:
            FNULL = open('/dev/null', 'w')
            rsync = subprocess.check_output(["rsync", "-are", '"ssh -q"', "%s" % localDir, "%s" % self.Username + "@" + self.Hostname + ":" + remoteDir], stderr=FNULL, shell=False)
        except CalledProcessError as cpe:
            self.logger.debug('ERROR: '+str(cpe))
            self.logger.exception('STACKTRACE')
            raise SSHCommandError(errMessage=str(cpe))

    def rsyncRemoteDir2(self, localDir, remoteDir):
        self.logger.debug('Performing rsync of local dir ['+localDir+'] with remote dir ['+remoteDir+']');
        stdout = subprocess.Popen(["rsync", "-ar", "%s" % localDir, "%s" % self.Username+"@"+self.Hostname+":"+remoteDir],
                         shell=False,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)


    def fileExists(self, fileName):
        fileFound = False
        self.logger.debug('checking to see if remote file [' + fileName + '] exists')
        cmdOut = self.run('if [ -f ' + fileName + ' ]; then echo Found; fi')
        if str(cmdOut)[0].strip() == "Found":
            self.logger.debug('Found the file')
            fileFound = True

        return fileFound

    def dirExists(self, dirName):
        dirFound = False
        self.logger.debug('Checking to see if remote directory [' + dirName + '] exists')
        cmdOut = self.run('if [ -d ' + dirName + ' ]; then echo Found; fi')
        self.logger.debug('Returned output [' + str(cmdOut).strip() + ']')
        formattedValue = str(cmdOut).strip()
        if len(formattedValue) > 0:
            if formattedValue == "Found":
                self.logger.debug('Directory exists')
                dirFound = True
        return dirFound

    def sendFile(self, localFile, remoteFile):
        self.logger.debug(
            'SCP local file [' + localFile + '] to remote file [' + self.Hostname + ':' + remoteFile + ']')
        scp = subprocess.Popen(["scp", "%s" % localFile, "%s" % self.Username + "@" + self.Hostname + ':' + remoteFile],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdErrOut = scp.stderr.readlines()
        self.checkError(stdErr=stdErrOut)
        self.logger.debug('SCP operation complete')

    def getFile(self, remoteFile, localFile):
        scp = subprocess.Popen(["scp", "%s" % self.Username + "@" + self.Hostname + ':' + remoteFile, "%s" % localFile],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdErrOut = scp.stderr.readlines()
        self.checkError(stdErr=stdErrOut)

    def rsyncRemoteDir(self, localDir, remoteDir):
        self.logger.debug('Performing rsync of local dir [' + localDir + '] with remote dir [' + remoteDir + ']')
        try:
            rsync = subprocess.check_output(["rsync", "-ar", "%s" % localDir, "%s" % self.Username + "@" + self.Hostname + ":" + remoteDir])
        except CalledProcessError as cpe:
            self.logger.error('Error during rsync')
            self.logger.exception('StackTrace')
            raise SSHCommandError(errMessage=str(cpe))

    def checkFile4Error(self, fileName, matchPattern='ERROR'):
        self.logger.debug('Checking remote filename [:' + fileName + ':] for errors')
        cmdOut = self.run('egrep ' + matchPattern + ' ' + fileName)
        self.logger.debug('The following error lines where found in the remote file |:' + str(cmdOut) + ':|')
        return cmdOut

    def checkFile4Match(self, fileName, matchPattern):
        self.logger.debug('Retrieving filename [:' + fileName + ':] from host [:' + self.Hostname + ':]')
        self.getFile(fileName, fileName)
        localFile = open(fileName, 'r')
        for line in localFile.readlines():
            if re.match(r'' + matchPattern + '', line):
                localFile.close()
                return True

        localFile.close()
        return False

    def copyFile(self, sourceFile, targetDir):
        self.logger.debug('Coping file [' + sourceFile + '] to dir [' + targetDir + ']')
        self.run(command='cp -f ' + sourceFile + ' ' + targetDir + '/.')


class CommandRunner:

    __package__ = 'applibs'

    def __init__(self, secureLog=False):
        self.logger = AppLogger().getAppLibLogger(className='CommandRunner')
        self.SecureLog = secureLog

    def run(self, command, simMode=False):
        if not self.SecureLog:
            self.logger.debug('Running command: ' + command)

        if not simMode:
            cmdArgs = shlex.split(command)
            try:
                stdOut = subprocess.check_output(cmdArgs)
                if not self.SecureLog:
                    self.logger.debug('Returned: ' + str(stdOut))
                return stdOut
            except CalledProcessError as cpe:
                raise CommandError(str(cpe))
        else:
            print('Simulated run')
            print(command)


class CommandError(Exception):

    def __init__(self, errMessage):
        Exception.__init__(self, "CommandError: "+errMessage)
        self.message = 'ERROR: '+errMessage


    def checkFile4Error(self, fileName, matchPattern='ERROR'):
        self.logger.debug('Checking remote filename [:' + fileName + ':] for errors')
        cmdOut = self.run('egrep ' + matchPattern + ' ' + fileName)
        self.logger.debug('The following error lines where found in the remote file |:' + str(cmdOut) + ':|')
        return cmdOut

    def checkFile4Match(self, fileName, matchPattern):
        self.logger.debug('Retrieving filename [:' + fileName + ':] from host [:' + self.Hostname + ':]')
        self.getFile(fileName, fileName)
        localFile = open(fileName, 'r')
        for line in localFile.readlines():
            if re.match(r'' + matchPattern + '', line):
                localFile.close()
                return True

        localFile.close()
        return False

    def copyFile(self, sourceFile, targetDir):
        self.logger.debug('Coping file [' + sourceFile + '] to dir [' + targetDir + ']')
        self.run(command='cp -f ' + sourceFile + ' ' + targetDir + '/.')


class CommandRunner:

    __package__ = 'applibs'

    def __init__(self, secureLog=False):
        self.logger = AppLogger().getAppLibLogger(className='CommandRunner')
        self.SecureLog = secureLog

    def run(self, command, simMode=False):
        if not self.SecureLog:
            self.logger.debug('Running command: ' + command)

        if not simMode:
            cmdArgs = shlex.split(command)
            try:
                stdOut = subprocess.check_output(cmdArgs)
                if not self.SecureLog:
                    self.logger.debug('Returned: ' + str(stdOut))
                return stdOut
            except CalledProcessError as cpe:
                raise CommandError(str(cpe))
        else:
            print('Simulated run')
            print(command)


class CommandError(Exception):

    def __init__(self, errMessage):
        Exception.__init__(self, "CommandError: "+errMessage)
        self.message = 'ERROR: '+errMessage


class SSHCommandError(Exception):

    def __init__(self, errMessage):
        Exception.__init__(self, "SSHCommandError: "+errMessage)
        self.message = 'ERROR: '+errMessage

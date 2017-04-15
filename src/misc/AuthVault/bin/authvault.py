#!/bin/env python

import argparse
import os



class CLIArgs(object):

    def __init__(self):
        self.AppName = 'authvault'
        self.ProgramVersion = '0.1.0'

    def parse(self):
        globalArgs = argparse.ArgumentParser(add_help=False)
        vaultArgs = argparse.ArgumentParser(add_help=False)
        credArgs = argparse.ArgumentParser(add_help=False)
        runParser = argparse.ArgumentParser(description=self.AppName)
        runParser.add_argument('--version', '-v', action="version", version="Version: " + self.ProgramVersion,
                               help='Displays the version of the program')
        actionParsers = runParser.add_subparsers(title='Actions', dest='actionName',
                                                 description='The available actions/operations that can be performed')
        globalArgs.add_argument('--debug', '-d', action="store_true", dest='debug',
                                required=False, help='Flag to indicate that logging data will be displayed to the console')
        vaultArgs.add_argument('--vault-name', '-vn', action="store", dest='vaultName',
                               required=True, help='This specifies the name of the vault')
        vaultArgs.add_argument('--entry-name', '-en', action="store", dest='entryName',
                               required=True, help='This specifies the name of the entry to perform action on')
        credArgs.add_argument('--password', '-p', action="store", dest='cred',
                              required=True, help='This specifies the password to store for the entry')

        listParser = actionParsers.add_parser("keys", parents=[globalArgs, vaultArgs],
                                              description="This action will list all keys in the specified vault")
        getParser = actionParsers.add_parser("get", parents=[globalArgs, vaultArgs],
                                             description="This action will get and show the passphrase of a single entry")
        addParser = actionParsers.add_parser("add", parents=[globalArgs, vaultArgs],
                                             description="This action will add a new credential to a vault")
        changeParser = actionParsers.add_parser("change", parents=[globalArgs, vaultArgs, credArgs],
                                                description="This action will change a credential password")
        removeParser = actionParsers.add_parser("remove", parents=[globalArgs, vaultArgs, credArgs],
                                                description="This action will remove a credential entry")

        # PARSE COMMAND LINE ARGUMENTS
        args = runParser.parse_args()
        return args

class CommonUtils(object):

    @staticmethod
    def getAppBase():
        #return Path(__name__).parent
        return os.path.dirname(os.path.dirname(__file__))

    @staticmethod
    def getKeyFilename():
        return CommonUtils.getAppBase()+'/conf/.authvault.asc'

    @staticmethod
    def getCertFilename():
        return CommonUtils.getAppBase()+'/conf/.authvault.cert'

    @staticmethod
    def setSecureFilePerms():
        keyFilename = CommonUtils.getKeyFilename()
        certFilename = CommonUtils.getCertFilename()
        if not os.path.isfile(keyFilename):
            os.system('touch '+keyFilename)
        if not os.path.isfile(certFilename):
            os.system('touch '+certFilename)

        os.chmod(keyFilename, 600)
        os.chmod(certFilename, 600)




class AuthVault(object):

    def __init__(self, vaultName, entryName):
        self.VaultBase = '~/.secure/.data'
        self.VaultName = vaultName
        self.EntryName = entryName
        CommonUtils.setSecureFilePerms()

    def loadCert(self):
        appBase = CommonUtils.getAppBase()
        confDir = appBase+'/conf'
        certFile = appBase+'/conf/authvault.cert'

    def getCred(self):
        return None


class AuthVaultGuardDog(object):

    def __init__(self):
        pass
    

class Cli(object):

    @staticmethod
    def main():
        cliArgs = CLIArgs().parse()
        action = cliArgs.actionName

        if action == 'keys':
            print('Keystore keys')

class VaultIntegrityViolation(Exception):

    def __init__(self):
        self.message = 'The integrity of the datastore has been compromised.  Manually validate file integrity before any further operations are allowed'
        
    
if __name__ == '__main__':

    cli = Cli()
    cli.main()

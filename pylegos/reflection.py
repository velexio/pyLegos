import inspect
import logging

from logging import LogFactory


class Inspector(object):
    ##########################################
    # CLASS VARS
    ##########################################
    Logger = None

    ##########################################

    def __init__(self):
        LogFactory().addNullHandler()
        self.Logger = logging.getLogger(__name__)

    def getCallerMod(self,callLevel=1):
        fileName = inspect.stack()[callLevel][1]
        modName = inspect.getmodulename(fileName)
        return modName

    def getCallerFunc(self,callLevel=1):
        func = str(inspect.stack()[callLevel][3]).strip("'")
        return func

    def getCallerClass(self,callLevel=1):
        callClass=None
        try:
            callClass = str(inspect.stack()[callLevel][0].f_locals["self"].__class__).split(".")[1].strip("'>").strip("'")
        except KeyError: pass

        return callClass

    def getCaller(self):
        ''' Function to get the FQN of caller (FQN = module.class.function or module.function)

        :return: The name of the calling function
        '''
        fn = inspect.stack()[1][1]
        mn = inspect.getmodulename(fn)
        c=''
        f = str(inspect.stack()[1][3]).strip("'")

        caller=str(mn)+'.'+c+'.'+f
        caller = caller.replace("..",".")
        return caller



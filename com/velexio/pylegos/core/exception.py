import logging
import traceback
from vxlogging import LogHelper
from vxtermlego import QuoteMachine
from vxpatternlego import Singleton


class ExceptionHelper(object):
    __metaclass__ = Singleton

    ###############################################
    # Class Vars
    ###############################################
    Logger = None

    ###############################################

    def __init__(self):
        LogHelper().addNullHandler()
        self.Logger = logging.getLogger(__name__)

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




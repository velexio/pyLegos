import os
import sys
import inspect
import traceback
import logging
import shlex
import subprocess
import logging

from vxlogging import LogHelper


class Inspector(object):
    ##########################################
    # CLASS VARS
    ##########################################
    Logger = None

    ##########################################

    def __init__(self):
        LogHelper().addNullHander()
        self.Logger = logging.getLogger(__name__)

    def getCaller(self):
        callerMap = []
        curFrame = inspect.currentframe()
        outerFrame = inspect.getouterframes(curFrame, 2)
        callerMap.append(str(os.path.basename(os.path.normpath(outerFrame[2][1]))).strip(
            '.py'))  # BASE MODULE NAME (FILE NAME MINUX .py)
        callerMap.append(outerFrame[2][3])  # function/method name
        callerMap.append(outerFrame[2][2])  # line number from the file

        return callerMap


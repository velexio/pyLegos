import time

from Queue import Queue

import threading
from src.velexio.pylegos.core import LogFactory
from src.velexio.pylegos.core import ProgressBar
from src.velexio.pylegos.core import Spinner
from src.velexio.pylegos.core import SpinnerType


class Thread(object):

    def __init__(self):
        self.logger = LogFactory().getLibLogger()
        self.queue = Queue()

    def __runThread(self, func, args):
        threadName = self.queue.get()
        self.logger.debug('Thread ['+str(threadName)+'] calling func ['+str(func)+']')
        func(**args)
        self.logger.debug('Finished running function setting queue task to done')
        self.queue.task_done()

    def runAndWait(self, waitMessage, threadName, runFunc, funcNamedParams={}, spinnerType=SpinnerType.Classic):
        """
        * NOTE: Still if dev, so use at own risk ;)
        This procedure will run the named function in a seperate thread so that async operation is possible
        :param threadName: <br>
        :param runFunc: <br>
        :param funcArgs: <br>
        :return: None <br>
        """
        '''ToDo, check if thread name already exists, if so throw exception'''
        self.queue.put(item=threadName)
        t = threading.Thread(target=self.__runThread, args=(runFunc, funcNamedParams,))
        try:
            t.start()
            spinner = Spinner(message=waitMessage, spinnerType=spinnerType)
            while self.queue.unfinished_tasks > 0:
                spinner.spin()
                time.sleep(.25)
            spinner.stop()
        except Exception as e:
            self.logger.debug('Hit error: '+str(e))
            spinner.stop()
            raise


    def runAndShowProgress(self, jobMap, initMesg='Initializing'):
        """
        This will run a "jobMap" in a blocking fashion and show a progress bar, updating after
        each step in the job is complete. The jobMap argument must be a dictionary that has the following
        format:<br><br>
        jobMap = {'Step 1': {'func': stepOneFunc,
                             'args': {'parameter1': parameterValue,
                                      'parameter2': parameterValue
                                      }
                             },
                  'Step 2': {'func': stepTwoFunc,
                             'args': {'parameter1': parameterValue}
                             },
                  'Step 3': {'func': stepThreeFunc,
                             'args': {'parameter1': parameterValue,
                                      'parameter2': parameterValue
                                      }
                             }
        <br><br>
        :param jobMap: The job map that follows above format that holds the functions to run
        :param initMesg: The initial message to show on the progress bar.  Default 'Initializing'
        :return: None
        """
        progressBar = ProgressBar(initialMessage=initMesg, numOperations=len(jobMap))
        time.sleep(1)
        msgHeader='Running -> '
        for step, stepAttribs in jobMap.iteritems():
            self.queue.put(item=step)
            stepMessage = msgHeader + step
            progressBar.updateMessage(message=stepMessage)
            fx=stepAttribs['func']
            fxa=stepAttribs['args']
            t = threading.Thread(target=self.__runThread, args=(fx, fxa,))
            t.start()
            spinner = Spinner(message='  : ', spinnerType=SpinnerType.Clock)
            while self.queue.unfinished_tasks > 0:
                spinner.spin()
                time.sleep(.15)
            progressBar.updateProgress()
        progressBar.updateMessage('Finished')
        progressBar.finish()

    def runAndContinue(self, runFunc, args):
        pass

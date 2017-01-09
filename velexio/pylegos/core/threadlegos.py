import re
import threading
import time
from Queue import Queue
from framework import LogFactory
from termlegos import Spinner


class Thread(object):

    def __init__(self):
        self.logger = LogFactory().getLibLogger()
        self.queue = Queue()

    def __runThread(self,func,args):
        threadName = self.queue.get()
        self.logger.debug('Thread ['+str(threadName)+'] calling func ['+str(func)+']')
        func(args)
        self.logger.debug('Finished running function setting queue task to done')
        self.queue.task_done()

    def runAndWait(self,threadName, runFunc, funcArgs):
        '''ToDo, check if thread name already exists, if so throw exception'''
        self.queue.put(item=threadName)
        threadArgs = []
        threadArgs.append(runFunc)
        for a in funcArgs:
            threadArgs.append(a)
        t = threading.Thread(target=self.__runThread, args=threadArgs)
        t.start()
        spinner = Spinner()
        while self.queue.unfinished_tasks > 0:
            spinner.spin()
            time.sleep(.25)
        spinner.stop()
        print('Ok, thread is finished')

    def runAndContinue(self,runFunc,args):
        pass





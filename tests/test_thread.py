import time
from unittest import TestCase

from pylegos.core import Thread


class TestThread(TestCase):

    def sutWorker(self):
        time.sleep(10)


    def test_runAndWait(self):
        t = Thread()
        t.runAndWait(threadName='test', runFunc=sutWorker,args=None)
        print('finished')


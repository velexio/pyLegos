#!/usr/bin/env python
import time

from velexio.pylegos.core.threadlegos import Thread

def worker(sleepSec):
    time.sleep(sleepSec)


t = Thread()
t.runAndWait(threadName='test', runFunc=worker(10))
print('finished')

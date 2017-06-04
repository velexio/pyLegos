#!/usr/bin/env python
import time

from pylegos.core import Thread


def worker(sleepSec):
    time.sleep(sleepSec)


t = Thread()
t.runAndWait(threadName='test', runFunc=worker(10))
print('finished')

#!/usr/bin/env python
import sys
import time
import random
from progress.spinner import Spinner
from progress.spinner import MoonSpinner
from progress.spinner import PieSpinner
from progress.spinner import LineSpinner
from progress.bar import IncrementalBar

state='Running'
spinner = LineSpinner('Running ')
counter=0
while state != 'FINISHED':
    # Do some work
    time.sleep(.1)
    spinner.next()
    counter += 1
    if counter > 20:
        state = 'FINISHED'
sys.stdout.write('\b'*11)
sys.stdout.flush()
sys.stdout.write('\r ')
print("Finished")
state='Running'
spinner = MoonSpinner('Running ')
counter=0
while state != 'FINISHED':
    # Do some work
    time.sleep(.1)
    spinner.next()
    counter += 1
    if counter > 20:
        state = 'FINISHED'
sys.stdout.write('\b'*11)
sys.stdout.flush()
sys.stdout.write('\r ')
print("Finished")
iCount=0
bar = IncrementalBar('Mirgrating process e_gdbgra', max=10, suffix='%(percent).1f%% - %(eta)ds')
for i in range(10):
    time.sleep(round(random.random(),1))
    bar.next()
    iCount += 1
    if iCount > 5:
        bar.message="Migrating process p_gdbgra"
bar.finish()


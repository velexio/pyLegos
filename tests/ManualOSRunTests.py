#!/usr/bin/env python2.7

from velexio.pylegos.core.class_legos import UnixOSHelper
from velexio.pylegos.core.class_legos import OSRunException

def errorCatchTest():
    cmd='/tmp/foo/script.sh'
    try:
        UnixOSHelper().run(command=cmd)
    except OSRunException as e:
        print('Caught Expected error: '+e.message)





def runTests():
    errorCatchTest()


if __name__ == '__main__':
    runTests()
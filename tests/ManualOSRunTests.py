#!/usr/bin/env python2.7

from src.velexio.pylegos.core import OSRunException
from src.velexio.pylegos.core import UnixOSHelper


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
import unittest

from unittest import TestCase



from com.velexio.pylegos.core.vx_reflection import Inspector

class sut1(object):
    def __init__(self): pass
    def getCaller(self):
        i = Inspector()
        c = i.getCaller()


def test_getCallerNoClass():
    i = Inspector()
    c = i.printCallerInfo()
    TestCase().assertEqual(c,'test_inspector.test_getCallerNoClass')

class TestInspector(unittest.TestCase):

    def test_getCaller(self):
        i = Inspector()
        c = i.printCallerInfo()
        #import pdb; pdb.set_trace()
        self.assertEqual(c,'test_inspector.TestInspector.test_getCaller','Caller is  NOT correct')



if __name__ == '__main__':
    test_getCallerNoClass()
    unittest.main()

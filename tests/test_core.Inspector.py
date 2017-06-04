from unittest import TestCase
from pylegos.core import Inspector

__package__ = 'applibs'

class TestInspector(TestCase):

    def test_getCallerFilePath(self):
        callerFile = AppClassA.callGetCallerFile()
        self.assertEqual(__file__, callerFile, 'The caller file returned is not correct')

    def test_getCaller(self):
        caller = AppClassA().callGetCaller()
        self.assertEqual('applibs.test_CoreInspector.AppClassA.callGetCaller', caller, 'The expected name of caller is incorrect')
        #caller2 = AppClassA.callStaticGetCaller()
        #self.assertEqual('applibs.test_CoreInspector.AppClassA.callStaticGetCaller', caller2, 'The expected name of caller is incorrect')

    def test_getCallerModAndClass(self):
        caller = AppClassA().callGetCallerModAndClass()
        self.assertEqual('applibs.test_CoreInspector.AppClassA', caller)
        caller2 = AppClassA().callStaticGetCallerModAndClass()
        self.assertEqual('test_CoreInspector.AppClassA', caller2)
        caller3 = AppClassA.callStaticGetCallerModAndClass()
        self.assertEqual('test_CoreInspector.AppClassA', caller3)



    '''
    def test_getCallerMod(self):
        self.fail()

    def test_getCallerFunc(self):
        self.fail()

    def test_getCallerName(self):
        self.fail()

    '''


class AppClassA:
    __package__ = 'applibs'

    @staticmethod
    def callGetCallerFile():
        alm = AppLibMock()
        return alm.askForCallerFile()

    def callGetCaller(self):
        alm = AppLibMock()
        return alm.askInspectForCaller()

    @staticmethod
    def callStaticGetCaller():
        alm = AppLibMock()
        return alm.askInspectForCaller()

    def callGetCallerModAndClass(self):
        alm = AppLibMock()
        return alm.askInspectorForCallerModAndClass()

    @staticmethod
    def callStaticGetCallerModAndClass():
        alm = AppLibMock()
        return alm.askInspectorForCallerModAndClass()


class AppClassB:

    def callGetCaller(self):
        alm = AppLibMock()
        return alm.askInspectForCaller()

    @staticmethod
    def callStaticGetCaller():
        alm = AppLibMock()
        return alm.askInspectForCaller()


def modFuncCallGetModAndClass():
    alm = AppLibMock()
    return alm.askInspectorForCallerModAndClass()


class AppLibMock:

    def askForCallerFile(self):
        callerFile = Inspector.getCallerFilePath()
        return callerFile

    def askInspectForCaller(self):
        caller = Inspector.getCaller()
        return caller

    def askInspectorForCallerModAndClass(self):
        caller = Inspector.getCallerModAndClassName()
        return caller


from unittest import TestCase
from core import App
from app_platform import PlatformProperty

class TestApp(TestCase):
    def test_getAppBase(self):
        app = App()
        base = app.getAppBase()
        baseArray = base.split(PlatformProperty.FilePathSeparator)
        print(base)
        self.assertEqual(baseArray[len(baseArray)-1], 'xdba-workbench-core')

    def test_getAppName(self):
        app = App()
        appName = app.getAppName()
        self.assertEqual(appName, 'aperos')

    def test_getAppVersion(self):
        app = App()
        appVersion = app.getAppVersion()
        self.assertEqual(appVersion, '0.2.0')

    def test_getAppLogFilename(self):
        logFilename = App().getAppLogFilename()
        fsep = PlatformProperty.FilePathSeparator
        if not str(logFilename).endswith('xdba-workbench-core'+fsep+'logs'+fsep+'aperos.log'):
            self.fail('Logfile name ['+logFilename+'] is not correct')

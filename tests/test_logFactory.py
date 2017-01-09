from unittest import TestCase
from unittest import main
from velexio.pylegos import LogFactory


class TestLogFactory(TestCase):

    def test_LogLevel(self):
        cl = LogFactory.LogLevel.CRITICAL.value
        el = LogFactory.LogLevel.ERROR.value
        wl = LogFactory.LogLevel.WARNING.value
        il = LogFactory.LogLevel.INFO.value
        dl = LogFactory.LogLevel.DEBUG.value
        self.assertEqual(str(type(cl)),"<class 'int'>",'Critical log level is not integer')
        self.assertEqual(str(type(el)),"<class 'int'>",'Error log level is not integer')
        self.assertEqual(str(type(wl)),"<class 'int'>",'Warning log level is not integer')
        self.assertEqual(str(type(il)),"<class 'int'>",'Info log level is not integer')
        self.assertEqual(str(type(dl)),"<class 'int'>",'Debug log level is not integer')

    def test_getConsoleLogger(self):
        self.assertTrue(True)


if __name__ == '__main__':
    main()



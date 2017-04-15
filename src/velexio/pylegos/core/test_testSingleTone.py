from unittest import TestCase
from velexio.pylegos.core.framework import TestSingleTone

class TestTestSingleTone(TestCase):
    def test_getAppName(self):
        s1 = TestSingleTone()
        s2 = TestSingleTone()
        s1.setAppName('FooApp')
        s1AppName = s1.getAppName()
        s2AppName = s2.getAppName()

        self.assertEqual(s1AppName, s2AppName)

from unittest import TestCase

from pylegos.core import DeprecationUtil


class TestDeprecationUtil(TestCase):
    def test_deprecate(self):
        sut = DeprecationUtil()
        #sut.initFile()
        sut.deprecate('TestClass', 'oldMethod', 'betterMethod')
        sut.deprecate('OldClass', 'oldMethod', 'betterMethod')
        sut.printUsage()

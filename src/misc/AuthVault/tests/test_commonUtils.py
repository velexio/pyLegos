from unittest import TestCase

from bin.authvault import CommonUtils


class TestCommonUtils(TestCase):
    def test_getAppBase(self):
        appBase = CommonUtils.getAppBase()
        TestCase.assertEqual(self, '/Users/gchristiansen/projects/velexio-internal/common/AuthVault', appBase, 'The expected value for app base is incorrect')

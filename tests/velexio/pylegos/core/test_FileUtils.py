from fnmatch import fnmatch
from unittest import TestCase
from os import listdir

from velexio.pylegos.core.framework import FileUtils


class TestFileUtils(TestCase):

    Sut = FileUtils()

    def test_pathUtils(self):

        pd = self.Sut.getParentDir(filePath=__file__)
        self.assertEqual('/Users/gchristiansen/projects/pyLegos/tests/velexio/pylegos/core', pd)

        pd = self.Sut.getAppBase()
        self.assertEqual('/Users/gchristiansen/projects/pyLegos/tests/velexio/pylegos',pd)

        self.assertTrue(self.Sut.dirExists('/Users/gchristiansen/projects/pyLegos'),'Method dirExists determined existing dir does not exist')
        self.assertFalse(self.Sut.dirExists('/Users/gchristiansen/projects/pyLegos/xxxpylegos'),'Method dirExists returned True on a non-existent directory')
        self.assertFalse(self.Sut.dirExists('/Users/gchristiansen/projects/pyLegos/pylegos/tests/test_FileUtils.py'),'Method dirExists returned True on a check against a file')

        self.assertTrue(self.Sut.fileExists(__file__), 'Method fileExists returned false file that DOES exist')
        self.assertFalse(self.Sut.fileExists('/Users/gchristiansen/projects/pyLegos/tests'),'Method fileExists returned true on dir')
        self.assertFalse(self.Sut.fileExists('/Users/gchristiansen/projects/pyLegos/tests/xxxx.py'),'Method fileExists returned true file that DOES NOT exist')

        # Create some tmp dirs
        self.Sut.removeDirMatch(dirPath='/tmp', pattern='conf*')
        self.Sut.createDirectory('/tmp/conf')
        self.Sut.createDirectory('/tmp/config')

        self.assertEqual(len(self.Sut.getDirMatches(baseDir='/tmp',pattern='conf*')),2,'Method getDirMatches returns more than expected')
        self.assertEqual(self.Sut.getDirMatches(baseDir='/tmp',pattern='conf')[0],'conf','Method getDirMatches does not return full path')

    def test_DeleteFiles(self):
        testFiles = ['/tmp/app_test1', '/tmp/app_test2']
        for tf in testFiles:
            self.Sut.touchFile(tf)
        self.Sut.deleteFiles(baseDir='/tmp', pattern='app*')
        for file in listdir('/tmp'):
            if fnmatch(file, 'app*'):
                self.fail()

    def test_GetFileMatches(self):
        testFiles = ['/tmp/app_test1', '/tmp/app_test2', '/tmp/vapp_test1']
        for tf in testFiles:
            self.Sut.touchFile(tf)
        fileList = self.Sut.getFileMatches(baseDir='/tmp', pattern='app*')
        self.assertEqual(len(fileList), 2)

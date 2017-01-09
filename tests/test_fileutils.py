from unittest import TestCase
from velexio.pylegos.core.framework import FileUtils


class TestFileUtils(TestCase):

    Sut = FileUtils()

    def test_pathUtils(self):
        testFile = '/Users/gchristiansen/projects/pyLegos/tests/test_fileutils.py'

        pd = self.Sut.getParentDir(filePath=testFile)
        self.assertEqual('/Users/gchristiansen/projects/pyLegos/tests',pd)

        pd = self.Sut.getAppBase()
        self.assertEqual('/Users/gchristiansen/projects/pyLegos',pd)

        self.assertTrue(self.Sut.dirExists('/Users/gchristiansen/projects/pyLegos'),'Method dirExists determined existing dir does not exist')
        self.assertFalse(self.Sut.dirExists('/Users/gchristiansen/projects/pyLegos/xxxpylegos'),'Method dirExists returned True on a non-existent directory')
        self.assertFalse(self.Sut.dirExists('/Users/gchristiansen/projects/pyLegos/pylegos/tests/test_fileutils.py'),'Method dirExists returned True on a check against a file')

        self.assertTrue(self.Sut.fileExists('/Users/gchristiansen/projects/pyLegos/tests/test_fileutils.py'),'Method fileExists returned false file that DOES exist')
        self.assertFalse(self.Sut.fileExists('/Users/gchristiansen/projects/pyLegos/tests'),'Method fileExists returned true on dir')
        self.assertFalse(self.Sut.fileExists('/Users/gchristiansen/projects/pyLegos/tests/xxxx.py'),'Method fileExists returned true file that DOES NOT exist')

        # Create some tmp dirs
        self.Sut.rmDirMatch(dirPath='/tmp',pattern='conf*')
        self.Sut.mkdir('/tmp/conf')
        self.Sut.mkdir('/tmp/config')

        self.assertEqual(len(self.Sut.getDirMatches(baseDir='/tmp',pattern='conf*')),2,'Method getDirMatches returns more than expected')
        self.assertEqual(self.Sut.getDirMatches(baseDir='/tmp',pattern='conf')[0],'conf','Method getDirMatches does not return full path')

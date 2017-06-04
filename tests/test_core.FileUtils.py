import os
from unittest import TestCase
from core import FileUtils


class TestFileUtils(TestCase):
    def test_getParentDir(self):
        fullParentDir = FileUtils.getParentDir(__file__)
        dirArray = fullParentDir.split('\\')
        parentDirName = dirArray[len(dirArray)-1]
        self.assertEqual(parentDirName, 'applibs')
        fullParentDir2 = FileUtils.getParentDir(fullParentDir)
        dirArray2 = fullParentDir2.split('\\')
        parentDirName2 = dirArray[len(dirArray2)-1]
        self.assertEqual(parentDirName2, 'app')
        fullParentDir3 = FileUtils.getParentDir(fullParentDir2)
        dirArray3 = fullParentDir3.split('\\')
        parentDirName3 = dirArray[len(dirArray3)-1]
        self.assertEqual(parentDirName3, 'tests')

    def test_getAppBase(self):
        appBase = FileUtils().getAppBase()
        da = appBase.split(os.path.sep)
        bd = da[len(da)-1]
        self.assertEqual(bd, 'applibs', 'Fail on getAppBase')

    def test_getModuleAppBase(self):
        appBase = FileUtils().getModuleAppBase()
        da = appBase.split(os.path.sep)
        bd = da[len(da)-1]
        self.assertEqual(bd, 'tests', 'Fail on getModuleAppBase')

    def test_getAppProjectBase(self):
        appBase = FileUtils().getAppProjectBase()
        da = appBase.split(os.path.sep)
        bd = da[len(da)-1]
        self.assertEqual(bd, 'app', 'Fail on getAppProjectBase')

    def test_getModuleProjectBase(self):
        appBase = FileUtils().getModuleProjectBase()
        da = appBase.split(os.path.sep)
        bd = da[len(da)-1]
        self.assertEqual(bd, 'xdot', 'Fail on getModuleProjectBase')

    '''
    def test_dirExists(self):
        self.fail()

    def test_fileExists(self):
        self.fail()

    def test_fileMatchExist(self):
        self.fail()

    def test_dirMatchExist(self):
        self.fail()

    def test_getFileMatches(self):
        self.fail()

    def test_getDirMatches(self):
        self.fail()

    def test_mkdir(self):
        self.fail()

    def test_rmdir(self):
        self.fail()

    def test_rmDirMatch(self):
        self.fail()

    '''
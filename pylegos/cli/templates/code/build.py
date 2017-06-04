from pylegos.core import FileUtils
from pylegos.core import PlatformProperty


class AppBuilder:

    def __init__(self):
        sep = PlatformProperty.FileSep
        self.ProjectBaseDir = FileUtils.getParentDir(__file__) + sep
        projectDirArray = self.ProjectBaseDir.strip(sep).split(sep)
        self.ProjectName = projectDirArray[len(projectDirArray) - 1].lower()
        self.DistDir = self.ProjectBaseDir+'dist'+sep

        if not FileUtils().dirExists(self.DistDir):
            FileUtils().createDir(self.DistDir)
            FileUtils().touchFile(self.DistDir+'build.log')

    def __buildDatabaseScripts(self):
        pass

    def buildApp(self):
        pass

    def buildInstaller(self):
        pass


if __name__ == '__main__':
    appBuilder = AppBuilder()
    appBuilder.buildApp()
    appBuilder.buildInstaller()

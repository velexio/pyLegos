from pylegos.cli.pycli_services import ProjectService
from pylegos.cli.pycli_services import ModuleService
from pylegos.cli.pycli_services import ModelService


class ProjectController:

    def __init__(self, projectName):
        self.ProjectName = projectName.lower()
        self.Service = ProjectService(name=self.ProjectName)

    def initProject(self, isSimple):
        self.Service.initProject(simpleProject=isSimple)

    def modularize(self):
        self.Service.modularize()


class ModuleController:

    def __init__(self, moduleName):
        self.ModuleName = moduleName.lower()
        self.Service = ModuleService(moduleName=self.ModuleName)

    def addModule(self):
        self.Service.initModule()


class ModelController:

    def __init__(self):
        self.Service = ModelService(modelName=self.ModelName)

    def createDef(self, moduleName):
        pass

    def addModel(self, defFilename, persistent, forceAdd):
        pass

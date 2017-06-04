from pylegos.core import App
from pylegos.core import ModuleClass


class ModuleController:
    """
    This class is for putting logic that control the entire module.  Always call the standard 'initModule()'. Method before calling
    any other controllers.
    """
    @staticmethod
    def initModule():
        """
        This will 'initialize' the module with the pylegos framework.  Call this as early in program execution as possible.
        """
        App().injectModule()


'''
REMOVE THIS CLASS AT ANYTIME.  HERE FOR EXAMPLE PURPOSE ONLY
'''
class ExampleController(ModuleClass):

    def __init__(self):
        ModuleClass.__init__(className='ExampleController')

    def foo(self):
        self.logger.debug('Parent class has a logger')
        pass

'''
-- PUT CONTROLLER CLASSES IN THIS MODULE --
'''

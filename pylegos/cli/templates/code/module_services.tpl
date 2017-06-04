from pylegos.core import ModuleClass


'''
REMOVE THIS CLASS AT ANYTIME.  HERE FOR EXAMPLE PURPOSE ONLY
'''
class ExampleService(ModuleClass):

    def __init__(self):
        ModuleClass.__init__(className='ExampleService')

    def foo(self):
        self.logger.debug('Parent class has a logger, so you do not need to instantiate, just call')

'''
-- PUT SERVICE CLASSES IN THIS MODULE --
'''
'''Module to hold various dev/design pattern classes (i.e. singleton)

'''
class Singleton(type):
    '''Use to create a singleton class
    '''
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
            return cls.__instance
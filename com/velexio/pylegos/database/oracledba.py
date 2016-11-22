'''
Created on Sep 19, 2016

@author: a597485
'''
from com.velexio.pylegos.database.oracle.database import Database
from com.velexio.pylegos.database.oracle.database import TablespaceContentType


class Admin(object):
    '''
    classdocs
    '''
    database = None

    def __init__(self, database):
        '''
        Constructor
        '''
        self.database = database

    '''
    this is a test
    '''

    def createUser(self, username, password, defaultTablespace=None, defaultTempTablespace=None, profile='DEFAULT'):
        userPermTBS = defaultTablespace
        userTempTBS = defaultTempTablespace

        if defaultTablespace is None:
            userPermTBS = self.database.getDefaultTablespace(type=TablespaceContentType.Permanent)

        if defaultTempTablespace is None:
            userTempTBS = self.database.getDefaultTablespace(type=TablespaceContentType.Temporary)

        ddl = ("create user " + username + " identified by " + password + " "
               "default tablespace " + userPermTBS + " "
               "temporary tablespace " + userTempTBS + " "
               "profile " + profile + " "
               "account unlock")

        self.database.execute(ddl);

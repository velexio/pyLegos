'''
Created on Sep 19, 2016

@author: Gerry Christiansen <gchristiansen@velexio.com>
'''
import cx_Oracle
import sys
from collections import OrderedDict
from velexio.pylegos.core.framework import LogFactory

'''
-----------------------
ENUM Type Classes
-----------------------
'''


class DatabaseProperty(object):
    NAME = 'name'
    DBID = 'dbid'


class TablespaceContentType(object):
    Permanent = 1
    Temporary = 2


class CxOracleType(object):
    Varchar2 = "<class 'cx_Oracle.STRING'>"
    Number = "<class 'cx_Oracle.NUMBER'>"
    Date = "<class 'cx_Oracle.DATETIME'>"
    Timestamp = "<class 'cx_Oracle.TIMESTAMP'>"

    def __str__(self):
        return "{0}".format(self.value)

'''
-----------------------
END of ENUM Type Classes
-----------------------
'''

class Database(object):
    """This represents an oracle database object.  Use this object to perform data operations against the database (i.e dml)
    """

    def __init__(self):
        """Constructor takes no arguments, just instantiates the logger object
        """

        self.Connection = None
        self.Logger = LogFactory().getLibLogger()

    class OracleDataType(object):
        NUMBER = cx_Oracle.NUMBER



    def connect(self, username, password, connectString, asSysdba=False):
        """
        This method will create a connection to the database. Before you can call any other method, a connection must be established
        <br>
        :param username: The username to use for the connection <br>
        :param password: The password for the connection <br>
        :param connectString: The connection string in the format of db-host:port/service_name or db-host:port:sid <br>
        :param asSysdba: Boolean (True|False) for whether connection should be made as sysdba.  Default is False <br>
        :return: None <br>
        """
        try:
            if asSysdba:
                self.Connection = cx_Oracle.connect(user=username,
                                                    password=password,
                                                    dsn=connectString,
                                                    mode=cx_Oracle.SYSDBA)
            else:
                self.Connection = cx_Oracle.connect(username, password, connectString)
        except cx_Oracle.DatabaseError:
            raise DatabaseConnectionException()


    def disconnect(self):
        """
        This method will close the connection now rather than when application terminates and/or Database object is garbage collected.
        :return: None
        """
        self.Connection.close()

    def generateRSMetadata(self, cursor):
        cursorDesc = cursor.description
        fieldNumber = 0
        cursorMetadata = OrderedDict()
        for field in cursorDesc:
            metadataRecord = {}
            metadataRecord['FieldNumber'] = fieldNumber
            metadataRecord['DataType'] = field[1]
            metadataRecord['MaxSize'] = len(str(field[0]))
            metadataRecord['Scale'] = field[5]
            cursorMetadata[field[0]] = metadataRecord
            fieldNumber += 1

        return cursorMetadata

    def getResultSetObject(self, query, bindValues=[]):
        formatedResults = self.getQueryResult(query=query, bindValues=bindValues)
        resultSetObj = ResultSet(formatedResults)
        return resultSetObj

    def queryForSingleValue(self, query, columnName, bindValues=[]):
        retVal = None
        res = self.getQueryResult(query=query, bindValues=bindValues)
        if len(res) > 1:
            retVal = res[1][str(columnName).upper()]

        return retVal

    def getQueryResult(self, query, bindValues=[]):
        formattedResultSet = OrderedDict()
        formattedRowNumber = 1
        cursor = self.Connection.cursor()
        cursor.execute(query, bindValues)

        curMeta = self.generateRSMetadata(cursor=cursor)

        rawResultSet = cursor.fetchall()

        for row in rawResultSet:
            formattedRec = {}
            for field in curMeta:
                rowVal = row[curMeta[field]['FieldNumber']]
                formattedRec[field] = rowVal
                '''
                Determine if maxVal needs increase
                '''
                if (len(str(rowVal)) > curMeta[field]['MaxSize']) or (
                        len(str(rowVal)) == curMeta[field]['MaxSize'] and curMeta[field]['Scale'] > 0):
                    if curMeta[field]['Scale'] > 0:
                        curMeta[field]['MaxSize'] = len(str(rowVal)) + 1
                    elif curMeta[field]['DataType'] == str(CxOracleType.Timestamp):
                        curMeta[field]['MaxSize'] = 26
                    else:
                        curMeta[field]['MaxSize'] = len(str(rowVal))

            formattedResultSet[formattedRowNumber] = formattedRec
            formattedRowNumber += 1

        formattedResultSet[0] = curMeta;

        return formattedResultSet

    def execDML(self, dml, bindValues=[]):
        """
        This function is to be used to call any dml operation (insert,update,delete). It can also
        be used to run an anonymous pl/sql block.  If you want to execute a stored pl/sql procedure
        or function, use the executePL subtroutine
        """
        cursor = self.Connection.cursor()
        cursor.execute(dml, bindValues)

    def execProc(self, procedureName, parameters=[], namedParameters={}, inOutParams={}):
        pass

    def execFunc(self, functionName, oracleReturnType, parameters=[], namedParameters={}):
        cursor = self.Connection.cursor()
        retValue = cursor.callfunc(functionName,
                                   oracleReturnType,
                                   parameters)
        return retValue

    def commit(self):
        self.Connection.commit();

    def rollback(self):
        self.Connection.rollback();

    def getDefaultTablespace(self, type=TablespaceContentType.Permanent):
        if type is TablespaceContentType.Permanent:
            query = ("select property_value "
                     "from database_properties "
                     "where property_name = 'DEFAULT_PERMANENT_TABLESPACE'")
        elif type is TablespaceContentType.Temporary:
            query = ("select property_value "
                     "from database_properties "
                     "where property_name = 'DEFAULT_TEMP_TABLESPACE'")
        else:
            '''
            todo: raise exception/error
            '''
            return None

        res = self.queryForSingleValue(query=query, columnName='PROPERTY_VALUE')
        return res

    def getProperty(self, property=DatabaseProperty.NAME):
        query = "select " + property.value + " from v$database"
        res = self.queryForSingleValue(query=query, columnName=property.value)
        return res


class ResultSet(object):
    formattedResultSet = None

    def __init__(self, resultSet):
        self.formattedResultSet = resultSet

    def convertDatatypeForPrint(self, oracleType, scale=0):
        if (str(oracleType)) == CxOracleType.Number:
            if scale > 0:
                return 'f'
            else:
                return 'd'
        elif str(oracleType) == CxOracleType.DateTime:
            return 't'
        else:
            return 's'

    def printRecordDelimeter(self, metaData):
        maxLineWidth = 0

        for header in metaData:
            maxLineWidth += metaData[header]['MaxSize'] + 1

        sys.stdout.write("{v:{w}s}".format(v='-' * (maxLineWidth + 1), w=maxLineWidth))

    def printResultSet(self):
        metadataRow = self.formattedResultSet[0]
        fd = "|"
        '''
        PRINT  HEADER ROW
        '''
        self.printRecordDelimeter(metaData=metadataRow)
        sys.stdout.write() (fd)
        for header in metadataRow:
            fieldWidth = metadataRow[header]['MaxSize']
            sys.stdout.write("{v:{w}s}|".format(v=header, w=fieldWidth, d=fd))

            sys.stdout.write("\n")
            self.printRecordDelimeter(metaData=metadataRow)
            del self.formattedResultSet[0]

            for row in self.formattedResultSet:
                sys.stdout.write(fd)
                for header in metadataRow:
                    fieldWidth = metadataRow[header]['MaxSize']
                    fieldType = str(metadataRow[header]['DataType'])
                    scaleValue = metadataRow[header]['Scale']
                    fieldValue = self.formattedResultSet[row][header]

                    if fieldValue is None:
                        fieldValue = ""
                        fieldType = str(CxOracleType.Varchar2)
                    if fieldType == str(CxOracleType.Number) and scaleValue > 0:
                        sys.stdout.write(
                        "{v:{w}.{s}{t}}|".format(v=fieldValue, w=fieldWidth, t='f', s=scaleValue))
                        sys.stdout.flush()
                    elif fieldType == str(CxOracleType.Number):
                        sys.stdout.write(
                        "{v:{w}{t}}|".format(v=fieldValue, w=fieldWidth, t='d', s=scaleValue))
                        sys.stdout.flush()
                    elif fieldType == str(CxOracleType.Date):
                        printValue = fieldValue.strftime("%m.%d.%Y %H:%M:%S")
                        sys.stdout.write("{v:{w}{t}}|".format(v=printValue, w=fieldWidth, t='s'))
                        sys.stdout.flush()
                    elif fieldType == str(CxOracleType.Timestamp):
                        printValue = fieldValue.strftime("%m.%d.%Y %H:%M:%S:%f")
                        sys.stdout.write("{v:{w}{t}}|".format(v=printValue, w=fieldWidth, t='s'))
                        sys.stdout.flush()
                    else:
                        sys.stdout.write("{v:{w}{t}}|".format(v=fieldValue, w=fieldWidth, t='s'))
                        sys.stdout.write('\n')
                        sys.stdout.flush()


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

        self.database.execDML(ddl);

class DatabaseConnectionException(Exception):
    def __init__(self):
        self.message = "Unable to connect to database"
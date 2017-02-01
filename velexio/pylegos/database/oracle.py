'''
Created on Sep 19, 2016

@author: Gerry Christiansen <gchristiansen@velexio.com>
'''
import cx_Oracle
import sys
import re
from collections import OrderedDict
from velexio.pylegos.core.framework import LogFactory

'''
-----------------------
ENUM Type Classes
-----------------------
'''




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
        self.logger = LogFactory().getLibLogger()

    class DataType(object):
        NUMBER = cx_Oracle.NUMBER

    class DatabaseProperty(object):
        NAME = 'name'
        DBID = 'dbid'

    class TablespaceContentType(object):
        Permanent = 1
        Temporary = 2

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
        if self.Connection is None:
            self.logger.debug('Connecting to database with connect string ['+connectString+']')
            try:
                if asSysdba:
                    self.logger.debug('Connecting as sysdba')
                    self.Connection = cx_Oracle.connect(user=username,
                                                        password=password,
                                                        dsn=connectString,
                                                        mode=cx_Oracle.SYSDBA)
                else:
                    self.Connection = cx_Oracle.connect(username, password, connectString)
            except cx_Oracle.DatabaseError as e:
                raise DatabaseConnectionException(e)
        else:
            self.logger.debug('Connection already active, not creating an additional connection')

    def disconnect(self):
        """
        This method will close the connection now rather than when application terminates and/or Database object is garbage collected.
        :return: None
        """
        if self.Connection is not None:
            self.Connection.close()
            self.Connection = None

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

    def queryForSingleValue(self, query, columnName, bindValues=[], secureLog=False):
        retVal = None
        res = self.getQueryResult(query=query, bindValues=bindValues)
        if len(res) > 1:
            retVal = res[1][str(columnName).upper()]

        return retVal

    def getQueryResult(self, query, bindValues=[], secureLog=False):
        formattedResultSet = OrderedDict()
        formattedRowNumber = 1
        try:
            cursor = self.Connection.cursor()
            self.logger.debug('Running query: '+query)
            if not secureLog:
                self.logger.debug('Bind values for above query are '+str(bindValues))
            self.logger.debug('Executing query')
            if not secureLog:
                self.logger.debug('Session effective query user (current_schema) is ['+self.Connection.current_schema+']')
            cursor.execute(query, bindValues)
            self.logger.debug('Generating Resultset Metadata')
            curMeta = self.generateRSMetadata(cursor=cursor)
            self.logger.debug('Fetching all records')
            rawResultSet = cursor.fetchall()
            self.logger.debug('Formatting resultset')
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
            self.logger.debug('Returning resultset with ['+str(len(formattedResultSet)-1)+'] records')
            return formattedResultSet
        except cx_Oracle.DatabaseError as e:
            self.logger.debug('Hit cx_oracle DatabaseError: '+str(e))
            raise DatabaseQueryException(e)

    def getColumnMungedResultset(self, query, bindValues=[], colDelimiter='', secureLog=False):
        queryResult = self.getQueryResult(query=query, bindValues=bindValues, secureLog=secureLog)
        rsMeta = queryResult[0]
        resultSet = []
        self.logger.debug('Munging column values of resultset')
        for i in range(1,len(queryResult)):
            mungedColData = ''
            for k,v in rsMeta.iteritems():
                colVal = str(queryResult[i][k])
                mungedColData += colVal+colDelimiter
            trimmedColData = mungedColData[:len(mungedColData)-len(colDelimiter)]
            resultSet.append(trimmedColData)
        if not secureLog:
            self.logger.debug('Returning munged resultset: '+str(resultSet))
        return resultSet

    def getColumnDelimitedResultset(self, query, bindValues=[], fieldDelimiter=',', secureLog=False):
        queryResult = self.getQueryResult(query=query, bindValues=bindValues, secureLog=secureLog)
        rsMeta = queryResult[0]
        resultSet = []
        self.logger.debug('Generating record set with field delimiter [' + fieldDelimiter + ']')
        for i in range(1,len(queryResult)):
            recordData = ''
            for k,v in rsMeta.iteritems():
                colVal = str(queryResult[i][k])
                recordData += colVal + fieldDelimiter
            # NEED TO REMOVE THE TRAILING DELIMETER
            recordData = recordData[:len(recordData)-1]
            resultSet.append(recordData)
        if not secureLog:
            self.logger.debug('Returning resultset: '+str(resultSet))
        return resultSet

    def execDML(self, dml, bindValues=[]):
        """
        This function is to be used to call any dml operation (insert,update,delete). It can also
        be used to run an anonymous pl/sql block.  If you want to execute a stored pl/sql procedure
        or function, use the executePL subtroutine
        """
        try:
            cursor = self.Connection.cursor()
            cursor.execute(dml, bindValues)
        except cx_Oracle.DatabaseError as e:
            self.logger.debug('Hit cx_oracle DatabaseError: '+str(e))
            raise DatabaseDMLException(e)

    def execProc(self, procedureName, parameters=[], namedParameters={}, outParam=None):
        try:
            cursor = self.Connection.cursor()
            cursor.callproc(name=procedureName,
                            parameters=parameters,
                            keywordParameters=namedParameters)
            if outParam is not None:
                return outParam
        except cx_Oracle.DatabaseError as e:
            self.logger.debug('Hit cx_oracle DatabaseError: '+str(e))
            raise DatabaseDMLException(e)

    def execFunc(self, functionName, oracleReturnType, parameters=[], namedParameters={}):
        try:
            cursor = self.Connection.cursor()
            retValue = cursor.callfunc(name=functionName,
                                       returnType=oracleReturnType,
                                       parameters=parameters,
                                       keywordParameters=namedParameters)
            return retValue
        except cx_Oracle.DatabaseError as e:
            self.logger.debug('Hit cx_oracle DatabaseError: '+str(e))
            raise DatabaseDMLException(e)

    def commit(self):
        try:
            self.Connection.commit();
        except cx_Oracle.DatabaseError as e:
            self.logger.debug('Hit cx_oracle DatabaseError: '+str(e))
            raise DatabaseDMLException(e)

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
    """
    This exeception will be thrown if there is an issue connecting to the database. The
    exception will have the following attributes that can be used
    """

    def __init__(self, cxExceptionObj):
        self.message = str(cxExceptionObj)
        self.ErrCode = self.message.split(':')[0]
        self.__defineMessage()

    def __defineMessage(self):
        self.ErrMessage = 'ERROR: '
        if self.ErrCode == 'ORA-01017':
            self.ErrName = 'InvalidLoginCreds'
            self.ErrMessage += '['+self.ErrName+']['+self.ErrCode+'] - The credentials used are not valid'
        elif self.ErrCode == 'ORA-12154':
            self.ErrName = 'InvalidHost'
            self.ErrMessage += '['+self.ErrName+']['+self.ErrCode+'] - The host name used in the connection string is not correct or cannot be resolved'
        elif self.ErrCode == 'ORA-12514':
            self.ErrName = 'InvalidService'
            self.ErrMessage += '['+self.ErrName+']['+self.ErrCode+'] - The service name used in the connection string is not correct or is not running on the database server'
        elif self.ErrCode == 'ORA-12541':
            self.ErrName = 'NoListener'
            self.ErrMessage += '['+self.ErrName+']['+self.ErrCode+'] - The database listener did not respond. Verify the port is correct and all firewall ports are open between client and database server'
        else:
            self.ErrName = 'Undefined'
            self.ErrMessage += '['+self.ErrName+']['+self.ErrCode+'] - '+self.message


class DatabaseQueryException(Exception):

    def __init__(self, cxExceptionObj):
        self.message = str(cxExceptionObj)
        self.ErrCode = self.message.split(':')[0]
        self.__defineMessage()

    def __defineMessage(self):
        self.ErrMessage = 'ERROR: '
        if self.ErrCode == 'ORA-00942':
            self.ErrName = 'TableMissing'
            self.ErrMessage += '['+self.ErrName+']['+self.ErrCode+'] - The table referenced does not exist or your session user lacks privileges'
        else:
            self.ErrName = 'Undefined'
            self.ErrMessage += '['+self.ErrName+']['+self.ErrCode+'] - '+self.message


class DatabaseDMLException(Exception):
    def __init__(self, cxExceptionObj):
        self.message = str(cxExceptionObj)
        self.ErrCode = str(cxExceptionObj).split(':')[0]
        self.__defineMessage()

    def __defineMessage(self):
        objName = self.__extractObjectName()
        self.ErrMessage = 'ERROR: '
        if self.ErrCode == 'ORA-00001':
            self.ErrName = 'UniqueViolated'
            self.ErrMessage += '['+self.ErrName+']['+self.ErrCode+'] - The operation could not be performed as it would violate the unique constraint ['+objName+']'
        elif self.ErrCode == 'ORA-01400':
            self.ErrName = 'NotNullViolated'
            self.ErrMessage += '['+self.ErrName+']['+self.ErrCode+'] - The field '+objName+' must be assigned a value before the record can be saved'
        else:
            self.ErrName = 'Undefined'
            self.ErrMessage += '['+self.ErrName+']['+self.ErrCode+'] - '+self.message

    def __extractObjectName(self):
        objectName = 'Undefined'
        matchObj = re.match(r'ORA-\d+:\s[a-zA-Z0-9\s]+\(([A-Z0-9."#_]+)\)', self.message)
        if matchObj.groups():
            objectName = matchObj.group(1).replace('"','')
        self.ConstraintName=objectName
        return objectName


'''
Created on Sep 19, 2016

@author: Gerry Christiansen <gchristiansen@velexio.com>
'''
import json
import re
import sys
from collections import OrderedDict

import cx_Oracle

from pylegos.core import DeprecationUtil
from pylegos.core import LogFactory


class DatabaseProperty(object):
    """Enum type class that matches the v$database dictionary view.
    This class is used for parameter passing to the Database.getProperty function call
    which will return the value of the column 'property'.
    """
    DBID = 'DBID'
    NAME = 'NAME'
    CREATED = 'CREATED'
    RESETLOGS_CHANGE  = 'RESETLOGS_CHANGE#'
    RESETLOGS_TIME = 'RESETLOGS_TIME'
    PRIOR_RESETLOGS_CHANGE = 'PRIOR_RESETLOGS_CHANGE#'
    PRIOR_RESETLOGS_TIME = 'PRIOR_RESETLOGS_TIME'
    LOG_MODE = 'LOG_MODE'
    CHECKPOINT_CHANGE = 'CHECKPOINT_CHANGE#'
    ARCHIVE_CHANGE = 'ARCHIVE_CHANGE#'
    CONTROLFILE_TYPE = 'CONTROLFILE_TYPE'
    CONTROLFILE_CREATED = 'CONTROLFILE_CREATED'
    CONTROLFILE_SEQUENCE = 'CONTROLFILE_SEQUENCE#'
    CONTROLFILE_CHANGE = 'CONTROLFILE_CHANGE#'
    CONTROLFILE_TIME = 'CONTROLFILE_TIME'
    OPEN_RESETLOGS = 'OPEN_RESETLOGS'
    VERSION_TIME = 'VERSION_TIME'
    OPEN_MODE = 'OPEN_MODE'
    PROTECTION_MODE = 'PROTECTION_MODE'
    PROTECTION_LEVEL = 'PROTECTION_LEVEL'
    REMOTE_ARCHIVE = 'REMOTE_ARCHIVE'
    ACTIVATION = 'ACTIVATION#'
    SWITCHOVER = 'SWITCHOVER#'
    DATABASE_ROLE = 'DATABASE_ROLE'
    ARCHIVELOG_CHANGE = 'ARCHIVELOG_CHANGE#'
    ARCHIVELOG_COMPRESSION = 'ARCHIVELOG_COMPRESSION'
    SWITCHOVER_STATUS = 'SWITCHOVER_STATUS'
    DATAGUARD_BROKER = 'DATAGUARD_BROKER'
    GUARD_STATUS = 'GUARD_STATUS'
    SUPPLEMENTAL_LOG_DATA_MIN = 'SUPPLEMENTAL_LOG_DATA_MIN'
    SUPPLEMENTAL_LOG_DATA_PK = 'SUPPLEMENTAL_LOG_DATA_PK'
    SUPPLEMENTAL_LOG_DATA_UI = 'SUPPLEMENTAL_LOG_DATA_UI'
    FORCE_LOGGING = 'FORCE_LOGGING'
    PLATFORM_ID = 'PLATFORM_ID'
    PLATFORM_NAME = 'PLATFORM_NAME'
    RECOVERY_TARGET_INCARNATION = 'RECOVERY_TARGET_INCARNATION#'
    LAST_OPEN_INCARNATION = 'LAST_OPEN_INCARNATION#'
    CURRENT_SCN = 'CURRENT_SCN'
    FLASHBACK_ON = 'FLASHBACK_ON'
    SUPPLEMENTAL_LOG_DATA_FK = 'SUPPLEMENTAL_LOG_DATA_FK'
    SUPPLEMENTAL_LOG_DATA_ALL = 'SUPPLEMENTAL_LOG_DATA_ALL'
    DB_UNIQUE_NAME = 'DB_UNIQUE_NAME'
    STANDBY_BECAME_PRIMARY_SCN = 'STANDBY_BECAME_PRIMARY_SCN'
    FS_FAILOVER_STATUS = 'FS_FAILOVER_STATUS'
    FS_FAILOVER_CURRENT_TARGET = 'FS_FAILOVER_CURRENT_TARGET'
    FS_FAILOVER_THRESHOLD = 'FS_FAILOVER_THRESHOLD'
    FS_FAILOVER_OBSERVER_PRESENT = 'FS_FAILOVER_OBSERVER_PRESENT'
    FS_FAILOVER_OBSERVER_HOST = 'FS_FAILOVER_OBSERVER_HOST'
    CONTROLFILE_CONVERTED = 'CONTROLFILE_CONVERTED'
    PRIMARY_DB_UNIQUE_NAME = 'PRIMARY_DB_UNIQUE_NAME'
    SUPPLEMENTAL_LOG_DATA_PL = 'SUPPLEMENTAL_LOG_DATA_PL'
    MIN_REQUIRED_CAPTURE_CHANGE = 'MIN_REQUIRED_CAPTURE_CHANGE#'
    CDB = 'CDB'
    CON_ID = 'CON_ID'
    PENDING_ROLE_CHANGE_TASKS = 'PENDING_ROLE_CHANGE_TASKS'
    CON_DBID = 'CON_DBID'
    FORCE_FULL_DB_CACHING = 'FORCE_FULL_DB_CACHING'


class TablespaceContentType(object):
    """This is a subclass of Database and is a static, enum type class that defines
    two tablespace content types

    `Permanent` is a tablespace that holds tables

    `Temporary` Indicates a tablespace of type temporary
    """
    Permanent = 1
    Temporary = 2


class CxOracleType:
    """This class is an enum type class
    that is useful for testing vars against
     various cx_Oracle datatypes"""
    NUMBER = "<class 'cx_Oracle.NUMBER'>"
    STRING = "<class 'cx_Oracle.STRING'>"
    DATETIME = "<class 'cx_Oracle.DATETIME'>"
    TIMESTAMP = "<class 'cx_Oracle.TIMESTAMP'>"
    LOB = "<class 'cx_Oracle.LOB'>"
    CLOB = "<class 'cx_Oracle.CLOB'>"
    BLOB = "<class 'cx_Oracle.BLOB'>"


class Database(object):
    """This represents an oracle database object.  Use this object to perform data operations against the database (i.e dml)
    """

    def __init__(self):
        """Constructor takes no arguments, just instantiates the logger object
        """
        self.Connection = None
        self.logger = LogFactory().getLibLogger()

    @staticmethod
    def __buildConnectString(connectString):
        connectDsn = None
        sidStyleRegexMatch = '[a-zA-Z0-9-_.]+:\d+:[a-zA-Z\d._#$]+'
        sidStyleExtractRegex = '([a-zA-Z0-9-_.]+):(\d+):([a-zA-Z0-9-_.]+)'
        serviceStyleRegexMatch = '[a-zA-Z0-9-_.]+:\d+/[a-zA-Z\d._#$]+'
        serviceStyleExtractRegex = '([a-zA-Z0-9-_.]+):(\d+)/([a-zA-Z0-9-_.]+)'

        if re.match(sidStyleRegexMatch, connectString):
            host = re.match(sidStyleExtractRegex, connectString).group(1)
            port = re.match(sidStyleExtractRegex, connectString).group(2)
            sid = re.match(sidStyleExtractRegex, connectString).group(3)
            connectDsn = cx_Oracle.makedsn(host=host, port=port, sid=sid)
        elif re.match(serviceStyleRegexMatch, connectString):
            host = re.match(serviceStyleExtractRegex, connectString).group(1)
            port = re.match(serviceStyleExtractRegex, connectString).group(2)
            serviceName = re.match(serviceStyleExtractRegex, connectString).group(3)
            connectDsn = cx_Oracle.makedsn(host=host, port=port, service_name=serviceName)
        else:
            raise DatabaseConnectionException('The format of the connection string passed [] cannot be parsed')
        return connectDsn

    @staticmethod
    def __generateRSMetadata(cursor):
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

    def __mungeColumns(self, resultSet, colDelimiter='|::|', secureLog=False):
        rsMeta = resultSet[0]
        mungedResultSet = [rsMeta]
        self.logger.debug('Munging column values of resultset')
        for i in range(1, len(resultSet)):
            mungedColData = ''
            for k, v in rsMeta.iteritems():
                colVal = str(resultSet[i][k])
                mungedColData += colVal + colDelimiter
            trimmedColData = mungedColData[:len(mungedColData) - len(colDelimiter)]
            mungedResultSet.append(trimmedColData)
        if not secureLog:
            self.logger.debug('Returning munged resultset: ' + str(mungedResultSet))
        return mungedResultSet
    
    def sessionPool(self, username, password, connectString, min=5, max=50, increment=5):
        """
        `BETA`

        This will return a pool of connections.

        `username:` The user name that will be used to make the connections to the database

        `password:` The password of the user for connections

        `connectString:` The connection string. Valid formats are <host>:<port>/<service_name> and <host>:<port>:<sid>

        `min:` The number of connections to start and always keep in the pool

        `max:` The maximum number of connections that can be created in the session pool

        `increment:` How many connections should be created when all connections in the pool are busy.

        `Returns:` SessionPool object that can be used to get connections

        """
        connectDsn = self.__buildConnectString(connectString=connectString)
        pool = cx_Oracle.SessionPool(user=username,
                                     password=password,
                                     database=connectDsn,
                                     min=min,
                                     max=max,
                                     increment=increment)
        return pool

    def connect(self, username, password, connectString, asSysDBA=False):
        """
        This method will create a connection to the database. Before you can call any other method, a connection must be established

        `username` The username to use for the connection

        `password` The password for the connection

        `connectString` The connection string in the format of db-host:port/service_name or db-host:port:sid

        `asSysDBA` Boolean (True|False) for whether connection should be made as sysdba.  Default is False
        """
        if self.Connection is None:
            self.logger.debug('Connecting to database with connect string ['+connectString+']')
            connectDsn = self.__buildConnectString(connectString=connectString)
            try:
                if asSysDBA:
                    self.logger.debug('Connecting as sysdba')
                    self.Connection = cx_Oracle.connect(user=username,
                                                        password=password,
                                                        dsn=connectDsn,
                                                        mode=cx_Oracle.SYSDBA)
                else:
                    self.Connection = cx_Oracle.connect(user=username,
                                                        password=password,
                                                        dsn=connectDsn)
            except cx_Oracle.DatabaseError as e:
                raise DatabaseConnectionException(e)
        else:
            self.logger.debug('Connection already active, not creating an additional connection')

    def disconnect(self):
        """
        This method will close the connection now rather than when application terminates and/or Database object is garbage collected.
        """
        if self.Connection is not None:
            self.Connection.close()
            self.Connection = None

    def getValue(self, query, bindValues=[], namedBinds={}, secureLog=False):
        """
        At times you want to simply get the raw value of a single row, single column query.  When this is
        the case, the use of the `pylegos.database.oracle.Database.getResultSet` may be overkill.  This method is
        designed to more efficiently get data for this use case.

        `query: ` The query to run.  It is expected that this query will only return a single row.  This is not a
        strict rule.  The first column of the first record is the data that is returned.

        `bindValues: ` List object containing the positional value for each bind variable

        `namedBinds: ` Dictionary object containing the name/value pairs for the bind variables in the query

        `secureLog: ` Sometimes there will be security sensitive data as part of either the query or result set.  If so,
                      set this to True, so that neither the query or resultset are logged. Only high level names of
                      operations will be logged.

        `Returns:` String

        """
        bindInput = bindValues
        if len(namedBinds) > 0:
            bindInput = namedBinds

        self.logger.debug('Running query to get single value result')
        if not secureLog:
            self.logger.debug('Executing query ['+query+']')
        cur = self.Connection.cursor()
        cur.execute(query, bindInput)
        retVal = cur.fetchone()[0]
        if not secureLog:
            self.logger.debug('Single value return is ['+retVal+']')
        return str(retVal)

    def getResultSet(self, query, bindValues=[], namedBinds={}, mungeColumns=False, fieldDelimiter=',',
                     secureLog=False, returnRaw=False):
        """
        Primary method for retrieval of data from the database. By default, this will return an instance of
        `pylegos.database.oracle.ResultSet`.  This object holds all the data with methods for different types of
        retrieval.

        Use of bind variables is encouraged and can be passed in via one of two methods. 1) Positional values by using
        the bindValues parameter and 2) Named variable/value pairs via the namedBinds parameter.  These two
        parameters are mutually exclusive.

        `query: ` The query to run

        `bindValues: ` List object containing the positional value for each bind variable

        `namedBinds: ` Dictionary object containing the name/value pairs for the bind variables in the query

        `mungeColumns: ` Optional boolean parameter that will "munge" columns using the value of the fieldDelimiter
                         parameter.  Example usage would be for creating a CSV file.

        `fieldDelimiter: ` The delimiter to use when munging columns together into a single value

        `secureLog: ` Sometimes there will be security sensitive data as part of either the query or result set.  If so,
                      set this to True, so that neither the query or resultset are logged. Only high level names of
                      operations will be logged.

        `returnRaw: ` Boolean to indicate that raw results should be returned rather than an instance of
                      `pylegos.database.oracle.ResultSet`.  Here for mostly for backward compatability, but not yet
                      deprecated.

        `Returns:` `pylegos.database.oracle.ResultSet`

        """
        rawResultSet = OrderedDict()
        formattedRowNumber = 1
        try:
            cursor = self.Connection.cursor()
            self.logger.debug('Running query: '+query)
            if not secureLog:
                self.logger.debug('Bind values for above query are '+str(bindValues))
            self.logger.debug('Executing query')
            if not secureLog:
                self.logger.debug('Session effective query user (current_schema) is ['+str(self.Connection.current_schema)+']')
            cursor.execute(query, bindValues)
            self.logger.debug('Generating Resultset Metadata')
            curMeta = self.__generateRSMetadata(cursor=cursor)
            self.logger.debug('Fetching all records')
            recordSet = cursor.fetchall()
            self.logger.debug('Formatting resultset')
            for row in recordSet:
                formattedRec = {}
                for field in curMeta:
                    rowVal = row[curMeta[field]['FieldNumber']]
                    formattedRec[field] = rowVal
                    '''
                    Determine if maxVal needs increase
                    '''
                    dataType = str(curMeta[field]['DataType'])
                    if dataType == "<class 'cx_Oracle.CLOB'>":
                        curMeta[field]['MaxSize'] = 100
                    else:
                        rowValLen = len(rowVal)
                        if rowValLen > curMeta[field]['MaxSize']:
                            curMeta[field]['MaxSize'] = rowValLen

                rawResultSet[formattedRowNumber] = formattedRec
                formattedRowNumber += 1

            rawResultSet[0] = curMeta
            if mungeColumns:
                rawResultSet = self.__mungeColumns(resultSet=rawResultSet,
                                                   colDelimiter=fieldDelimiter,
                                                   secureLog=secureLog)

            self.logger.debug('Returning resultset with ['+str(len(rawResultSet)-1)+'] records')
            resultSet = ResultSet(recordSet=rawResultSet)
            if returnRaw:
                return rawResultSet
            else:
                return resultSet
        except cx_Oracle.DatabaseError as e:
            self.logger.debug('Hit cx_oracle DatabaseError: '+str(e))
            raise DatabaseQueryException(e)

    def execute(self, statement, bindValues=[], namedBindValues={}):
        """
        This will execute any sql statement against the database under the current database session.
        The statement should make use of bind variables. The bind variables can be passed in via one of two
        methods.  1) Positional via a list object and 2) Named via a dictionary object.  These two parameters
        are mutually exclusive.

        `statement:` The sql to be executed against the database.

        `bindValues:` This is the positional list of bind values (if any) to use when parsing the statement.

        `namedBindValues:` Dictionary object holding bind variable names,values to be used in the statement
        """
        try:
            bindInput = bindValues
            if len(namedBindValues) > 0:
                bindInput = namedBindValues
            cursor = self.Connection.cursor()
            cursor.execute(statement, bindInput)
        except cx_Oracle.DatabaseError as e:
            self.logger.debug('Hit cx_oracle DatabaseError: '+str(e))
            raise DatabaseDMLException(e)

    def execProc(self, procedureName, parameters=[], namedParameters={}, outParam=None):
        """
        This will execute a plsql stored procedure.  The procedure can either be a standalone procedure
        or inside a package. You can pass parameters as either positional (via the parameters argument) or
        as named parameters (via the namedParameters argument). These two arguments are mutually exclusive.

        If you simply want to run an anonymous plsql code block, you can use the `pylegos.database.oracle.Database.execute`
        method.

        `functionName:` The name of the procedure

        `parameters:` This is a python list object that contains the values of the positional parameters to pass to the procedure.

        `namedParameters:` Dictionary object that contains the named parameters and their corresponding values to pass to
                           the procedure

        `Returns:` None

        """
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
        """
        This will execute a plsql stored function.  The function can either be a standalone function
        or inside a package. You can pass parameters as either positional (via the parameters argument) or
        as named parameters (via the namedParameters argument). These two arguments are mutually exclusive.

        If you simply want to run an anonymous plsql code block, you can use the `pylegos.database.oracle.Database.execute`
        method.

        `functionName:` The name of the function

        `oracleReturnType:` Use the `pylegos.database.oracle.DataType` class for the value of this parameter.  Function
                            must return one of these defined types. Otherwise it is not supported.

        `parameters:` This is a python list object that contains the values of the positional parameters to pass to the function.

        `namedParameters:` Dictionary object that contains the named parameters and their corresponding values to pass to
                           the function

        `Returns:` Result as passed in type

        """
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
        """
        Will commit the current transaction

        Returns: None

        """
        try:
            self.Connection.commit();
        except cx_Oracle.DatabaseError as e:
            self.logger.debug('Hit cx_oracle DatabaseError: '+str(e))
            raise DatabaseDMLException(e)

    def rollback(self):
        """Will rollback the current transaction"""
        self.Connection.rollback();

    def getDefaultTablespace(self, contentType='Permanent'):
        """
        This will return the default tablespace for the database, based on content type.


        `contentType` This is the type of contents that the tablespace holds. It is best to pass
        the value using the `pylegos.database.oracle.TablespaceContentType` class.

        Returns: String

        `Example Usage:`

            ...
            db = Database()
            tbsName = db.getDefaultTablespace(contentType=TablespaceContentType.Permanent)
            ...

        """
        if contentType.upper() is 'PERMANENT':
            query = ("select property_value "
                     "from database_properties "
                     "where property_name = 'DEFAULT_PERMANENT_TABLESPACE'")
        elif contentType.upper() is 'TEMPORARY':
            query = ("select property_value "
                     "from database_properties "
                     "where property_name = 'DEFAULT_TEMP_TABLESPACE'")
        else:
            '''
            todo: raise exception/error
            '''
            return None

        tbsName = self.getValue(query=query, columnName='PROPERTY_VALUE')
        return tbsName

    def getProperty(self, propertyName=DatabaseProperty.NAME):
        """ A convenience function for getting values from v$database view.  Each field in the view is
        a class variable of the `pylegos.database.oracle.DatabaseProperty` class.  The value of any field can
        be easily retrieved via this method call.

        `propertyName`  This is the name of the property (field of v$database) that you want to get the value. It
        is best to use the `pylegos.database.oracle.DatabaseProperty` class to pass the value.

        `Returns` String

        `Example Usage:`

            ...
            db = Database()
            db.connect(....)
            dbName = db.getProperty(propertyName=DatabaseProperty.NAME)
            ...
        """
        query = "select " + propertyName + " from v$database"
        res = self.getValue(query=query)
        return res

    def getContainerType(self):
        pass

    # DEPRECATED METHODS
    def getQueryResult(self, query, bindValues=[], secureLog=False):
        """
        `DEPRECATED`

        Please use the `pylegos.database.oracle.Database.getResultSet` method instead
        """
        DeprecationUtil().deprecate(className='Database', methodName='getQueryResult', newMethodName='getResultSet')
        return self.getResultSet(query, bindValues, secureLog, returnRaw=True)

    def queryForSingleValueDep(self, query, columnName, bindValues=[], secureLog=False):
        """
        `DEPRECATED`

        Please use the `pylegos.database.oracle.Database.getValue` method instead
        """
        DeprecationUtil().deprecate(className='Database', methodName='queryForSingleValue', newMethodName='getValue')
        return self.getValue(query, columnName, bindValues, secureLog)

    def getColumnMungedResultset(self, query, bindValues=[], colDelimiter='|::|', secureLog=False):
        """
        `DEPRECATED`

        Please use the `pylegos.database.oracle.Database.getResultSet` method instead
        """
        DeprecationUtil().deprecate(className='Database', methodName='getColumnMungedResultset', newMethodName='getResultSet')
        return self.getResultSet(query, bindValues, mungeColumns=True, fieldDelimiter=colDelimiter,
                                 secureLog=secureLog, returnRaw=True)

    def getColumnDelimitedResultset(self, query, bindValues=[], fieldDelimiter=',', secureLog=False):
        """
        `DEPRECATED`

        Please use the `pylegos.database.oracle.Database.getResultSet` method instead
        """
        DeprecationUtil().deprecate(className='Database', methodName='getColumnDelimitedResultset', newMethodName='getResultSet')
        return self.getResultSet(query, bindValues, mungeColumns=True, fieldDelimiter=fieldDelimiter, secureLog=secureLog)

    def execDML(self, dml, bindValues=[]):
        """
        `DEPRECATED`

        Please use the `pylegos.database.oracle.Database.execute` method instead
        """
        DeprecationUtil().deprecate(className='Database', methodName='execDML', newMethodName='execute')
        self.execute(dml, bindValues)


class ResultSet(object):
    """
    This object is used to hold the result set from a call to `pylegos.database.oracle.Database.getResultSet`.  It has
    several methods that can be used for consumption of the data.
    """

    def __init__(self, recordSet):
        """
        Initialize a new instance of the ResultSet object

        `recordSet: `The records that are returned from the call to `pylegos.database.oracle.Database.getResultSet`

        """
        self.ResultSet = recordSet

    @staticmethod
    def __getPrintDatatype(oracleType, scale=0):
        if (str(oracleType)) == cx_Oracle.NUMBER:
            if scale > 0:
                return 'f'
            else:
                return 'd'
        elif str(oracleType) == cx_Oracle.DATETIME:
            return 't'
        else:
            return 's'

    @staticmethod
    def __printRecDel(metaData, padding):
        maxLineWidth = 0
        fieldCount = 0

        for header in metaData:
            maxLineWidth += metaData[header]['MaxSize'] + (padding*2)
            fieldCount += 1

        sys.stdout.write("{v:{w}s}".format(v='-' * (maxLineWidth + fieldCount + 1), w=maxLineWidth)+'\n')

    def printResultSet(self, showRecordCount=True, padding=1):
        """
        This method will print the result set to the screen in a ascii table format.  The width of each column is
        set to the size of the widest field in the result set automatically. This can be very useful in console
        applications.

        `showRecordCount: ` A boolean indicator as to whether a total record count should be shown at the bottom of
        the table.

        `padding: ` The padding amount that should surround each value with respect to the field delimiter "|" character

        Returns:` None.  Prints results to the screen.

        """
        metadataRow = self.ResultSet[0]
        fd = "|"
        '''
        PRINT  HEADER ROW
        '''
        self.__printRecDel(metaData=metadataRow, padding=padding)
        sys.stdout.write(fd)
        for header in metadataRow:
            fieldWidth = metadataRow[header]['MaxSize']+(padding*2)
            sys.stdout.write("{v:{w}s}|".format(v=' '*padding+header, w=fieldWidth, d=fd))

        sys.stdout.write("\n")
        self.__printRecDel(metaData=metadataRow, padding=padding)

        del self.ResultSet[0]

        for row in self.ResultSet:
            sys.stdout.write(fd)
            for header in metadataRow:
                fieldWidth = metadataRow[header]['MaxSize']+(padding*2)
                fieldType = str(metadataRow[header]['DataType'])
                scaleValue = metadataRow[header]['Scale']
                fieldValue = self.ResultSet[row][header]

                if fieldValue is None:
                    fieldValue = ""
                    fieldType = cx_Oracle.STRING

                if fieldType == Database.CxOracleType.NUMBER and scaleValue > 0:
                    sys.stdout.write("{v:{w}.{s}{t}}|".format(v=' '*padding+fieldValue, w=fieldWidth, t='f', s=scaleValue))
                elif fieldType == Database.CxOracleType.NUMBER:
                    sys.stdout.write("{v:{w}{t}}|".format(v=' '*padding+str(fieldValue), w=fieldWidth, t='d', s=scaleValue))
                elif fieldType == Database.CxOracleType.DATETIME:
                    printValue = fieldValue.strftime("%m.%d.%Y %H:%M:%S")
                    sys.stdout.write("{v:{w}{t}}|".format(v=' '*padding+printValue, w=fieldWidth, t='s'))
                elif fieldType == Database.CxOracleType.TIMESTAMP:
                    printValue = fieldValue.strftime("%m.%d.%Y %H:%M:%S:%f")
                    sys.stdout.write("{v:{w}{t}}|".format(v=' '*padding+printValue, w=fieldWidth, t='s'))
                elif fieldType == Database.CxOracleType.CLOB:
                    sys.stdout.write("{v:{w}{t}}|".format(v=' '*padding+str(fieldValue)[:100], w=fieldWidth, t='s'))
                else:
                    sys.stdout.write("{v:{w}{t}}|".format(v=' '*padding+fieldValue, w=fieldWidth, t='s'))

            sys.stdout.write('\n')
            sys.stdout.flush()

        self.__printRecDel(metaData=metadataRow, padding=padding)
        if showRecordCount:
            sys.stdout.write('Records: '+str(len(self.ResultSet))+'\n')

    def getJson(self, includeMeta=False):
        """
        Returns the records of the result set as json

        `includeMeta: `Indicator as to whether or not the metadata record should also be returned. Usually not needed.

        `Returns:` String, formatted as json

        """

        if not includeMeta:
            return json.dumps(self.ResultSet)

    def getRows(self, includeMeta=False):
        """
        Will return just the plain records that were returned from the query.  The records are in a Dictionary
        object of the format.

        `includeMeta: ` Indicates if metadata record should be included

        `Returns:` List [Dictionary]

        `Example Usage:`

            ...
            db = Database()
            db.connect(...)
            query = 'select object_name, object_type from dba_objects'
            resultSet = db.getResultSet(...)
            rows = resultSet.getRows()
            for row in rows:
                objectName = rows[row]['OBJECT_NAME']
                objectType = rows[row]['OBJECT_TYPE']

            ...

        """

        if not includeMeta:
            del self.ResultSet[0]
            return self.ResultSet
        else:
            return self.ResultSet


class Admin(object):
    """
    Class that contains common DBA routines
    """

    def __init__(self, database):
        """
        Will create a new instance of the class.

        `database` This is an instance of `pylegos.database.oracle.Database`
        """
        self.database = database

    def createUser(self, username, password, defaultTablespace=None, defaultTempTablespace=None, profile='DEFAULT'):
        """
        This will create a new user with the parameters specified

        `username:` The username to create

        `password:` The string value of the password to assign to the new user

        `defaultTablespace:` The name of the tablespace that will be the default for the user.  If this is left
                             off, then it will be assigned the database default permanent tablespace.

        `defaultTempTablespace:` the name of the tablespace for temporary objecdts.  If this is left as None, then
                               the value will be populated with the default for the database.

        `profile:` The name of the databae profile to assign.

        `Returns:` None

        """
        userPermTBS = defaultTablespace
        userTempTBS = defaultTempTablespace

        if defaultTablespace is None:
            userPermTBS = self.database.getDefaultTablespace(contentType='Permanent')

        if defaultTempTablespace is None:
            userTempTBS = self.database.getDefaultTablespace(contentType='Temporary')

        ddl = ("create user " + username + " identified by " + password + " "
               "default tablespace " + userPermTBS + " "
               "temporary tablespace " + userTempTBS + " "
               "profile " + profile + " "
               "account unlock")

        self.database.execute(ddl);

    def createRole(self, roleName):
        """
        Creates a role in the database

        `roleName:` The name of the role to create

        `Returns:` None

        """
        dcl = 'create role '+roleName
        self.database.execute(dcl)

    def grantRole(self, grantee, role):
        """
        Will grant the role to the specified grantee

        `grantee:` The username to grant the role to

        `role: ` The name of the role. It must exists

        `Returns:` None

        """
        dcl = "grant role "+role+" to "+grantee
        self.database.execute(dcl)

    def createTablespace(self, tablespaceName, datafileSize='100M'):
        """
        Creates a new tablespace inside the database

        `tablespaceName:` The name of the tablespace

        `datafileSize:` The size specification for the initial size of the tablespace

        `Returns:` None

        """
        ddl = "create tablespace "+tablespaceName+"datafile size "+datafileSize
        self.database.execute(ddl)

    def addDatafile(self, tablespaceName, datafileSize='32767M'):
        """
        Will add a datafile to an existing tablespace

        `tablespaceName: `The name of the tablespace for the datafile

        `datafileSize: ` The size spec for the datafile

        `Returns:` None

        """
        ddl = "alter tablespace "+tablespaceName+" add datafile datafile size "+datafileSize
        self.database.execute(ddl)


class DatabaseConnectionException(Exception):
    """
    This exeception will be thrown if there is an issue connecting to the database. The
    exception will have the following attributes that can be used
    """

    def __init__(self, cxExceptionObj=None, message=None):
        if message is not None:
            self.message = message
        else:
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


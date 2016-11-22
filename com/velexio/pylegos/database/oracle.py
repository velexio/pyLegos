'''
Created on Sep 19, 2016

@author: a597485
'''
import cx_Oracle
import enum
from collections import OrderedDict

'''
-----------------------
ENUMS
-----------------------
'''


class DatabaseProperty(enum.Enum):
    NAME = 'name'
    DBID = 'dbid'


class TablespaceContentType(enum.Enum):
    Permanent = 1
    Temporary = 2


class CxOracleType(enum.Enum):
    Varchar2 = "<class 'cx_Oracle.STRING'>"
    Number = "<class 'cx_Oracle.NUMBER'>"
    Date = "<class 'cx_Oracle.DATETIME'>"
    Timestamp = "<class 'cx_Oracle.TIMESTAMP'>"

    def __str__(self):
        return "{0}".format(self.value)


class Database(object):
    '''
    classdocs
    '''
    connection = None

    def __init__(self):
        '''
        Constructor
        '''
        self.connection = None

    def connect(self, username, password, connectString, asSysdba=False):
        if asSysdba:
            self.connection = cx_Oracle.connect(user=username, password=password, dsn=connectString,
                                                mode=cx_Oracle.SYSDBA)
        else:
            self.connection = cx_Oracle.connect(username, password, connectString)

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
        resultSetObj = ResultSetObject(formatedResults)
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
        cursor = self.connection.cursor()
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

    """
    This function is to be used to call any dml operation (insert,update,delete). It can also
    be used to run an anonymous pl/sql block.  If you want to execute a stored pl/sql procedure
    or function, use the executePL subtroutine
    """
    def execute(self, dml, bindValues=[]):
        cursor = self.connection.cursor()
        cursor.execute(dml, bindValues)

    def commit(self):
        self.connection.commit();

    def rollback(self):
        self.connection.rollback();

    def getById(self, id):
        return self.formattedResultSet

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


class ResultSetObject(object):
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

        print ("{v:{w}s}".format(v='-' * (maxLineWidth + 1), w=maxLineWidth))

    def printResultSet(self):
        metadataRow = self.formattedResultSet[0]
        fd = "|"
        '''
        PRINT  HEADER ROW
        '''
        self.printRecordDelimeter(metaData=metadataRow)
        print(fd, end="")
        for header in metadataRow:
            fieldWidth = metadataRow[header]['MaxSize']
            print ("{v:{w}s}|".format(v=header, w=fieldWidth, d=fd), end="", flush = True)

            print("\n", end="")
            self.printRecordDelimeter(metaData=metadataRow)
            del self.formattedResultSet[0]

            for row in self.formattedResultSet:
                print(fd, end="")
                for header in metadataRow:
                    fieldWidth = metadataRow[header]['MaxSize']
                    fieldType = str(metadataRow[header]['DataType'])
                    scaleValue = metadataRow[header]['Scale']
                    fieldValue = self.formattedResultSet[row][header]

                    if fieldValue is None:
                        fieldValue = ""
                        fieldType = str(CxOracleType.Varchar2)

                    if fieldType == str(CxOracleType.Number) and scaleValue > 0:
                        print(
                        "{v:{w}.{s}{t}}|".format(v=fieldValue, w=fieldWidth, t='f', s=scaleValue), end="", flush = True)
                    elif fieldType == str(CxOracleType.Number):
                        print(
                        "{v:{w}{t}}|".format(v=fieldValue, w=fieldWidth, t='d', s=scaleValue), end="", flush = True)
                    elif fieldType == str(CxOracleType.Date):
                        printValue = fieldValue.strftime("%m.%d.%Y %H:%M:%S")
                        print("{v:{w}{t}}|".format(v=printValue, w=fieldWidth, t='s'), end="", flush = True)
                    elif fieldType == str(CxOracleType.Timestamp):
                        printValue = fieldValue.strftime("%m.%d.%Y %H:%M:%S:%f")
                        print("{v:{w}{t}}|".format(v=printValue, w=fieldWidth, t='s'), end="", flush = True)
                    else:
                        print("{v:{w}{t}}|".format(v=fieldValue, w=fieldWidth, t='s'), end="", flush = True)
                        print("\n", end="")


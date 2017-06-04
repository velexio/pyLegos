from pylegos.core import FileUtils
from pylegos.core import PlatformProperty
from pylegos.core import ConfigManager
from pylegos.utils import NameConverter


class ProjectService:

    def __init__(self, name):
        self.ProjectName = name
        self.AppName = name.lower()
        self.ProjectBaseDir = self.ProjectName+PlatformProperty.FileSep
        self.TemplateDir = FileUtils.getParentDir(__file__)+PlatformProperty.FileSep+'templates'+PlatformProperty.FileSep

    def __validate(self):
        if FileUtils.dirExists(self.ProjectName):
            raise RuntimeError('A project by that name already exists')

    def __buildDirTree(self, isSimple):
        s = PlatformProperty.FileSep
        databaseDirs = ['database'+s+'ddl'+s+'objects',
                        'database'+s+'ddl'+s+'packages',
                        'database'+s+'data',
                        'database'+s+'user']
        containerDirs = ['build', 'test', 'app', 'dist']
        testDir = self.ProjectBaseDir+'test'+s
        appDirs = ['lib',
                   'conf',
                   'modules']
        FileUtils.createDir(self.ProjectName)
        for cDir in containerDirs:
            FileUtils.createDir(self.ProjectBaseDir+cDir)

        FileUtils.createDir(testDir+'app'+s+'lib')
        FileUtils.createDir(self.ProjectBaseDir+'build'+s+'def-files')

        for dDir in databaseDirs:
            FileUtils.createDir(self.ProjectBaseDir+'dist'+s+dDir)
            FileUtils.createDir(self.ProjectBaseDir+'app'+s+dDir)

        for appDir in appDirs:
            if appDir.endswith('modules'):
                if not isSimple:
                    FileUtils.createDir(self.ProjectBaseDir+'app'+s+appDir)
                    FileUtils.createDir(testDir+'app'+s+'modules')
            else:
                FileUtils.createDir(self.ProjectBaseDir+'app'+s+appDir)

    def __buildManifest(self):
        sep = PlatformProperty.FileSep
        sourceFile = self.TemplateDir+'config'+sep+'project_base_manifest.tpl'
        targetFile = self.ProjectBaseDir+'app'+sep+'conf'+sep+self.ProjectName.lower()+'_manifest.ini'
        FileUtils.copyFile(sourceFile, targetFile)
        configManager = ConfigManager(targetFile)
        configManager.setValue('APP', 'AppName', self.ProjectName)
        configManager.setValue('APP', 'Version', {'MAJOR': '0.1', 'MINOR': '.0'})
        configManager.setValue('PYTHON', 'RuntimeVersions', '['+PlatformProperty.getPythonVersion()+']')
        configManager.save()

    def __buildConfFile(self):
        sep = PlatformProperty.FileSep
        appDir = self.ProjectBaseDir+'app'+sep
        FileUtils.copyFile(self.TemplateDir+'config'+sep+'app.ini', appDir+'conf'+sep+self.AppName+'.ini')

    def __buildCodeFiles(self):
        sep = PlatformProperty.FileSep
        appDir = self.ProjectBaseDir+sep+'app'+sep
        appName = self.ProjectName.lower()
        templateFiles = FileUtils().getFileMatches(self.TemplateDir+'code'+sep, 'app*.tpl')
        for tf in templateFiles:
            file = open(self.TemplateDir+'code'+sep+tf, 'r')
            fileContent = file.read()
            file.close()
            fileContent = fileContent.replace('{{APPNAME_OBJECT}}', NameConverter.getObjectName(self.AppName))
            codeFile = open(appDir+tf.replace('app', self.AppName).replace('.tpl', '.py'), 'w')
            codeFile.write(fileContent)
            codeFile.close()

    def __buildAppBinFile(self):
        sep = PlatformProperty.FileSep
        appName = self.ProjectName.lower()
        tplFile = 'app.sh'
        FileUtils.copyFile(self.TemplateDir+'launchers'+sep+tplFile, self.ProjectBaseDir+'bin'+sep+appName)

    def __buildTestFiles(self):
        sep = PlatformProperty.FileSep
        appDir = self.ProjectBaseDir+'test'+sep+'app'+sep
        testFiles = ['test_'+self.AppName+'.py', 'test_'+self.AppName+'_controllers.py', 'test_'+self.AppName+'_services.py']
        for tf in testFiles:
            testFile = open(appDir+tf, 'w')
            testFile.write('from unittest import TestCase\n\n')
            testFile.close()

    def __copyModDefTemplate(self):
        s = PlatformProperty.FileSep
        FileUtils.copyFile(self.TemplateDir+'config'+s+'modelDef.tpl', self.ProjectBaseDir+'build'+s+'def-files'+s+'model.def')
        FileUtils.copyFile(self.TemplateDir+'config'+s+'model-def.README', self.ProjectBaseDir+'build'+s+'def-files'+s+'model-def.README')

    def __createDatabaseScripts(self):
        s = PlatformProperty.FileSep

        objectScripts = ['dblinks.sql',
                         'synonyms.sql',
                         'sequences.sql',
                         'types.sql',
                         'queues.sql',
                         'tables.sql',
                         'triggers.sql',
                         'views.sql',
                         'indexes.sql',
                         'constraints_ck.sql',
                         'constraints_pk.sql',
                         'constraints_uk.sql',
                         'constraints_fk.sql']
        dataScripts = ['seed.sql']

        for obj in objectScripts:
            FileUtils.touchFile(self.ProjectBaseDir+'app'+s+'database'+s+'ddl'+s+'objects'+s+obj)

        for data in dataScripts:
            FileUtils.touchFile(self.ProjectBaseDir+'app'+s+'database'+s+'data'+s+data)

        FileUtils.copyFile(self.TemplateDir+'config'+s+'database-userInfo.tpl', self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_info.ini')
        FileUtils.copyFile(self.TemplateDir+'config'+s+'database-userPrivs.tpl', self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_privs.ini')
        # REPLACE TOKENS IN INFO FILE
        iniFile = open(self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_info.ini', 'r')
        fileContents = iniFile.read()
        iniFile.close()
        fileContents = fileContents.replace('{{APPNAME}}', self.AppName.upper())
        iniFile = open(self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_info.ini', 'w')
        iniFile.write(fileContents)
        iniFile.close()
        # REPLACE TOKENS IN PRIV FILE
        iniFile = open(self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_privs.ini', 'r')
        fileContents = iniFile.read()
        iniFile.close()
        fileContents = fileContents.replace('{{APPNAME}}', self.AppName.upper())
        iniFile = open(self.ProjectBaseDir+'app'+s+'database'+s+'user'+s+'user_privs.ini', 'w')
        iniFile.write(fileContents)
        iniFile.close()

    def __createBuildFiles(self):
        s = PlatformProperty.FileSep
        FileUtils.copyFile(self.TemplateDir+'code'+s+'build.py', self.ProjectBaseDir+'build'+s+'build.py')

    def initProject(self, simpleProject):
        self.__validate()
        self.__buildDirTree(simpleProject)
        self.__buildManifest()
        self.__buildCodeFiles()
        self.__buildConfFile()
        #self.__buildAppBinFile()
        self.__buildTestFiles()
        self.__copyModDefTemplate()
        self.__createDatabaseScripts()
        self.__createBuildFiles()

    def modularize(self):
        sep = PlatformProperty.FileSep
        modDir = self.ProjectBaseDir+'app'+sep+'modules'
        modTestDir = self.ProjectBaseDir+'test'+sep+'app'+sep+'modules'
        if not FileUtils.dirExists(modDir):
            FileUtils.createDir(modDir)
        if not FileUtils.dirExists(modTestDir):
            FileUtils.createDir(modTestDir)


class ModuleService:

    def __init__(self, moduleName):
        fsep = PlatformProperty.FileSep
        self.ModuleName = moduleName.lower()
        self.ProjectBaseDir = FileUtils.getWorkingDir()+fsep
        projectDirArray = self.ProjectBaseDir.strip(fsep).split(fsep)
        self.ProjectName = projectDirArray[len(projectDirArray)-1].lower()
        self.ModuleBaseDir = 'app'+fsep+'modules'+fsep
        self.ModuleDir = self.ModuleBaseDir+self.ModuleName+fsep
        self.ConfDir = 'app'+fsep+'conf'+fsep
        self.TemplateDir = FileUtils.getParentDir(__file__)+fsep+'templates'+fsep

    def __validate(self):
        if not FileUtils.dirExists(self.ModuleBaseDir):
            message = """ It does not appear you are in your project directory.  This command must be run from within your project directory.
            If you are inside your project directory, then you are getting this error because your project was not initialized as modular. To
            make it modular.  Navigate to your project base directory and run the following:
            
            pylegos project modularize --name <project name>
            
            """
            raise RuntimeError(message)

    def __buildModDir(self):
        FileUtils.createDir(self.ModuleBaseDir+self.ModuleName)

    def __buildManifest(self):
        fsep = PlatformProperty.FileSep
        manifestFilename = self.ProjectBaseDir+'app'+fsep+'conf'+fsep+self.ModuleName.lower()+'_manifest.ini'
        FileUtils.copyFile(self.TemplateDir+'modBaseManifest.tpl', manifestFilename)
        manFile = open(manifestFilename, 'r')
        fileContents = manFile.read()
        manFile.close()
        fileContents = fileContents.replace('{{MODNAME}}', self.ModuleName.lower())
        manFile = open(manifestFilename, 'w')
        manFile.write(fileContents)
        manFile.close()

    def __buildConfFile(self):
        FileUtils.copyFile(self.TemplateDir+'module.ini', self.ConfDir+self.ModuleName+'.ini')

    def __buildCodeFiles(self):
        templateFiles = FileUtils().getFileMatches(self.TemplateDir, 'module_*.tpl')
        for tpl in templateFiles:
            codeFilename = self.ModuleDir+tpl.replace('module', self.ModuleName).replace('.tpl', '.py')
            FileUtils.copyFile(self.TemplateDir+tpl, codeFilename)
            codeFile = open(codeFilename, 'r')
            fileContents = codeFile.read()
            codeFile.close()
            fileContents = fileContents.replace('{{MODNAME_OBJECT}}', NameConverter.getObjectName(self.ModuleName))
            fileContents = fileContents.replace('{{MODNAME}}', NameConverter.getObjectName(self.ModuleName))
            codeFile = open(codeFilename, 'w')
            codeFile.write(fileContents)
            codeFile.close()

    def __buildTestFiles(self):
        fsep = PlatformProperty.FileSep
        modTestDir = self.ProjectBaseDir+'test'+fsep+'app'+fsep+'modules'+fsep+self.ModuleName+fsep
        FileUtils.createDir(modTestDir)
        FileUtils.touchFile(modTestDir+'test_'+self.ModuleName+'.py')
        FileUtils.touchFile(modTestDir+'test_'+self.ModuleName+'_controllers.py')
        FileUtils.touchFile(modTestDir+'test_'+self.ModuleName+'_services.py')

    def __registerToManifest(self):
        fsep = PlatformProperty.FileSep
        manFilename = self.ProjectBaseDir+'conf'+fsep+self.ProjectName+'_manifest.ini'
        confManager = ConfigManager(configFile=manFilename)
        modArray = confManager.getValue('MODULES', 'ModuleList')
        modArray.append(self.ModuleName)
        confManager.setValue('MODULES', 'ModuleList', modArray)
        confManager.save()


    def initModule(self):
        self.__validate()
        self.__buildModDir()
        self.__buildManifest()
        self.__buildCodeFiles()
        self.__buildTestFiles()


class ModelService:

    def __init__(self, modelName):
        self.ModelName = modelName


class GitService:

    def getTagCommit(self, tagName):
        # git show-ref -s <tag name>
        pass

    def __genDiff(self):
        pass

    def buildDeployScript(self):
        runStatements = []
        diffFile = open('/tmp/table.diff')
        endStatement = False
        statement = None
        statementKeyMap = None
        for l in diffFile.readlines():
            line = l.lower().strip()
            if line.startswith('+++'):
                continue
            if line.startswith('+') and len(line) > 2:
                line = line.strip('+')
                lineArray = line.split()
                if lineArray[0].upper() in DDLMetadata.StatementKeys:
                    endStatement = False
                    statement = ''
                    statementKeyMap = DDLMetadata.StatementKeys[lineArray[0].upper()]

                for terminator in statementKeyMap['TERMINATORS']:
                    if line.endswith(terminator):
                        endStatement = True

                statement += line+'\n'

                if endStatement:
                    runStatements.append(statement)

        for s in runStatements:
            print('Run: '+s)

class DatabaseMeta(object):

    def __init__(self, db_user, db_pass, db_connect_string, db_working_schema, table_name):
        self.db = cx_Oracle.connect(db_user, db_pass, db_connect_string)
        self.db.current_schema = db_working_schema
        self.SchemaName = db_working_schema
        self.TableName = table_name

    def get_columns(self):
        sql = """
              select column_name
              from dba_tab_columns
              where owner = upper(:b1)
              and table_name = upper(:b2)
              and column_name not in ('ID','CREATED','MODIFIED')
              order by column_id
              """
        cursor = self.db.cursor()
        cursor.execute(sql, [self.SchemaName, self.TableName])
        rs = cursor.fetchall()
        columnData = []
        for row in rs:
            columnData.append(row[0])
        return columnData


class DataType:
    ValidTypes = ['BOOLEAN', 'STRING', 'INTEGER', 'FLOAT', 'LARGE_STRING', 'DATE', 'TIMESTAMP', 'LARGE_BINARY']
    Type = {'BOOLEAN': {'RDB': {'ORACLE': {'DATATYPE': 'varchar2',
                                           'DEFAULT': "'N'",
                                           'DEFAULT_LEN': '1',
                                           'CONVERT_FUNCTION': 'UPPER',
                                           'VALID_VALUES': "'Y','N'"}
                                }
                        },
            'INTEGER': {'RDB': {'ORACLE': {'DATATYPE': 'number',
                                           'DEFAULT': None,
                                           'DEFAULT_LEN': None,
                                           'CONVERT_FUNCTION': None,
                                           'VALID_VALUES': None}
                                }
                        },
            'FLOAT': {'RDB': {'ORACLE': {'DATATYPE': 'number',
                                         'DEFAULT': None,
                                         'DEFAULT_LEN': '*,2',
                                         'CONVERT_FUNCTION': None,
                                         'VALID_VALUES': None}
                              }
                      },
            'STRING': {'RDB': {'ORACLE': {'DATATYPE': 'varchar2',
                                          'DEFAULT': None,
                                          'DEFAULT_LEN': '255',
                                          'CONVERT_FUNCTION': None,
                                          'VALID_VALUES': None}
                               }
                       },
            'LARGE_STRING': {'RDB': {'ORACLE': {'DATATYPE': 'clob',
                                                'DEFAULT': None,
                                                'DEFAULT_LEN': None,
                                                'CONVERT_FUNCTION': None,
                                                'VALID_VALUES': None}
                                     }
                             },
            'LARGE_BINARY': {'RDB': {'ORACLE': {'DATATYPE': 'blob',
                                                'DEFAULT': None,
                                                'DEFAULT_LEN': None,
                                                'CONVERT_FUNCTION': None,
                                                'VALID_VALUES': None}
                                     }
                             },
            'DATE': {'RDB': {'ORACLE': {'DATATYPE': 'date',
                                        'DEFAULT': None,
                                        'DEFAULT_LEN': None,
                                        'CONVERT_FUNCTION': None,
                                        'VALID_VALUES': None}
                             }
                     },
            'TIMESTAMP': {'RDB': {'ORACLE': {'DATATYPE': 'timestamp',
                                             'DEFAULT': None,
                                             'DEFAULT_LEN': '6',
                                             'CONVERT_FUNCTION': None,
                                             'VALID_VALUES': None}
                                  }
                          }
            }


class Util(object):

    def convertName(self, target, name, pluralizeCollections=False):

        validTargets = ['table', 'object', 'tableField', 'objectAttribute']

        if target in validTargets:

            if target.lower() == 'table' or target.lower() == 'tablefield':
                newName = name[:1].lower()
                convertPortion = name[1:]
                for c in convertPortion:
                    newChar = c
                    if c.isupper():
                        newChar = '_'+c.lower()
                    newName += newChar
                if target.lower() == 'table':
                    if pluralizeCollections:
                        newName = self.toPluralName(newName)
                    newName = newName.upper()
                return newName

            else:
                newName = name[:1].lower()
                convertPortion = name[1:].lower()
                upperNextChar = False
                for c in convertPortion:
                    if upperNextChar:
                        newChar = c.upper()
                        upperNextChar = False
                    else:
                        newChar = c
                        if c == '_':
                            newChar = ''
                            upperNextChar = True
                    newName += newChar

                newName = self.toSingularName(newName)
                if target.lower() == 'object':
                    newName = newName[:1].upper()+newName[1:]
                return newName

        else:
            raise RuntimeError('target specified ['+str(target)+'] in call to convertName is not valid.')

    @staticmethod
    def toPluralName(name):
        inflectEngine = inflect.engine()
        pluralName = inflectEngine.plural_noun(name)
        return pluralName

    @staticmethod
    def toSingularName(name):
        inflectEngine = inflect.engine()
        singularName = inflectEngine.singular_noun(name)
        return singularName

    @staticmethod
    def initCapName(objectName):
        def findUnderscores(s, c):
            return [i for i, ltr in enumerate(s) if ltr == c]
        underscorePositions = findUnderscores(objectName, '_')
        '''I am doing this because after all the _ chars are replaced, the index positions for the
           uppercase chars will have shifted down by one (shifted to the left) for all positions
           but the first position
        '''
        if len(underscorePositions) > 1:
            modPos = []
            posCntr = 0
            for p in underscorePositions:
                if posCntr == 0:
                    modPos.append(p)
                else:
                    modPos.append(p-1)
                posCntr += 1
            underscorePositions = modPos
        nameArray = list(objectName.replace('_', '').lower())
        charCount = 0
        convertedArray = []
        for c in nameArray:
            if charCount == 0 or charCount in underscorePositions:
                convertedArray.append(c.upper())
            else:
                convertedArray.append(c)
            charCount += 1
        return ''.join(convertedArray)

    def camelCaseName(self, objectName):
        initName = self.initCapName(objectName)
        initLetter = initName[:1].lower()
        baseName = initName[1:]
        return initLetter+baseName


class DaoGenerator(object):

    def __init__(self, db_user, db_pass, db_connect_string, db_working_schema, table_name):
        self.db = cx_Oracle.connect(db_user, db_pass, db_connect_string)
        self.db.current_schema = db_working_schema
        self.SchemaName = db_working_schema
        self.TableName = table_name
        self.DatabaseMeta = DatabaseMeta(db_user=db_user,
                                         db_pass=db_pass,
                                         db_connect_string=db_connect_string,
                                         db_working_schema=db_working_schema,
                                         table_name=table_name)

    def createBaseDao(self):
        className = Util().initCapName(objectName=self.TableName)
        className = className[:len(className)-1]+'Dao'
        code = 'class '+className+'\n\n'
        code += ' '*4+'def __init__(self,\n'
        columns = self.DatabaseMeta.get_columns()
        daoAttribs = ''
        for c in columns:
            ccn = Util().camelCaseName(c)
            attribLine = ' '*17+ccn+',\n'
            daoAttribs += attribLine
        initLine = daoAttribs[:len(daoAttribs)-2]+'):\n'
        code += initLine
        for cn in columns:
            attribName = Util().initCapName(objectName=cn)
            valueName = Util().camelCaseName(objectName=cn)
            attribLine = ' '*8+'self.'+attribName+' = '+valueName+'\n'
            code += attribLine
        print(code)


class TapiGenerator(object):

    def __init__(self, db_user, db_pass, db_connect_string, db_working_schema, table_name):
        self.db = cx_Oracle.connect(db_user, db_pass, db_connect_string)
        self.db.current_schema = db_working_schema
        self.SchemaName = db_working_schema
        self.TableName = table_name
        self.DatabaseMeta = DatabaseMeta(db_user=db_user,
                                         db_pass=db_pass,
                                         db_connect_string=db_connect_string,
                                         db_working_schema=db_working_schema,
                                         table_name=table_name)

    def createSpec(self):
        columns = self.DatabaseMeta.get_columns()
        specDDL = """
        CREATE OR REPLACE PACKAGE tapi_"""+self.TableName+"""
        IS
        /**
         RECORD TYPE FOR TABLE
        */
        TYPE """+self.TableName+"""_rec IS RECORD
          ("""
        typeColumns = ''
        cntr = 0
        for cn in columns:
            attribLine = ''
            if cntr < 1:
                attribLine = cn+' '+self.TableName+'.'+cn+'%TYPE,\n '
            else:
                attribLine = ' '*10+cn+' '+self.TableName+'.'+cn+'%TYPE,\n'
            cntr += 1
            typeColumns += attribLine
        typeAttribs = typeColumns[:len(typeColumns)-2]+');'
        specDDL += typeAttribs+"""

        TYPE """+self.TableName+"""_tab IS TABLE OF """+self.TableName+"""_rec INDEX BY PLS_INTEGER;

        /**
         CRUD PROCEDURES
        */

        PROCEDURE add("""
        procColumns = ''
        addDDL = ''
        cntr = 0
        for cn in columns:
            if cntr < 1:
                attribLine = 'i_'+cn.lower()+' IN '+self.TableName.upper()+'.'+cn+'%TYPE, \n'
            else:
                attribLine = ' '*22+'i_'+cn.lower()+' IN '+self.TableName.upper()+'.'+cn+'%TYPE, \n'
            cntr += 1
            procColumns += attribLine
        addDDL = procColumns[:len(procColumns)-3]+');'
        specDDL += addDDL+"""

        PROCEDURE add("""
        procColumns = ''
        cntr = 0
        for cn in columns:
            attribLine = ''
            if cntr < 1:
                attribLine = 'i_'+cn.lower()+' IN '+self.TableName.upper()+'.'+cn+'%TYPE, \n'
            else:
                attribLine = ' '*22+'i_'+cn.lower()+' IN '+self.TableName.upper()+'.'+cn+'%TYPE, \n'
            cntr += 1
            procColumns += attribLine
        procColumns += ' '*23+'i_suppress_dup IN BOOLEAN DEFAULT TRUE,\n'
        specDDL += procColumns+' '*22+"""o_id  OUT """+self.TableName+""".ID%TYPE);

        PROCEDURE add(i_"""+self.TableName+""" IN """+self.TableName+"""_tab);

        PROCEDURE modify(i_id IN """+self.TableName+""".ID%TYPE,\n"""
        procColumns = ''
        for cn in columns:
            procColumns += ' '*25+'i_'+cn.lower()+' IN '+self.TableName.upper()+'.'+cn+'%TYPE, \n'
        modDDL = procColumns[:len(procColumns)-3]+');'
        specDDL += modDDL+"""

        PROCEDURE remove(i_id  IN  """+self.TableName+""".ID%TYPE);

        END tapi_"""+self.TableName+""";
        /
        """
        print(specDDL)

    def createBody(self):
        columns = self.DatabaseMeta.get_columns()
        ddl = """
        CREATE OR REPLACE PACKAGE BODY tapi_"""+self.TableName+"""
        IS
        /**
        CRUD PROCEDURE IMPLEMENTATIONS
        */

        PROCEDURE add("""
        procColumns = ''
        cntr=0
        for cn in columns:
            attribLine = ''
            if cntr < 1:
                attribLine = 'i_' + cn.lower() + ' IN ' + self.TableName.upper() + '.' + cn + '%TYPE, \n'
            else:
                attribLine = ' '*22+'i_' + cn.lower() + ' IN ' + self.TableName.upper() + '.' + cn + '%TYPE, \n'
            cntr += 1
            procColumns += attribLine
        addDDL = procColumns[:len(procColumns) - 3] + ')'
        ddl += addDDL + """
        IS
          l_id """+self.TableName+""".ID%TYPE;
        BEGIN
           -----
           add (o_id => l_id,
        """
        procColumns = ''
        ddlClause = ''
        cntr = 0
        for cn in columns:
            attribLine = ''
            if cntr < 1:
                attribLine = ' '*8+'i_'+cn.lower()+' => i_'+cn.lower()+', \n'
            else:
                attribLine = ' '*16+'i_'+cn.lower()+' => i_'+cn.lower()+', \n'
            cntr += 1
            procColumns += attribLine
        ddlClause = procColumns[:len(procColumns)-3]+');'
        ddl += ddlClause+"""
           -----
        END add;

        PROCEDURE add(i_"""+self.TableName+""" IN """+self.TableName+"""_tab)
        IS
          l_id """+self.TableName+""".ID%TYPE;
        BEGIN
          FOR i IN i_"""+self.TableName+""".FIRST..i_"""+self.TableName+""".LAST LOOP
             -----
             add (o_id => l_id,
        """
        procColumns = ''
        ddlClause = ''
        cntr = 0
        for cn in columns:
            attribLine = ''
            if cntr < 1:
                attribLine = ' '*10+'i_'+cn.lower()+' => i_'+self.TableName+'(i).'+cn.lower()+', \n'
            else:
                attribLine = ' '*18+'i_'+cn.lower()+' => i_'+self.TableName+'(i).'+cn.lower()+', \n'
            cntr += 1
            procColumns += attribLine
        ddlClause = procColumns[:len(procColumns)-3]+');'
        ddl += ddlClause+"""
             -----
          END LOOP;
        END add;

        PROCEDURE add ("""
        procColumns = ''
        cntr=0
        for cn in columns:
            attribLine = ''
            if cntr < 1:
                attribLine = 'i_' + cn.lower() + ' IN ' + self.TableName.upper() + '.' + cn + '%TYPE, \n'
            else:
                attribLine = ' '*23+'i_' + cn.lower() + ' IN ' + self.TableName.upper() + '.' + cn + '%TYPE, \n'
            cntr += 1
            procColumns += attribLine
        procColumns += ' '*23+'i_suppress_dup IN BOOLEAN DEFAULT TRUE,\n'
        ddl += procColumns + ' '*23 + """o_id OUT """+self.TableName+""".ID%TYPE)
        IS
        BEGIN
           -----
           INSERT INTO """+self.TableName+"""
             ("""
        tabColumns = ''
        for cn in columns:
            tabColumns += cn.lower()+','
            tabDDL = tabColumns[:len(tabColumns) - 1] + ')'
        ddl += tabDDL + """
           VALUES
             ("""
        procColumns = ''
        for cn in columns:
            procColumns += 'i_' + cn.lower() + ','
            paramDDL = procColumns[:len(procColumns) - 1] + ')'
        ddl += paramDDL + """
           RETURNING id INTO o_id;
           -----
        EXCEPTION
          WHEN dup_val_on_index THEN
            IF NOT i_suppress_dup
            THEN
              raise;
            END IF;
        END add;

        PROCEDURE modify(i_id  IN """+self.TableName+""".ID%TYPE, \n"""
        procColumns = ''
        addDDL = ''
        for cn in columns:
            procColumns += ' '*25+'i_' + cn.lower() + ' IN ' + self.TableName.upper() + '.' + cn + '%TYPE, \n'
        addDDL = procColumns[:len(procColumns) - 3] + ')'
        ddl += addDDL + """
        IS
        BEGIN
           -----
           UPDATE """+self.TableName+"""
        """
        procColumns = ''
        addDDL = ''
        cntr=0
        for cn in columns:
            attribLine = ''
            if cntr < 1:
                attribLine = '      SET ' + cn.lower() + ' = i_' + cn.lower() + ', \n'
            else:
                attribLine = ' '*18+ cn.lower() + ' = i_' + cn.lower() + ', \n'
            cntr += 1
            procColumns += attribLine
        addDDL = procColumns[:len(procColumns) - 3]
        ddl += addDDL + """
            WHERE id = i_id;
           -----
        END modify;

        PROCEDURE remove (i_id IN """+self.TableName+""".ID%TYPE)
        IS
        BEGIN
           -----
           DELETE FROM """+self.TableName+"""
           WHERE id = i_id;
           -----
        END remove;

        END tapi_"""+self.TableName+""";
        / """
        print(ddl)


class TableGenerator:

    def __init__(self):
        self.ObjectName = None
        self.ObjectCat = None
        self.TablePrefix = 'T_'

    @staticmethod
    def getCodeFromTablename(tableName, prefixLength=2, codeLength=5):
        tabCode = tableName[prefixLength:codeLength+prefixLength]
        return tabCode

    def getTableCode(self, codeLength=3):
        baseTableName = Util().convertName('table', self.ObjectName)
        tnArray = baseTableName.split('_')
        codeArray = []
        codeFinished = False
        idx = -1
        aiter = -1
        while not codeFinished:
            idx += 1
            aiter += 1
            apos = 0
            for ts in tnArray:
                iPos = apos+aiter
                codeArray.insert(iPos, ts[idx])
                if len(codeArray) == codeLength:
                    codeFinished = True
                    break
                apos += 1

        tabCode = ''
        for l in codeArray:
            tabCode += l

        return self.ObjectCat.upper()+tabCode.upper()

    def getConstraintPrefix(self):
        tabCode = self.getTableCode()
        return tabCode+'#'

    def runInteractive(self):

        objectName = input('Enter the name of the object or table name: ')

        finishedDef = False
        while not finishedDef:
            moreCols = True
            defineRI = False
            attribLine = ''
            while moreCols:
                attribName = input('Attribute Name: ')
                attribType = input('Type '+str(DataType.ValidTypes)+': ')
                attribSize = input('Max Len/Precision (leave empty for default): ')
                attribNulls = input('Allow null values (y/n) [y]: ')
                attribUnique = input('Column values UNIQUE (y/n) [n]: ')
                attribDefault = input('Default value (Empty for none): ')
                print("Enter comma delimited list of restricted values for field (Enclose strings with single quote (i.e. 'valid1','valid2') )")
                attribValidValues = input("Restricted values: ")
                print('Sometimes you may want to store values in all uppercase or lowercase, of so enter value.  If not, just hit enter')
                attribCase = input('Enter Case (upper/lower): ')


                validAnswer = False
                addMore = 'Y'
                while not validAnswer:
                    addMoreCols = input('Define another field (y/n): ')
                    addMore = str(addMoreCols).upper()
                    if addMore.upper() in ('Y', 'N'):
                        validAnswer = True
                if addMore == 'N':
                    moreCols = False

                attribLine += attribName+'='+attribType+':'+attribNulls+':'+attribSize+':'+attribUnique+':'+attribDefault+':'+attribValidValues+':'+attribCase+';'

            attribLine = attribLine[:-1]
            haveRI = 'N'
            validAnswer = False
            while not validAnswer:
                haveRI = str(input('Define RI (y/n): ')).upper()
                if haveRI in ('Y', 'N'):
                    validAnswer = True
            if haveRI == 'Y':
                defineRI = True

            while defineRI:
                localColumn = input('Enter child field name: ')
                refTable = input('Enter referencing table: ')
                refCol = input('Enter referencing field: ')

            finishedDef = True

        ddlBundle = self.processObjectDefFile(objectName=objectName,
                                              attributes=attribLine)
        return ddlBundle

    @staticmethod
    def genSequenceDDL(tableName, startValue):
        seqName = tableName+'_seq'
        startVal = '100' if startValue is None else str(startValue)
        seqDDL = 'CREATE SEQUENCE '+seqName+' START WITH '+startVal+';\n\n'
        return seqDDL

    @staticmethod
    def genTriggerDDL(tableName, caseColumns):
        seqName = tableName+'_seq'
        trigName = tableName+'_trg'
        trigDDL = "CREATE OR REPLACE TRIGGER "+trigName+"\n"
        trigDDL += "BEFORE INSERT OR UPDATE ON "+tableName+"\n"
        trigDDL += "FOR EACH ROW\n"
        trigDDL += "BEGIN\n"
        trigDDL += "  IF INSERTING THEN \n"
        trigDDL += "    :new.id := "+seqName+".nextval;\n"
        trigDDL += "    :new.created := sysdate;\n"
        trigDDL += "    :new.modified := sysdate;\n"
        trigDDL += "  END IF; \n"
        trigDDL += "  IF UPDATING THEN \n"
        trigDDL += "    :new.id := :old.id;\n"
        trigDDL += "    :new.created := :old.created;\n"
        trigDDL += "    :new.modified := sysdate;\n"
        trigDDL += "  END IF; \n\n-- DATA RULES FOR INSERT OR UPDATE\n"
        for cc in caseColumns:
            cn = cc['COLUMN_NAME']
            fx = str(cc['CASE'])
            trigDDL += '  :new.'+cn+' := '+fx.upper()+'(:new.'+cn+');\n'
        trigDDL += '\nEND '+trigName+';\n/'
        return trigDDL

    def genUKConstraints(self, tableName, uniqueColumns):
        ddlStatements = []
        prefix = self.getConstraintPrefix()

        for cn in uniqueColumns:
            ddl = 'ALTER TABLE '+tableName+' ADD CONSTRAINT '+prefix+cn[:27-(len(prefix))]+'#uk UNIQUE('+cn+');'
            ddlStatements.append(ddl)
        return ddlStatements

    def genPKConstraint(self, tableName):
        prefix = self.getConstraintPrefix()
        return 'ALTER TABLE '+tableName+' ADD CONSTRAINT '+prefix+'pk PRIMARY KEY(ID);'

    def genCKConstraints(self, tableName, checkColumns):
        prefix = self.getConstraintPrefix()
        ddlStatements = []

        for entry in checkColumns:
            cn = entry['COLUMN_NAME']
            vv = entry['VALID_VALUES']
            ddl = 'ALTER TABLE '+tableName+' ADD CONSTRAINT '+prefix+cn[:27-(len(prefix))]+'#ck\nCHECK (' + cn + ' IN ('+vv+'));\n'
            ddlStatements.append(ddl)
        return ddlStatements

    def genFKConstraints(self, tableName, refColumns):
        prefix = self.getConstraintPrefix()
        ddlStatements = []

        for entry in refColumns:
            cn = entry['COLUMN_NAME']
            refTab = entry['REF_TABLE']
            refPrefix = self.getCodeFromTablename(refTab)
            refCol = entry['REF_FIELD']
            refDelRule = entry['DELETE_RULE']
            ddl = 'ALTER TABLE '+tableName+' \nADD CONSTRAINT '+prefix+cn[:27-(len(prefix)+len(refPrefix))]+'#'+refPrefix+'#fk \nFOREIGN KEY('+cn+') \n'
            ddl +='REFERENCES '+refTab+'('+refCol+')'
            if refDelRule is not None:
                ddl += ' ON DELETE '+refDelRule+';'
            else:
                ddl +=';\n'
            ddlStatements.append(ddl)

        return ddlStatements

    def genTableDDLBundle(self, objectDef, targetContainerType='RDB', targetName='ORACLE'):
        ind = 3
        dtp = 15
        cis = 30
        targetType = targetContainerType.upper()
        targetName = targetName.upper()
        objectName = objectDef['NAME']
        seqOverride = objectDef['SEQ_OVERRIDE']
        tabCat = objectDef['CATEGORY']
        attribArray = objectDef['ATTRIBUTES']
        tableName = self.TablePrefix+self.getTableCode()+'_'+Util().convertName('table', objectName)[:22]
        constraintPrefix = self.getConstraintPrefix()
        tableDDL = 'CREATE TABLE ' + tableName + ' (\n'
        tableDDL +=' '*ind+'id'+' '*28+'NUMBER'+' '*9+'CONSTRAINT ' + constraintPrefix + 'id#nn NOT NULL,\n'
        uniqueColumns = []
        validateColumns = []
        fxColumns = []
        refColumns = []

        for attrib in attribArray:
            colName = Util().convertName('tableField', attrib.split(':')[0])
            options = attrib.split(':')[1].split(';')
            idx = [i for i, v in enumerate(options) if 't=' in v.lower()]
            dataType = 'STRING' if len(idx) < 1 else options[idx[0]].split('=')[1].upper()
            idx = [i for i, v in enumerate(options) if 'n=' in v.lower()]
            allowNull = 'Y' if len(idx) < 1 else options[idx[0]].split('=')[1].upper()
            idx = [i for i, v in enumerate(options) if 'm=' in v.lower()]
            maxSize = None if len(idx) < 1 else options[idx[0]].split('=')[1].upper()
            idx = [i for i, v in enumerate(options) if 'u=' in v.lower()]
            unique = 'N' if len(idx) < 1 else options[idx[0]].split('=')[1].upper()
            idx = [i for i, v in enumerate(options) if 'd=' in v.lower()]
            default = None if len(idx) < 1 else options[idx[0]].split('=')[1].upper()
            idx = [i for i, v in enumerate(options) if 'v=' in v.lower()]
            validValues = None if len(idx) < 1 else options[idx[0]].split('=')[1].upper()
            idx = [i for i, v in enumerate(options) if 'f=' in v.lower()]
            convertFunction = None if len(idx) < 1 else options[idx[0]].split('=')[1].upper()
            idx = [i for i, v in enumerate(options) if 'r=' in v.lower()]
            refObjectName = None if len(idx) < 1 else options[idx[0]].split('=')[1]
            idx = [i for i, v in enumerate(options) if 'rf=' in v.lower()]
            refFieldName = 'id' if len(idx) < 1 else options[idx[0]].split('=')[1]
            idx = [i for i, v in enumerate(options) if 'rd=' in v.lower()]
            refDelRule = None if len(idx) < 1 else options[idx[0]].split('=')[1]

            if dataType not in DataType.ValidTypes:
                errMessage = 'The datatype [] defined in object definition file is not a valid datatype. Must be one of the following:\n'
                errMessage += str(DataType.ValidTypes)
                raise RuntimeError(errMessage)


            targetDataType = DataType.Type[dataType][targetType][targetName]['DATATYPE']
            targetSize = DataType.Type[dataType][targetType][targetName]['DEFAULT_LEN'] if maxSize is None else maxSize
            targetDefault = DataType.Type[dataType][targetType][targetName]['DEFAULT'] if default is None else default
            targetValidValues = DataType.Type[dataType][targetType][targetName][
                'VALID_VALUES'] if validValues is None else validValues
            targetConvertFunction = DataType.Type[dataType][targetType][targetName][
                'CONVERT_FUNCTION'] if convertFunction is None else convertFunction
            # NEED TO OVERRIDE TO GUARANTEE TRUE UNIQUENESS
            if unique == 'Y' and targetConvertFunction is None:
                targetConvertFunction = 'LOWER'

            tabColLine = ' ' * ind + colName + ' '*(cis-len(colName)) + targetDataType.upper()
            tabColLine += ' '*(dtp-len(targetDataType))
            if targetSize is not None:
                tabColLine = tabColLine[:len(tabColLine)-(dtp-len(targetDataType))]
                tabColLine += '(' + targetSize + ')'
                tabColLine += ' '*(dtp-(len(targetDataType)+len(targetSize)+2))
            if targetDefault is not None:
                tabColLine += 'DEFAULT ' + targetDefault + ' '
            if allowNull == 'N':
                tabColLine += 'CONSTRAINT ' + constraintPrefix + colName.strip('_')[:17] + '#nn NOT NULL'
            tabColLine += ',\n'
            if unique == 'Y':
                uniqueColumns.append(colName)
            if targetValidValues is not None:
                validateCol = {'COLUMN_NAME': colName,
                               'VALID_VALUES': targetValidValues}
                validateColumns.append(validateCol)
            if targetConvertFunction is not None:
                fxCol = {'COLUMN_NAME': colName,
                         'CASE': targetConvertFunction}
                fxColumns.append(fxCol)
            if refObjectName is not None:
                refCol = {'COLUMN_NAME': colName,
                          'REF_TABLE': refObjectName,
                          'REF_FIELD': refFieldName,
                          'DELETE_RULE': refDelRule}
                refColumns.append(refCol)

            tableDDL += tabColLine

        tableDDL += ' ' * ind + 'created'+' '*23+'DATE'+' '*11+'CONSTRAINT ' + constraintPrefix + 'created#nn NOT NULL,\n'
        tableDDL += ' ' * ind + 'modified'+' '*22+'DATE'+' '*11+'CONSTRAINT ' + constraintPrefix + 'modified#nn NOT NULL,\n'
        tableDDL += 'CONSTRAINT '+constraintPrefix+'pk PRIMARY KEY(ID)\n'
        tableDDL += ');\n\n'

        seqDDL = self.genSequenceDDL(tableName, seqOverride)
        trigDDL = self.genTriggerDDL(tableName, fxColumns)
        ukDDL = self.genUKConstraints(tableName, uniqueColumns)
        ckDDL = self.genCKConstraints(tableName, validateColumns)
        fkDDL = self.genFKConstraints(tableName, refColumns)

        ddlBundle = {'SEQUENCE_DDL': seqDDL,
                     'TABLE_DDL': tableDDL,
                     'TRIGGER_DDL': trigDDL,
                     'UK_DDL': ukDDL,
                     'CK_DDL': ckDDL,
                     'FK_DDL': fkDDL}

        return ddlBundle

    def processObjectDefFile(self, objectDefFilename):
        ddlBundles = []

        defFile = open(objectDefFilename, 'r')
        defFileContents = []
        for line in defFile.readlines():
            if not line.startswith((';', '#', '--')) and len(line) > 0:
                defFileContents.append(line.strip('\n').strip())

        objectName = None
        tableSeqOverride = None
        objectAttributes = []
        for entry in defFileContents:
            if str(entry).endswith('{'):
                objectName = entry.split(':')[0].strip('{').strip()
                objectAttributes = []
                objectOptions = entry.split(':')[1].strip('{').strip().split(';')
                if len(objectOptions[0]) < 1:
                    raise RuntimeError('You must specify a category for all object defenitions')
                for o in objectOptions:
                    if o.lower().startswith('c=') or o.lower().startswith('category='):
                        category = o.split('=')[1]
                        validCats = ['AD', 'DB', 'EV', 'PC', 'PQ']
                        if not category in validCats:
                            raise RuntimeError('The category specified ['+category+'] for ['+objectName+'] is not valid.  Must be one of: '+
                                               str(validCats))
                    elif o.lower().startswith('s=') or o.lower().startswith('sequence='):
                        tableSeqOverride = o.split('=')[1]
            elif str(entry).endswith('}'):
                objectDef = {'NAME': objectName,
                             'CATEGORY': category,
                             'SEQ_OVERRIDE': tableSeqOverride,
                             'ATTRIBUTES': objectAttributes}
                self.ObjectName = objectName
                self.ObjectCat = category

                tableBundle = self.genTableDDLBundle(objectDef)
                ddlBundles.append(tableBundle)
                objectName = None
                objectAttributes = []
                tableSeqOverride = None
            else:
                # PROCESS LINE AS ATTRIBUTE LINE
                objectAttributes.append(entry)

        return ddlBundles


class DatabaseReverseEngineer:

    def __init__(self, sourceFilename):
        self.SourceFileName = sourceFilename
        self.ObjectTypes = ['SEQUENCE', 'TYPE', 'TABLE', 'TRIGGER', 'VIEW', 'FUNCTION', 'PROCEDURE',
                            'PACKAGE', 'QUEUE']

    def __parseSourceFile(self):
        defFile = open(self.SourceFileName, 'r')
        for line in defFile.readlines():
            if len(line) > 1:
                line = line.strip()




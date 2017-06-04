[ORACLE]
UserPrivileges = {'{{APPNAME}}_DBO': {'SYSTEM': ['create session',
                                                 'create any synonym',
                                                 'create table',
                                                 'create view',
                                                 'create procedure',
                                                 'create trigger',
                                                 'create sequence',
                                                 'unlimited tablespace',
                                                 'create type',
                                                 ],
                                      'OBJECT': {'VIEWS': {'SELECT': ['SYS.V_$DATABASE',
                                                                      'SYS.V_$INSTANCE']},
                                                 'PACKAGES': {'EXECUTE': ['SYS.DBMS_LOCK']},
                                                 'TYPES': {'EXECUTE': []}
                                                 }
                  '{{APPNAME}}_USR': {'SYSTEM': ['create session'],
                                      'OBJECT': {'TABLES': {'SELECT': ['*']},
                                                 'VIEWS': {'SELECT': ['*']},
                                                 'PACKAGES': {'EXECUTE': ['*']},
                                                 'TYPES': {'EXECUTE': ['*']}
                                                 }
                  }
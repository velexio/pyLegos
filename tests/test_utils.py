from unittest import TestCase
from pylegos.utils import NameConverter


class TestNameConverter(TestCase):

    def test_getObjectName(self):
        rn = 'app'
        cn = NameConverter.getObjectName(rn)
        self.assertEqual(cn, 'App')
        rn = 'app_log'
        cn = NameConverter.getObjectName(rn)
        self.assertEqual(cn, 'AppLog')
        rn = 'app log'
        cn = NameConverter.getObjectName(rn)
        self.assertEqual(cn, 'AppLog')
        rn = 'App Log'
        cn = NameConverter.getObjectName(rn)
        self.assertEqual(cn, 'AppLog')
        rn = 'appLog'
        cn = NameConverter.getObjectName(rn)
        self.assertEqual(cn, 'AppLog')
        rn = 'AppLog'
        cn = NameConverter.getObjectName(rn)
        self.assertEqual(cn, 'AppLog')
        rn = 'a really_weird_example test'
        cn = NameConverter.getObjectName(rn)
        self.assertEqual(cn, 'AReallyWeirdExampleTest')

    def test_getMethodName(self):
        rn = 'AppLog'
        cn = NameConverter.getMethodName(rn)
        self.assertEqual(cn, 'appLog')

    def test_objectToDBTable(self):
        rn = 'AppLog'
        cn = NameConverter.objectToDBTable(rn)
        self.assertEqual(cn, 'app_logs')
        rn = 'App Log'
        cn = NameConverter.objectToDBTable(rn)
        self.assertEqual(cn, 'app_logs')
        rn = 'AppDBA'
        cn = NameConverter.objectToDBTable(rn)
        self.assertEqual(cn, 'app_dbas')

    def test_toDatabaseFieldName(self):
        rn = 'appLog'
        cn = NameConverter.toDatabaseFieldName(rn)
        self.assertEqual(cn, 'app_log')
        rn = 'app_Log'
        cn = NameConverter.toDatabaseFieldName(rn)
        self.assertEqual(cn, 'app_log')
        rn = 'appLOg'
        cn = NameConverter.toDatabaseFieldName(rn)
        self.assertEqual(cn, 'app_log')
        rn = 'app_LOg'
        cn = NameConverter.toDatabaseFieldName(rn)
        self.assertEqual(cn, 'app_log')
        rn = 'appDBA'
        cn = NameConverter.toDatabaseFieldName(rn)
        self.assertEqual(cn, 'app_dba')

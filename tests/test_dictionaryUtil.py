from unittest import TestCase

from src.velexio.pylegos.core import DictionaryUtil


# noinspection PyDictCreation
class TestDictionaryUtil(TestCase):
    SUT = DictionaryUtil()

    def test_toFormattedString(self):
        simpleMap = {}
        simpleMap['Key'] = 'Value'
        '''
        simpleF = self.SUT.toFormattedString(dictObj=simpleMap)
        self.assertEqual(simpleF,'Key : Value\n')

        '''
        multiLevelMap = {}
        multiLevelMap['L1K1'] = simpleMap
        multiLevelMap['L1K2'] = simpleMap
        '''
        multiF = self.SUT.toFormattedString(dictObj=multiLevelMap)
        print(multiF)
        self.assertEqual(multiF,'L1K1 : Key : Value\n')
        '''

        D3Map = {}
        D3Map['D3Key1'] = multiLevelMap
        D3Map['D3Key2'] = multiLevelMap
        D3Map['Logging'] = {'LogLevel':'DEBUG','LogFile':'/tmp/test.log','ConsoleFormat':'::|'}
        D3Map['CONTACTS'] = ['Mary','Amy','Beth','Betsie','Sara']
        d3F = self.SUT.formatToString(D3Map)
        print(d3F)
        self.assertEqual(d3F,'D3Key1 : \n')






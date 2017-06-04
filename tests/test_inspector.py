from unittest import TestCase
from unittest import main

from pylegos.core import Inspector


#USE CASE 1:  Called from the different types of methods that can be contained inside a class
class sut1(object):
    #USE CASE 2: Called from a nested class
    class sut1nested(object):
        @staticmethod
        def getCallerFromNestedStaticMethod(sutMethod):
            return sutMethod()
        @classmethod
        def getCallerFromNestedClassMethod(cls,sutMethod):
            return sutMethod()
        def getCallerFromNestedObjMethod(self,sutMethod):
            return sutMethod()
    @staticmethod
    def getCallerFromStaticMethod(sutMethod):
        return sutMethod()
    @classmethod
    def getCallerFromClassMethod(cls,sutMethod):
        return sutMethod()
    def getCallerFromObjMethod(self,sutMethod):
        return sutMethod()

#USE CASE 3: Called from a module level method
def test_getCallerFromModMethod(sutMethod):
    return sutMethod()

#USE CASE 4: Caller is from different types of methods in a class
class sut2(object):
    #USE CASE 5: Caller is from a nested class
    #  This will also have calls from this nested class to
    #  the sut1nested class.  Will come as as the sut1method arg
    class sut2nested(object):
        @staticmethod
        def calledFromNestedStaticMethod(sut1Method,sutTestMethod):
            return sut1Method(sutMethod=sutTestMethod)
        @classmethod
        def calledFromNestedClassMethod(cls,sut1Method,sutTestMethod):
            return sut1Method(sutMethod=sutTestMethod)
        def calledFromNestedObjMethod(self,sut1Method,sutTestMethod):
            return sut1Method(sutMethod=sutTestMethod)
    @staticmethod
    def calledFromStaticMethod(sut1Method,sutTestMethod):
        return sut1Method(sutMethod=sutTestMethod)
    @classmethod
    def calledFromClassMethod(cls,sut1Method,sutTestMethod):
        return sut1Method(sutMethod=sutTestMethod)



#USE CASE 6: Caller is a module level method
def test_calledFromModMethod():
    # THIS NEEDS TO BE IN THE FORMAT OF Inspector.<methodToTest>:'<ExpectedValueToReturn>
    sutTestMethods = {Inspector.getCallerFQN:'test_inspector.test_calledFromModMethod',
                      Inspector.getCallerClass:None,
                      Inspector.getCallerMod:'test_inspector',
                      Inspector.getCallerFunc:'test_calledFromModMethod'}

    for testFx,expectVal in sutTestMethods.items():
        for sutTest in [sut1.getCallerFromStaticMethod,
                        sut1.getCallerFromClassMethod,
                        sut1().getCallerFromObjMethod,
                        sut1.sut1nested.getCallerFromNestedStaticMethod,
                        sut1.sut1nested.getCallerFromNestedClassMethod,
                        sut1.sut1nested().getCallerFromNestedObjMethod]:
            testRetVal = sutTest(sutMethod=testFx)
            TestCase().assertEqual(expectVal,testRetVal,'Failed on call to |::|'+str(testFx)+'|::| for function type |::|'+str(sutTest)+'|::| from module method |::|test_calledFromModMethod|::|')

        testRetval = test_getCallerFromModMethod(sutMethod=testFx)
        TestCase().assertEqual(expectVal,testRetVal,'Failed on call to |::|'+str(testFx)+'|::| from function type |::|test_getCallerFromModMethod|::|  from module method |::|test_calledFromModMethod|::|')


class TestInspector(TestCase):

    def test_Inspector(self):
        # THIS WILL CALL ALL CALLER TESTS FOR NORMAL USE CASE WHERE CALLER WILL COME FROM
        # A STANDARD CLASS/METHOD
        inspector = Inspector.Instance()

        # THIS NEEDS TO BE IN THE FORMAT OF Inspector.<methodToTest>:'<ExpectedValueToReturn>
        sutTestMethods = {inspector.getCallerFQN:'test_inspector.TestInspector.test_Inspector',
                          inspector.getCallerClass:'TestInspector',
                          inspector.getCallerMod:'test_inspector',
                          inspector.getCallerFunc:'test_Inspector'}

        for testFx,expectVal in sutTestMethods.items():
            for sutTest in [sut1.getCallerFromStaticMethod,
                            sut1.getCallerFromClassMethod,
                            sut1().getCallerFromObjMethod,
                            sut1.sut1nested.getCallerFromNestedStaticMethod,
                            sut1.sut1nested.getCallerFromNestedClassMethod,
                            sut1.sut1nested().getCallerFromNestedObjMethod]:
                testRetVal = sutTest(sutMethod=testFx)
                self.assertEqual(expectVal,testRetVal,'Failed on call to <'+str(testFx)+'> for function type ['+str(sutTest)+']')

            testRetval = test_getCallerFromModMethod(sutMethod=testFx)
            self.assertEqual(expectVal,testRetVal,'Failed on call to <'+str(testFx)+'> for function type [test_getCallerFromModMethod]')

        # NOW CALL ALL TESTS FOR USE CASES FOR DIFFERENT TYPES OF CALLERS
        test_calledFromModMethod()

        #rv = sut2.calledFromStaticMethod(sut1Method=sut1.getCallerFromStaticMethod,sutTestMethod=Inspector.getCallerFQN)
        #self.assertEqual('test_inspector.sut2.calledFromStaticMethod',rv,'failed on poc')
        # TODO  FIX CALL TO GET CLASS WHEN CALLED FROM STATIC METHOD
        #rv = sut2.calledFromStaticMethod(sut1Method=sut1.getCallerFromStaticMethod,sutTestMethod=Inspector.getCallerClass)
        #self.assertEqual('calledFromStaticMethod',rv,'failed on poc')

    @classmethod
    def test_InspectorFromStatic(cls):
        inspector = Inspector.Instance()
        rv = sut1().getCallerFromStaticMethod(sutMethod=inspector.getCallerClass)
        TestCase().assertEqual('TestInspector',rv)

if __name__ == '__main__':
    #TestInspector.test_InspectorStatics()
    main()

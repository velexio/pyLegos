from inflect import engine as inflectEngine


class NameConverter:

    @staticmethod
    def __camelCase(name):
        newName = name[:1].lower()
        convPortion = name[1:]
        upperNext = False
        for c in convPortion:
            if upperNext:
                newChar = c.upper()
                upperNext = False
            else:
                newChar = c
                if c == '_' or c == ' ':
                    newChar = ''
                    upperNext = True
            newName += newChar
        return newName

    @staticmethod
    def getObjectName(name):
        camelName = NameConverter.__camelCase(name)
        return camelName[:1].upper()+camelName[1:]

    @staticmethod
    def getMethodName(name):
        return NameConverter.__camelCase(name)

    @staticmethod
    def __underscoreName(name):
        newName = name[:1].lower()
        convertPart = name[1:].replace(' ', '')
        prevChar = ''
        prevC = ''
        for c in convertPart:
            newChar = c
            if c.isupper():
                if prevChar.startswith('_') or prevC.isupper():
                    newChar = c.lower()
                else:
                  newChar = '_'+c.lower()
            prevChar = newChar
            prevC = c
            newName += newChar
        newName = newName.lower()
        return newName

    @staticmethod
    def objectToDBTable(name, pluralize=True):
        newName = NameConverter.__underscoreName(name)
        if pluralize:
            newName = inflectEngine().plural(newName)

        return newName

    @staticmethod
    def toDatabaseFieldName(name):
        return NameConverter.__underscoreName(name)

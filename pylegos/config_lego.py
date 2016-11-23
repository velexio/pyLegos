import logging

from collections import OrderedDict
from ConfigParser import RawConfigParser
from vxlogging import LogHelper


class ConfigHelper(object):
    ###############
    # CLASS VARS
    ###############
    Config = None
    Logger = None

    ###############

    def __init__(self):
        LogHelper().addNullHandler()
        self.Logger = logging.getLogger(__name__)

    def getConfig(self, configFile):
        config = RawConfigParser()
        config.optionxform = str
        self.Logger.debug('Reading configuration file [' + configFile + ']')
        config.read(configFile)
        return config

    def getConfigValue(self, configFile, sectionName, propertyName):
        config = self.getConfig(configFile)
        self.Logger.debug('Returning value from section [' + sectionName + '], property [' + propertyName + ']')
        return config.get(sectionName, propertyName)

    def getConfigKeys(self, configFile, sectionName):
        config = self.getConfig(configFile)
        self.Logger.debug('Getting all properties for section [' + sectionName + ']')
        return config.options(sectionName)

    def getConfigMap(self, configFile):
        configMap = OrderedDict()
        config = self.getConfig(configFile)

        self.Logger.debug('Building config map')

        for s in config.sections():
            self.Logger.debug('Building section [' + s + ']')
            sectionMap = {}
            for k in config.options(s):
                self.Logger.debug('Getting value for key [' + k + ']')
                sectionMap[k] = config.get(s, k)

            self.Logger.debug('Adding section map ||' + str(sectionMap) + '|| to the config map')
            configMap[s] = sectionMap

        self.Logger.debug('Returning config map ||' + str(configMap) + '||')
        return configMap

    def setConfigValue(self, configFile, section, key, value):
        config = self.getConfig(configFile)
        self.Logger.debug(
            'Setting config value [' + value + '] for section [' + section + '] and property [' + key + ']')
        config.set(section, key, value)
        file = open(configFile, 'w')
        self.Logger.debug('Writing changes to file')
        config.write(file)

    def writeConfigMap(self, configMap, fileName):
        config = self.getConfig(fileName)

        self.Logger.debug('Building the config from map object')
        for s in configMap:
            self.Logger.debug('Building section [' + s + ']')
            config.add_section(s)
            for k in configMap[s]:
                self.Logger.debug('Adding property [' + k + '] with value [' + configMap[s][k] + ']')
                config.set(s, k, configMap[s][k])

        self.Logger.debug('Opening config file [' + fileName + '] for write')
        file = open(fileName, 'w')
        self.Logger.debug('Writing config to the file')
        config.write(file)

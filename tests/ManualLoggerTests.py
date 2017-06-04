
from pylegos import LogFactory

def consoleOnlyTest():

    logFactory = LogFactory()
    logLevel = logFactory.LogLevel.INFO
    log = logFactory.getConsoleLogger()

    log.debug('This is a console debug message')
    log.info('This is an console info message')
    log.warn('This is a warning message')
    log.error('This is a error message')
    log.critical('This is a critical message')

    log.info('Logging to a file now')

    fileLogger = logFactory.getFileLogger('/tmp/ManLogTest.log',logFactory.LogLevel.DEBUG)
    fileLogger.debug('Debug message for file')
    fileLogger.info('Info message for file')
    fileLogger.warn('Warn message for file')
    fileLogger.error('Error message for file')
    fileLogger.critical('Critical message for file')




def main():
    consoleOnlyTest()


if __name__ == '__main__':
    main()
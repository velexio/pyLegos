import os
import sys

from progress.bar import IncrementalBar
from progress.spinner import MoonSpinner
from progress.spinner import PieSpinner
from progress.spinner import Spinner as ProgressSpinner

from src.velexio.pylegos.core import LogFactory


class SpinnerType(object):
    """ Used as a enum type of class, used to set the type of spinner to use
    when initializing a Spinner object
    Options are: Clock (default), Cicle, and classic
    """
    Clock = PieSpinner
    Circle = MoonSpinner
    Classic = ProgressSpinner


class Spinner(object):
    """
    Creates a Spinner to use for operations that run for some time and can be used to give the
    user the indication that the process is taking some time, but still running.  Most of the
    work in this class is performed by the progress module (found on PyPi, written by Giorgos Verigakis)
    This is just a thin wrapper to used by this framework so to reduce repitition and provide
    some customizations.
    """

    def __init__(self, message='Running ', spinnerType=SpinnerType.Classic):
        """
        This will iniatialize a spinner class.
        :param message: The message to display in front of spinner.  Default is 'Running '
        :param spinnerType: The type of spinner.  Use the SpinnerType class to override default, SpinnerType.Clock
        """
        self.spinnerMessage = message
        self.spinner = spinnerType(message)

    def spin(self):
        """
        This will make the spinner animate to the next phase character, making it appear to move
        :return: None
        """
        self.spinner.next()

    def stop(self):
        """
        While it is not 100% necessary to call this method at the end of the spinner cycle, it will clean up the
        console by completely removing the message and spinner character.
        :return:
        """
        sys.stdout.write('\b'*(len(self.spinnerMessage)+2))
        sys.stdout.flush()
        sys.stderr.write('\r ')


class ProgressBar(object):
    """
    Creates an IncrementalBar object (from the progress package) with suffix set to show percentage complete to
    one decimal place and also give an ETA.
    """

    def __init__(self, initialMessage, numOperations):
        """
        Will create in instance of a progress bar.
        :param initialMessage:  Used to set the initial message to be displayed in front of the message bar.  This
                                message can be updated after the progress bar has been 'started' by calling the
                                updateMessage method.
        :param numOperations: The total number of operations that the progress bar will cover.
        """
        self.bar = IncrementalBar(message=initialMessage, max=numOperations, suffix='%(percent).1f%% - %(eta)ds')
        self.bar.update()

    def updateProgress(self):
        """
        This will update or move the progress bar.  Call this after each step of the operation completes.
        :return: None
        """
        self.bar.next()

    def updateMessage(self, message):
        """Will update the message displayed in front of the progress bar
        :message: The new message to display
        :return: None
        """
        self.bar.message = message
        self.bar.update()

    def updateStatus(self):
        """Will update the status of the progress bar
        :return: None
        """
        self.bar.update()

    def finish(self):
        """
        This will complete the progress bar to 100%.
        :return: None
        """
        self.bar.finish()

class TermColor(object):

    def __init__(self):
        self.RESET = '\033[0m'

    class Style(object):
        BOLD = 1
        DARK = 2
        UNDERLINE = 4
        BLINK = 5
        REVERSE = 7
        CONCEALED = 8

    class Color(object):
        GREY = 30
        RED = 31
        GREEN = 32
        YELLOW = 33
        BLUE = 34
        MAGENTA = 35
        CYAN = 36
        WHITE = 37

    class Background(object):
        GREY = 40
        RED = 41
        GREEN = 42
        YELLOW = 43
        BLUE = 44
        MAGENTA = 45
        CYAN = 46
        WHITE = 47

    def colorMessage(self, message, textColor, textBackground=None, textStyle=None):
        message = ' '+message+' '
        if os.getenv('ANSI_COLORS_DISABLED') is None:
            colorFormat = '\033[%dm%s'
            message = colorFormat % (textColor, message)
            if textBackground is not None:
                message = colorFormat % (textBackground, message)
            if textStyle is not None:
                message = colorFormat % (textStyle, message)
            message += self.RESET
        return message

    def cprint(self, message, textColor, textBackground=None, textStyle=None, printNewLine=True):
        coloredMessage = self.colorMessage(message=message,
                                          textColor=textColor,
                                          textBackground=textBackground,
                                          textStyle=textStyle)
        if printNewLine:
            print(coloredMessage)
        else:
            sys.stdout.write(coloredMessage)
            sys.stdout.flush()


class TermUI(object):
    """
    Class to aide in UI operations at the console/terminal
    """

    def __init__(self):
        self.logger = LogFactory().getLibLogger()

    def getUserInput(self, promptMessage, caseSenstiveMatching=False, validChoices=[], defaultChoice=None, listChoices=False, secureMode=False):
        """
        This will capture user input at the terminal.
        :param promptMessage: The message to display to the user <BR>
        :param caseSenstiveMatching: Optional. Boolean to indicate if the user input must match in case sensitive manner to validChoices. Default: False<br>
        :param validChoices: Optional.  A list of valid choices that will be validated against user input. Default: EmptyList []<br>
        :param defaultChoice: Optional. If there is a default value, supply this and if the user just hits enter, this <br>
                              will be the value returned. Default: None<br>
        :param listChoices: Optional. Boolean value to indicate you would like each choice printed on one line if the user inputs a value <br>
                            that is not in the list of validChoices.  Helpful if you have many options. Default: False<br>
        :param secureMode: Optional.  This will cause the input to not be echoed to the terminal.  Use this if gathering password or other<br>
                           sensitive data.  Default: False<br>
        :return: Users Input as String value<br>
        """
        validInput = False
        if len(validChoices) > 0:
            while not validInput:
                if len(validChoices) <= 3 and defaultChoice is None:
                    displayMessage = promptMessage + ' '+str(validChoices)+': '
                elif defaultChoice is not None:
                    displayMessage = promptMessage + ' ['+defaultChoice+']: '
                userInput = raw_input(displayMessage)
                if len(userInput) == 0 and defaultChoice is not None:
                    userInput = defaultChoice
                if caseSenstiveMatching:
                    if userInput in validChoices:
                        validInput = True
                else:
                    if userInput.upper() in validChoices or userInput.lower() in validChoices:
                        validInput = True
                if not validInput:
                    if listChoices:
                        self.logger.info('You must supply one of the following choices:')
                        for c in validChoices:
                            self.logger.info(str(c))
                    else:
                        self.logger.info('You must supply one of the following choices: '+str(validChoices))
        else:
            if secureMode:
                import getpass
                userInput = getpass.getpass(promptMessage)
            else:
                userInput = raw_input(promptMessage)

        return str(userInput)



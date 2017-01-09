import sys

from progress.spinner import Spinner as ProgressSpinner
from progress.spinner import PieSpinner
from progress.spinner import MoonSpinner
from progress.bar import IncrementalBar


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

    def __init__(self,message='Running ', spinnerType=SpinnerType.Clock):
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
        sys.stdout.write('\b'*(len(self.spinnerMessage)+1))
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

    def updateProgress(self):
        """
        This will update or move the progress bar.  Call this after each step of the operation completes.
        :return: None
        """
        self.bar.next()

    def updateMessage(self, message):
        """Will update the message displayed in front of the progress bar
        :message: The new message to display
        """
        self.bar.message = message

    def finish(self):
        """
        This will complete the progress bar to 100%.
        :return: None
        """
        self.bar.finish()


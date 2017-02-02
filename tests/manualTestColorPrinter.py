#!/usr/bin/env python

import time
from velexio.pylegos.core.termlegos import TermColor


def main():
    fail = " Failed "
    bold = " BOLD "
    status = " Running test: "
    result = " Passed "
    cprinter = TermColor()
    cprinter.printInColor(message=fail, textColor=TermColor.Color.YELLOW, textBackground=TermColor.Background.RED, textStyle=TermColor.Style.BLINK)
    cprinter.printInColor(message=bold, textColor=TermColor.Color.WHITE, textBackground=TermColor.Background.BLUE, textStyle=TermColor.Style.BOLD)
    cprinter.printInColor(message=status, textColor=TermColor.Color.WHITE, textBackground=TermColor.Background.BLUE, printNewLine=False)
    time.sleep(5)
    cprinter.printInColor(message=result, textColor=TermColor.Color.WHITE, textBackground=TermColor.Background.GREEN, textStyle=TermColor.Style.BOLD)
    cprinter.printInColor(message=status, textColor=TermColor.Color.WHITE, textBackground=TermColor.Background.BLUE, printNewLine=False)
    time.sleep(3)
    cprinter.printInColor(message=fail, textColor=TermColor.Color.YELLOW, textBackground=TermColor.Background.RED, textStyle=TermColor.Style.BLINK)

if __name__ == '__main__':
    main()

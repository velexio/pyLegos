#!/usr/bin/env python

import time
from velexio.pylegos.core.termlegos import ColorPrinter


def main():
    fail = " Failed "
    bold = " BOLD "
    status = " Running test: "
    result = " Passed "
    cprinter = ColorPrinter()
    cprinter.printInColor(message=fail, textColor=ColorPrinter.Color.YELLOW, textBackground=ColorPrinter.Background.RED, textStyle=ColorPrinter.Style.BLINK)
    cprinter.printInColor(message=bold, textColor=ColorPrinter.Color.WHITE, textBackground=ColorPrinter.Background.BLUE, textStyle=ColorPrinter.Style.BOLD)
    cprinter.printInColor(message=status, textColor=ColorPrinter.Color.WHITE, textBackground=ColorPrinter.Background.BLUE, printNewLine=False)
    time.sleep(5)
    cprinter.printInColor(message=result, textColor=ColorPrinter.Color.WHITE, textBackground=ColorPrinter.Background.GREEN, textStyle=ColorPrinter.Style.BOLD)
    cprinter.printInColor(message=status, textColor=ColorPrinter.Color.WHITE, textBackground=ColorPrinter.Background.BLUE,  printNewLine=False)
    time.sleep(3)
    cprinter.printInColor(message=fail, textColor=ColorPrinter.Color.YELLOW, textBackground=ColorPrinter.Background.RED, textStyle=ColorPrinter.Style.BLINK)

if __name__ == '__main__':
    main()

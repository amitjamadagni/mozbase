# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from logging import getLogger as getSysLogger
from logging import *
# Some of the build slave environments don't see the following when doing
# 'from logging import *'
# see https://bugzilla.mozilla.org/show_bug.cgi?id=700415#c35
from logging import getLoggerClass, addLevelName, setLoggerClass, shutdown

_default_level = INFO
_LoggerClass = getLoggerClass()

# Define mozlog specific log levels
START      = _default_level + 1
END        = _default_level + 2
PASS       = _default_level + 3
KNOWN_FAIL = _default_level + 4
FAIL       = _default_level + 5
CRASH      = _default_level + 6
# Define associated text of log levels
addLevelName(START, 'TEST-START')
addLevelName(END, 'TEST-END')
addLevelName(PASS, 'TEST-PASS')
addLevelName(KNOWN_FAIL, 'TEST-KNOWN-FAIL')
addLevelName(FAIL, 'TEST-UNEXPECTED-FAIL')
addLevelName(CRASH, 'PROCESS-CRASH')

class MozLogger(_LoggerClass):
    """
    MozLogger class which adds some convenience log levels
    related to automated testing in Mozilla
    """
    def testStart(self, message, *args, **kwargs):
        """Logs a test start message"""
        self.log(START, message, *args, **kwargs)

    def testEnd(self, message, *args, **kwargs):
        """Logs a test end message"""
        self.log(END, message, *args, **kwargs)

    def testPass(self, message, *args, **kwargs):
        """Logs a test pass message"""
        self.log(PASS, message, *args, **kwargs)

    def testFail(self, message, *args, **kwargs):
        """Logs a test fail message"""
        self.log(FAIL, message, *args, **kwargs)

    def testKnownFail(self, message, *args, **kwargs):
        """Logs a test known fail message"""
        self.log(KNOWN_FAIL, message, *args, **kwargs)

    def processCrash(self, message, *args, **kwargs):
        """Logs a process crash message"""
        self.log(CRASH, message, *args, **kwargs)

class _MozFormatter(Formatter):
    """
    MozFormatter class used to standardize formatting
    If a different format is desired, this can be explicitly
    overriden with the log handler's setFormatter() method
    """
    level_length = 0
    max_level_length = len('TEST-START')

    def __init__(self):
        """
        Formatter.__init__ has fmt and datefmt parameters that won't have
        any affect on a MozFormatter instance. Bypass it to avoid confusion.
        """

    def format(self, record):
        record.message = record.getMessage()

        # Handles padding so record levels align nicely
        if len(record.levelname) > self.level_length:
            pad = 0
            if len(record.levelname) <= self.max_level_length:
                self.level_length = len(record.levelname)
        else:
            pad = self.level_length - len(record.levelname) + 1
        sep = '|'.rjust(pad)
        fmt = '%(name)s %(levelname)s ' + sep + ' %(message)s'
        return fmt % record.__dict__

def getLogger(name, logfile=None):
    """
    Returns the logger with the specified name.
    If the logger doesn't exist, it is created.

    :param name: The name of the logger to retrieve
    :param logfile: If specified, the logger will log to the specified file. 
                    Otherwise, the logger logs to stdout.
                    This parameter only has an effect if the logger doesn't already exist.
    """
    setLoggerClass(MozLogger)

    if name in Logger.manager.loggerDict:
        return getSysLogger(name)

    logger = getSysLogger(name)
    logger.setLevel(_default_level)

    if logfile:
        handler = FileHandler(logfile)
    else:
        handler = StreamHandler()
    handler.setFormatter(_MozFormatter())
    logger.addHandler(handler)
    return logger


import os
import re
from datetime import datetime
# JayTAKObjLib

# Objects:
# Custom Exceptions:

# Custom exception to handle server response codes.


class WeatherServerException(Exception):

    def __init__(self, errorCode, message="WeatherServerException: Received a code that was not 200. check README.md for more information."):
        self.errorCode = errorCode
        self.message = message
        super().__init__(self.message, self.errorCode)


# Custom exception to handle invalid usage.
class UsageException(Exception):

    def __init__(self, message="UsageException: Invalid Usage!"):
        self.message = message
        super().__init__(self.message)


# Other Objects:
# Date and time object.
class DTimeLive:
    def getTime(self):
        return datetime.now()

    def getFormattedTime(self, dt):
        return dt.strftime("[%H.%M.%S][%d-%m-%Y]")

    def getLogFormattedTime(self, dt):
        return dt.strftime("[%H:%M:%S][%d-%m-%Y]")

    def getLocalFormattedTime(self, timestamp, timezoneOffset):
        localTimeSeconds = timestamp + timezoneOffset
        return datetime.utcfromtimestamp(localTimeSeconds).strftime("[%H:%M:%S][%d-%m-%Y]")

    def getSunFormattedTime(self, timestamp, timezoneOffset):
        localTimeSeconds = timestamp + timezoneOffset
        return datetime.utcfromtimestamp(localTimeSeconds).strftime("%H:%M:%S")


# Logger Object.
class ActionLogger:  # Levels in order: TRACE, DEBUG, INFO, NOTICE, WARN, ERROR, FATAL
    def __init__(self, logFile="weatherAppActions.log"):
        self.logFile = logFile

    def logMsg(self, message, level="INFO"):
        time = DTimeLive()
        separator = " - "
        match(level):
            case "WARN" | "INFO":
                separator = " --- "
            case "ALERT" | "TRACE" | "DEBUG" | "ERROR" | "FATAL":
                separator = " -- "
            case "NOTICE":
                separator = " - "
        timestamp = time.getLogFormattedTime(time.getTime())
        logEntry = f"{timestamp}[{level}]{separator}{message}\n"
        with open(self.logFile, 'a') as file:
            file.write(logEntry)
        return


# Log prune object for logs folder and sub-folders.
class LogPruner:

    def __init__(self, basePath, maxSeconds="21600"):
        self.basePath = basePath
        self.maxSeconds = maxSeconds

    def pruneLogs(self):
        KEY = True
        names = ""
        removedFiles = 0
        logger = ActionLogger()
        logger.logMsg(
            f"Function 'LogPruner.pruneLogs' called with base path {self.basePath} and max seconds is set to {self.maxSeconds}")
        time = datetime.now()
        pattern = re.compile(r'(\w+)\[(\d+\.\d+\.\d+)\]\[(\d{2}-\d{2}-\d{4})\]\.json')
        for filename in os.listdir(self.basePath):
            filepath = os.path.join(self.basePath, filename)
            if os.path.isfile(filepath):
                fileMatch = pattern.match(filename)
                if pattern.match(filename):
                    fileName, timeStr, dateStr = fileMatch.groups()
                    timestampStr = f"{dateStr} {timeStr}"
                    fileTime = datetime.strptime(timestampStr, "%d-%m-%Y %H.%M.%S")
                    timeDifference = time - fileTime
                    if timeDifference.total_seconds() > float(self.maxSeconds):
                        if KEY:
                            names += f"{filename}, "
                            removedFiles += 1
                            os.remove(filepath)
                        else:
                            logger.logMsg(f"Function 'LogPruner.pruneLogs' KEY disabled, unable to remove {filename}", "TRACE")
                    else:
                        logger.logMsg(
                            f"Function 'LogPruner.pruneLogs' File {filename} not old enough yet, current time: {time}, file time: {fileTime} time difference: {timeDifference}", "DEBUG")
                else:
                    logger.logMsg(f"Function 'LogPruner.pruneLogs' file {filepath} does not match pattern", "DEBUG")
        names = names.rstrip(", ")
        logger.logMsg(f"Function 'LogPruner.pruneLogs' removed {removedFiles} file{'s' if removedFiles != 1 else ''}: {names}")
        return removedFiles


# Log prune object for a single log file.
class LogFilePruner:

    def __init__(self, filePath, maxLines="10000", pruneMultiplier="0.8"):
        self.filePath = filePath
        self.maxLines = int(maxLines)
        self.pruneMultiplier = float(pruneMultiplier)
        self.calculatedPrune = round(self.maxLines * self.pruneMultiplier)

    def pruneLogFile(self):
        logger = ActionLogger()
        logger.logMsg(
            f"Function 'LogFilePruner.pruneLogFile' called. Max Lines: {self.maxLines} Calculated-Prune: {self.calculatedPrune} Using Multiplier: {self.pruneMultiplier}", "INFO")
        linesRemoved = 0
        try:
            with open(self.filePath, 'r') as file:
                lines = file.readlines()
            length = len(lines)
            if length > self.maxLines:
                linesToKeep = lines[length - self.calculatedPrune:]
                with open(self.filePath, 'w') as file:
                    file.writelines(linesToKeep)
                linesRemoved = length - len(linesToKeep)
                logger.logMsg(
                    f"Function 'LogFilePruner.pruneLogFile' length of {self.filePath} was {length} which exceeded limit of {self.maxLines}. Removed {linesRemoved} lines and has been pruned to {len(linesToKeep)}, calculated with the multiplier: {self.pruneMultiplier}.", "INFO")

        except Exception as e:
            print(e)
        return linesRemoved

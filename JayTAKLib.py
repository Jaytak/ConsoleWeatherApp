import os
import sys
import math
import json
import shutil
import argparse
import requests
import platform
from pyfiglet import Figlet
from JayTAKObjectLib import WeatherServerException, DTimeLive, ActionLogger, LogPruner, LogFilePruner

# JayTAKLib
liveTime = DTimeLive()
logger = ActionLogger()


# Functions:
# Function to pull the weather data from the response and print it.
def parsePrintWeather(response, data, unit, spd, DEBUG):
    logger.logMsg(
        f"Function 'parsePrintWeather' called with the following passed parameters: {response}, {unit}, {spd}, {DEBUG}, along with the weather data logged at /logs/getWeather{liveTime.getFormattedTime(liveTime.getTime())}.json", "NOTICE")
    if DEBUG:
        print("DEBUG~finalProj:main(): Called codeCheck()")
    codeCheck(response, DEBUG)

    timezone = data.get("timezone", "N/A")     # Default to N/A if data isn't available.
    timezoneOffset = data.get("timezone_offset", "N/A")
    current = data.get("current", {})          # Default to an empty dictionary if "current" does not exist.
    weather = current.get("weather", [{}])[0]  # Default to a list with an empty dictionary if "weather" does not exist.
    dt = current.get("dt", "N/A")
    sunrise = current.get("sunrise", "N/A")
    sunset = current.get("sunset", "N/A")
    description = weather.get("description", "N/A").capitalize()
    temp = current.get("temp", "N/A")
    feelsLike = current.get("feels_like", "N/A")
    pressure = current.get("pressure", "N/A")
    humid = current.get("humidity", "N/A")
    dewPoint = current.get("dew_point", "N/A")
    uvi = current.get("uvi", "N/A")
    cloudCover = current.get("clouds", "N/A")
    windSpd = current.get("wind_speed", "N/A")
    windDeg = current.get("wind_deg", "N/A")
    windArrow = degToArrow(windDeg) if windDeg != "N/A" else "N/A"
    windCardinal = degToCardinal(windDeg) if windDeg != "N/A" else "N/A"
    windGust = current.get("wind_gust", "N/A")

    if windSpd != "N/A":
        windKPH = mPSToKPH(windSpd) if unit == "°C" else ""
    else:
        windKPH = "N/A"

    if windGust != "N/A":
        gustKPH = mPSToKPH(windGust) if unit == "°C" else ""
    else:
        gustKPH = "N/A"

    localTime = liveTime.getLocalFormattedTime(dt, timezoneOffset)
    localRise = liveTime.getSunFormattedTime(sunrise, timezoneOffset)
    localSet = liveTime.getSunFormattedTime(sunset, timezoneOffset)
    print(
        f"Timezone:...... {timezone}\nLocal Time:.... {localTime}\nSunrise/Sunset: ⬆ [{localRise}] ⬇ [{localSet}]\nWeather:....... {description}\nClouds:........ {cloudCover} %\nTemp:.......... {temp} {unit}\nFeels Like:.... {feelsLike} {unit}")
    print(f"Dew Point:..... {dewPoint} {unit}\nPressure:...... {pressure} hPa\nHumidity:...... {humid} %\nUV Index:...... {uvi}\nWind Speed:.... {windSpd} {spd}{windKPH}, {windArrow} {windDeg}° ({windCardinal})\nGusting:....... {windGust} {spd}{gustKPH}")
    if DEBUG and input("DEBUG~JayTAKLib:parsePrintWeather(): Would you like to see the json data? [y/n]: ").lower() == 'y':
        print(f"{data}")
    logger.logMsg(f"Function 'parsePrintWeather' complete.", "NOTICE")
    return


# Function to ask user if they would like to rerun the program
def reprompt(msg):
    logger.logMsg(f"Function 'reprompt' called")
    inp = input(f"\n{msg} ").lower()
    if inp == "y" or inp == "yes":
        logger.logMsg(f"Function 'reprompt' returning")
        return
    else:
        logger.logMsg(f"Function 'reprompt' -> sys.exit(1)")
        sys.exit(1)


# Function to raise exception if server does not respond with code 200(ok).
def codeCheck(response, debug):
    logger.logMsg(f"Function 'codeCheck' called with {response.status_code}", "TRACE")
    try:
        if response.status_code == 200:
            logger.logMsg(f"Function 'codeCheck' OK!", "TRACE")
            return
        else:
            logger.logMsg(f"Function 'codeCheck' Code INVALID!", "ERROR")
            raise WeatherServerException(response.status_code)
    except WeatherServerException as e:
        logger.logMsg(f"Function 'codeCheck' Caught Exception 'WeatherServerException' Quitting.", "ERROR")
        logger.logMsg(f"Function 'codeCheck' -> sys.exit(8)", "NOTICE")
        logger.logMsg("Logs closed.", "ALERT")
        sys.exit(8)


# Function to render text using pyfiglet in ascii text.
def renderText(textInput, textFont="banner3"):
    logger.logMsg(f"Function 'renderText' called", "TRACE")
    try:
        if not textInput:
            logger.logMsg(f"Function 'reprompt' raised a ValueError because it was not passed any text to render!")
            raise ValueError("No text was passed to render!!...")
        availableFonts = Figlet().getFonts()
        if textFont not in availableFonts:
            logger.logMsg(
                f"Function 'reprompt' raised a ValueError because the selected font '{textFont}' was not available.", "WARN")
            raise ValueError(f"Font Error:\n'{textFont}' Not Available!!...")
        fig = Figlet(font=textFont)
        print(fig.renderText(textInput))
    except BaseException as e:
        logger.logMsg(f"Function 'renderText' ran into a BaseException/Child {e}", "WARN")
        print(f"Function 'renderText' from 'JayTAKLib' ran into an exception... RIP!~{e}")
    return


# Function to get user preferred unit to use.
def getUnits():
    logger.logMsg(f"Function 'getUnits' called.")
    units = ""
    unit = ""
    spd = ""
    try:
        consoleInput = input("What units would you like to use?\n (M)etric, (I)mperial or (K)elvin ").lower()
        if consoleInput == "m" or consoleInput == "metric":
            units = "metric"
            unit = "°C"
            spd = "m/s"
        elif consoleInput == "i" or consoleInput == "imperial":
            units = "imperial"
            unit = "°F"
            spd = "mph"
        elif consoleInput == "k" or consoleInput == "kelvin" or consoleInput == "s" or consoleInput == "standard":
            units = "standard"
            unit = "K"
            spd = "m/s"
        else:
            logger.logMsg(
                f"Function 'getUnits' raised a ValueError because it was given an invalid input of {consoleInput}. Valid inputs are: 'm', 'metric', 'i', 'imperial', 'k', 'kelvin', 's', 'standard'. Please note that kelvin and standard are the same units.", "WARN")
            raise ValueError(f"Function 'getUnits' from 'JayTAKLib' ran into an exception... Input '{consoleInput}' not valid.")
    except ValueError as e:
        logger.logMsg(f"Function 'getUnits' caught ValueError: {e}", "ERROR")
        logger.logMsg(f"Function 'getUnits' Recovering from ValueError.", "ERROR")
        return getUnits()  # Return so the result will propagate up the chain of recursion.
    logger.logMsg(f"Function 'getUnits' set units to {units}. Returning.", "DEBUG")
    print(f"Units set to {units}\n")
    return units, unit, spd


# Function to parse coords depending on how the data is received from the API.
def parseCoords(data):
    logger.logMsg(f"Function 'parseCoords' called.")
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and "lat" in data[0] and "lon" in data[0]:
            lat = data[0]["lat"]
            lon = data[0]["lon"]
        else:
            raise ValueError("Invalid data format in list.")
    elif isinstance(data, dict) and "lat" in data and "lon" in data:
        lat = data["lat"]
        lon = data["lon"]
    else:
        logger.logMsg(f"Function 'parseCoords' raised a ValueError because it was passed no data or data in an invalid format, check locationbyx.json at the matching timestamp to this log.", "WARN")
        raise ValueError("Invalid data format.")
    logger.logMsg(f"Function 'parseCoords' returning Lat: {lat} Lon: {lon}", "DEBUG")
    return lat, lon


# Function to get the location name from coords.
def getLocationNameByCoords(lat, lon, geolink, apikey):
    logger.logMsg(f"Function 'getLocationNameByCoords' called.")
    url = f"{geolink}reverse?lat={lat}&lon={lon}&limit=1&appid={apikey}"
    response = requests.get(url)
    logger.logMsg(f"Function 'getLocationNameByCoords' requested from OpenWeather GEO API, received {response}")
    data = response.json()
    with open(f"logs/getLocationNameByCoords/getLocationNameByCoords{liveTime.getFormattedTime(liveTime.getTime())}.json", "w") as file:
        json.dump(data, file, indent=4)
    try:
        if isinstance(data, dict):
            message = data.get("message", "N/A")
            if message != "N/A":
                logger.logMsg(f"Function 'getLocationNameByCoords' message not N/A received was {message}")
                print(message)
                raise WeatherServerException(message)
        locationName = data[0].get("name", f"Name N/A, lat: {lat} lon: {lon}")
    except IndexError:
        locationName = f"Name N/A, lat: {lat} lon: {lon}"
        logger.logMsg(f"Function 'getLocationNameByCoords' name not available. Using lat lon instead!", "WARN")
    except WeatherServerException:
        logger.logMsg(f"Function 'getLocationNameByCoords' Caught WeatherServerException", "WARN")
        logger.logMsg(f"Function 'getLocationNameByCoords' -> sys.exit(12)")
        sys.exit(12)
    logger.logMsg(f"Function 'getLocationNameByCoords' returning location name: {locationName} logged file: {file.name}", "NOTICE")
    return locationName


# Function to calculate directory size in human readable format.
def calculateDirSize(path):
    logger.logMsg(f"Function 'calculateDirSize' called to check {path}", "DEBUG")
    totalSize = 0
    for dirPath, dirNames, fileNames in os.walk(path):
        for file in fileNames:
            filePath = os.path.join(dirPath, file)
            if not os.path.islink(filePath):  # Ignore symbolic links.
                totalSize += os.path.getsize(filePath)
    logger.logMsg(f"Function 'calculateDirSize' calling convertSize with {totalSize} then returning size for {path}", "DEBUG")
    return convertSize(totalSize)


# Function to convert bytes into human readable format.
def convertSize(bytes):
    logger.logMsg(f"Function 'convertSize' called with {bytes}", "DEBUG")
    if bytes == 0:
        return "0B"
    sizes = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    index = int(math.floor(math.log(bytes, 1024)))
    actual = math.pow(1024, index)
    inUnit = round(bytes / actual, 2)
    outputStr = f"{inUnit} {sizes[index]}"
    logger.logMsg(f"Function 'convertSize' returning {outputStr}", "DEBUG")
    return outputStr


# Function to check if the logs directory exists, if the directory does not exist it creates it.
def logFolderCheck():
    logger.logMsg(f"Function 'logFolderCheck' called.", "TRACE")
    if not os.path.exists('logs'):
        logger.logMsg(f"Function 'getLocationNameByCoords' 'logs' folder doesn't exist, creating it and sub-directories...", "WARN")
        os.makedirs('logs')
        os.makedirs('logs/getWeather')
        os.makedirs('logs/coordsByLocationName')
        os.makedirs('logs/coordsByLocationNameAndPZCode')
        os.makedirs('logs/coordsByCodes')
        os.makedirs('logs/getLocationNameByCoords')
    else:
        logger.logMsg(
            f"Function 'logFolderCheck' 'logs' folder exists! Running LogPruner. Before pruning 'logs' folder size is: {calculateDirSize('logs')}", "NOTICE")
        pruneInit()
        logger.logMsg(f"Function 'logFolderCheck' 'logs' folder size is: {calculateDirSize('logs')}", "NOTICE")
    return


# Function to check if the userdata folder exists.
def userdataFolderCheck():
    logger.logMsg(f"Function 'userdataFolderCheck' called.", "TRACE")
    if not os.path.exists('userdata'):
        logger.logMsg(f"Function 'userdataFolderCheck' returning no userdata folder found.")
        return False
    logger.logMsg(f"Function 'userdataFolderCheck' returning userdata folder found.")
    return True


# Function to check the userdata file is actually there.
def userdataFileCheck(filePath="userdata/userData.json", expectedLength=8):
    logger.logMsg(f"Function 'userdataFileCheck' called with path {filePath}", "TRACE")
    if os.path.exists(filePath):
        with open(filePath, 'r') as file:
            lines = file.readlines()
        length = len(lines)
        if length == expectedLength:
            logger.logMsg(f"Function 'userdataFileCheck' Returning found userdata file with data", "INFO")
            return True
        else:
            logger.logMsg(
                f"Function 'userdataFileCheck' Found userdata file but it seems to have been altered outside of this program or is corrupted, creating a new one.", "WARN")
            return False
    else:
        logger.logMsg(f"Function 'userdataFileCheck' Returning userdata file does not exist", "INFO")
        return False


# Function to read in the userdata file
def readUserData():
    logger.logMsg(f"Function 'readUserData' called.", "TRACE")
    with open("userdata/userData.json", "r") as userData:
        data = json.load(userData)
        name = data.get('name')
        units = data.get('units')
        unit = data.get('unit')
        spd = data.get('speed')
        lat = data.get('latitude')
        lon = data.get('longitude')
    logger.logMsg(f"Function 'readUserData' returning {units}, {unit}, {spd}, {lat}, {lon}, {name}.", "DEBUG")
    return units, unit, spd, lat, lon, name


# Function to write the userdata file.
def writeUserData(lat, lon, units, unit, spd, geolink, apikey):
    logger.logMsg(f"Function 'writeUserData' called.", "TRACE")
    os.makedirs('userdata', exist_ok=True)
    locationName = getLocationNameByCoords(lat, lon, geolink, apikey)
    userData = {
        'name': locationName,
        'latitude': lat,
        'longitude': lon,
        'units': units,
        'unit': unit,
        'speed': spd,
    }
    with open(f"userdata/userData.json", "w") as userDataFile:
        json.dump(userData, userDataFile, indent=4)
        logger.logMsg(f"Function 'writeUserData' returning, userdata written as {userDataFile.name}")
    return


# Function to display splash screen when launching app.
def splash(message, font, auth=False):
    logger.logMsg(f"Function 'splash' called {'with' if auth == True else 'without'} author message. Calling renderText.", "TRACE")
    renderText(message, font)
    if auth:
        renderText("Written by JayTAK", "cybermedium")
    logger.logMsg(f"Function 'splash' returning.", "TRACE")
    return


# Function to run log pruning.
def pruneInit():
    try:
        logger.logMsg(f"Function 'pruneInit' called. Creating LogPruner Objects.", "TRACE")
        coordsByCodesPruner = LogPruner("logs/coordsByCodes/")
        coordsByLocationNamePruner = LogPruner("logs/coordsByLocationName/")
        coordsByLocationNameAndPZCodePruner = LogPruner("logs/coordsByLocationNameAndPZCode/")
        getLocationNameByCoordsPruner = LogPruner("logs/getLocationNameByCoords/")
        getWeatherPruner = LogPruner("logs/getWeather/")
        appActionsPruner = LogFilePruner("weatherAppActions.log")
        logger.logMsg(f"Function 'pruneInit' LogPruner Objects created, let the pruning begin!", "TRACE")
        filesRemoved = coordsByCodesPruner.pruneLogs()
        filesRemoved += coordsByLocationNamePruner.pruneLogs()
        filesRemoved += coordsByLocationNameAndPZCodePruner.pruneLogs()
        filesRemoved += getLocationNameByCoordsPruner.pruneLogs()
        filesRemoved += getWeatherPruner.pruneLogs()
        linesRemoved = appActionsPruner.pruneLogFile()
        logger.logMsg(
            f"Function 'pruneInit' Pruning Done! Removed {filesRemoved} file(s) and {linesRemoved} lines from the actions.log. Returning.", "TRACE")
    except BaseException as e:
        logger.logMsg(f"Function 'pruneInit' Caught Exception: {e}", "ERROR")
        return
    return

# Yes this function was patched in later due to scope creep and should be incorporated with the function above, this is a job for another day.. ship it.
# Function to delete all logs regardless of age.


def purgeLogs():
    try:
        print("Purging logs.")
        logger.logMsg(f"Function 'purgeLogs' called. Creating LogPruner Objects with 0 second file timeouts.", "ALERT")
        coordsByCodesPruner = LogPruner("logs/coordsByCodes/", "0")
        coordsByLocationNamePruner = LogPruner("logs/coordsByLocationName/", "0")
        coordsByLocationNameAndPZCodePruner = LogPruner("logs/coordsByLocationNameAndPZCode/", "0")
        getLocationNameByCoordsPruner = LogPruner("logs/getLocationNameByCoords/", "0")
        getWeatherPruner = LogPruner("logs/getWeather/", "0")
        appActionsPruner = LogFilePruner("weatherAppActions.log", "21", "1.0")
        logger.logMsg(f"Function 'purgeLogs' LogPruner Objects created, let the purge begin!", "TRACE")
        filesRemoved = coordsByCodesPruner.pruneLogs()
        filesRemoved += coordsByLocationNamePruner.pruneLogs()
        filesRemoved += coordsByLocationNameAndPZCodePruner.pruneLogs()
        filesRemoved += getLocationNameByCoordsPruner.pruneLogs()
        filesRemoved += getWeatherPruner.pruneLogs()
        linesRemoved = appActionsPruner.pruneLogFile()
        logger.logMsg(
            f"Function 'purgeLogs' Purging Done! Removed {filesRemoved} file(s) and {linesRemoved} lines from the actions.log. Returning.", "NOTICE")
        print(f"Purged {filesRemoved} file{'s' if filesRemoved != 1 else ''} and removed {linesRemoved} line{'s' if linesRemoved != 1 else ''} from the weatherAppActions.log")
    except BaseException as e:
        logger.logMsg(f"Function 'purgeLogs' Caught Exception: {e}", "ERROR")
        return
    return


# Function to check valid usage.
def checkUsage(geolink):
    logger.logMsg(f"Function 'checkUsage' called.")
    logger.logMsg(f"Function 'checkUsage' Platform Info(1/3): {platform.uname()}", "DEBUG")
    logger.logMsg(
        f"Function 'checkUsage' Platform Info(2/3): Platform: '{platform.platform()}' Architecture: {platform.architecture()} Python-Build: {platform.python_build()} Python-Compiler: '{platform.python_compiler()}'", "DEBUG")
    logger.logMsg(
        f"Function 'checkUsage' Platform Info(3/3): Python-Version: '{platform.python_version()}' Python-Implementation: '{platform.python_implementation()}' Python-Branch: '{platform.python_branch()}' Python-Revision: '{platform.python_revision()}'", "DEBUG")
    parser = argparse.ArgumentParser(
        description='You can run this app with no additional flags, or you could use one of the following.')
    subparsers = parser.add_subparsers(dest='mode', help='Mode of operation')
    # User mode.
    subparsers.add_parser('user', help='User mode. Allows user to input any location rather then printing the saved location.')
    # Purge logs mode.
    subparsers.add_parser(
        'purge-logs', help='Purge logs mode. This will remove any logs from the logs directory that are older then 24 hours and exits.')
    # Update Key Mode.
    subparsers.add_parser('update-key', help='Rewrites the API Key file with a new key and exits')
    # Purge all logs mode.
    parser_nuke = subparsers.add_parser(
        'app-reset', help='Reset app mode. (requires --CONFIRM-RESET). This will fully wipe any file and folder ever created by this app from your system and exits.')
    parser_nuke.add_argument('--CONFIRM-RESET', action='store_true', help='Confirmation for reset')
    args = parser.parse_args()
    if args.mode == 'user':
        logger.logMsg(f"Function 'checkUsage' Returning flag used: user")
        return "", "manual"
    elif args.mode == 'purge-logs':
        logger.logMsg(f"Function 'checkUsage' Running log purge.")
        purgeLogs()
        logger.logMsg(f"Function 'checkUsage' Purge Complete...")
        logger.logMsg(f"Function 'checkUsage' -> sys.exit(2)")
        logger.logMsg("Logs closed.", "ALERT")
        sys.exit(2)
    elif args.mode == 'update-key':
        logger.logMsg(f"Function 'checkUsage' Running API key update.")
        updateKey(geolink)
        logger.logMsg(f"Function 'checkUsage' -> sys.exit(3)")
        logger.logMsg("Logs closed.", "ALERT")
        sys.exit(3)
    elif args.mode == 'app-reset' and args.CONFIRM_RESET:
        print("Passing nuke code.")
        purgeLogs()
        return "NUKE", "NUKE"
    elif args.mode is None:
        logger.logMsg(f"Function 'checkUsage' No arguments used.")
        return "norm", "savedata"
    else:
        logger.logMsg(f"Function 'checkUsage' Displaying Help")
        parser.print_help()
        logger.logMsg(f"Function 'checkUsage' -> sys.exit(5)")
        logger.logMsg("Logs closed.", "ALERT")
        sys.exit(5)


# Function to convert degrees into cardinal directions.
def degToCardinal(deg):
    logger.logMsg(f"Function 'degToCardinal' called.", "TRACE")
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(deg/(360.0 / len(directions))) % len(directions)
    logger.logMsg(f"Function 'degToCardinal' returning {directions[index]}", "DEBUG")
    return directions[index]


# Function to convert degrees into cardinal arrow directions.
def degToArrow(deg):
    logger.logMsg(f"Function 'degToArrow' called.", "TRACE")
    directions = ["⬆", "⬈", "➡", "⬊", "⬇", "⬋", "⬅", "⬉"]
    index = round(deg/(360.0 / len(directions))) % len(directions)
    logger.logMsg(f"Function 'degToArrow' returning {directions[index]}", "DEBUG")
    return directions[index]


# Function to convert meters per second into kilometers per hour.
def mPSToKPH(mps):
    logger.logMsg(f"Function 'mPSToKPH' called.", "TRACE")
    kph = mps * 3.6
    string = f" ({kph:.2f} km/h)"
    logger.logMsg(f"Function 'mPSToKPH' returning{string}.", "DEBUG")
    return string

# Function to reset app.


def nuker():
    if os.path.exists('userdata'):
        shutil.rmtree("userdata")
        print("'userdata' folder deleted.")
    if os.path.exists('logs'):
        print("'logs' folder and all subdirectories deleted.")
        shutil.rmtree("logs")
    if os.path.isfile('weatherAppActions.log'):
        print("'weatherAppActions.log' file deleted.")
        os.remove("weatherAppActions.log")
    print("Fully Wiped. Next run will be like first download.")
    return


# Function to output size of logs.
def sizeReport():
    logger.logMsg(f"SizeReport 'logs' folder size is: {calculateDirSize('logs')}", "NOTICE")
    logger.logMsg(
        f"SizeReport 'weatherAppActions.log' file size is: {convertSize(os.path.getsize('weatherAppActions.log'))}", "NOTICE")
    return


# Function to handle API key.
def checkAPIKey(geolink):
    logger.logMsg(f"Function 'checkAPIKey' Called.")
    try:
        if userdataFolderCheck():
            if os.path.exists("userdata/APIKEY.json"):
                key = readAPIKey()
            else:
                print("API KEY MISSING!")
                logger.logMsg(f"Function 'checkAPIKey' API Key Missing!")
                key = writeAPIKey(geolink)
            if validateKey(key, geolink):
                return key
            else:
                print("Invalid API Key! Either wait for OpenWeatherMap's Servers to Update, or your input had a typo.")
        else:
            os.makedirs('userdata', exist_ok=True)
            return checkAPIKey(geolink)
    except KeyboardInterrupt:
        logger.logMsg(f"Function 'checkAPIKey' -> sys.exit(10)")
        logger.logMsg("Logs closed.", "ALERT")
        sys.exit(10)


# Function to read the API key file.
def readAPIKey():
    logger.logMsg(f"Function 'readAPIKey' called.", "TRACE")
    with open("userdata/APIKEY.json", "r") as apikeyFile:
        data = json.load(apikeyFile)
        key = data.get('APIKEY')
    logger.logMsg(f"Function 'readAPIKey' returning {key}.", "DEBUG")
    return key


# Function to write the API key file.
def writeAPIKey(geolink):
    logger.logMsg(f"Function 'writeAPIKey' called.", "TRACE")
    os.makedirs('userdata', exist_ok=True)
    key = input("API Key Setup. Please enter your API Key:\n")
    validateKey(key, geolink)
    keyData = {
        'APIKEY': key,
    }

    with open(f"userdata/APIKEY.json", "w") as apikeyFile:
        json.dump(keyData, apikeyFile, indent=4)
        logger.logMsg(f"Function 'writeAPIKey' returning, userdata written as {apikeyFile.name}")
    print(f"On next run the app will read your api key from the file {apikeyFile.name}")
    return key


# Function to validate if API key is valid.
def validateKey(key, geolink):
    logger.logMsg(f"Function 'validateKey' Called.", "TRACE")
    url = f"{geolink}reverse?lat=00.00&lon=00.00&limit=1&appid={key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.logMsg(f"Function 'validateKey' Code: {response.status_code} API Key Valid! ")
            return True
        else:
            print(
                f"API KEY INVALID, OpenWeatherMap Status Code: {response.status_code}. Read the README.md file for information on these codes.\nRun with 'update-key' to update the saved key.")
            logger.logMsg(f"Function 'validateKey' API KEY INVALID, OpenWeatherMap Status Code: {response.status_code}")
            raise WeatherServerException(response.status_code)
    except WeatherServerException as e:
        logger.logMsg(f"Function 'validateKey' Caught Exception 'WeatherServerException' {e}. Quitting.", "ERROR")
        logger.logMsg(f"Function 'validateKey' -> sys.exit(6)", "NOTICE")
        logger.logMsg("Logs closed.", "ALERT")
        sys.exit(6)
    except BaseException as e:
        logger.logMsg(f"Function 'validateKey' Caught Exception 'BaseException' {e}. Quitting.", "ERROR")
        logger.logMsg(f"Function 'validateKey' -> sys.exit(7)", "NOTICE")
        logger.logMsg("Logs closed.", "ALERT")
        sys.exit(7)


# Function to update stored API key.
def updateKey(geolink):
    try:
        logger.logMsg(f"Function 'validateKey' Called.", "TRACE")
        print("Updating Saved API Key.")
        key = writeAPIKey(geolink)
        print(f"Key updated to {key}")
        logger.logMsg(f"Function 'validateKey' Returning.", "TRACE")
    except KeyboardInterrupt:
        logger.logMsg(f"Function 'updateKey' caught KeyboardInterrupt", "NOTICE")
        logger.logMsg(f"Function 'updateKey' -> sys.exit(11)", "NOTICE")
        sys.exit(11)
    return

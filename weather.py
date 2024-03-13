# Import existing libraries
import sys
import json
import requests
# Import my custom library, JayTAK Lib.
# !!!~~~IMPORTANT~~~!!!
# Do not forget to install pyfiglet with 'pip install pyfiglet'! JayTAK Lib depends on it.
from JayTAKLib import getUnits, parseCoords, logFolderCheck, splash, codeCheck, checkUsage, parsePrintWeather, reprompt, userdataFolderCheck, readUserData, writeUserData, getLocationNameByCoords, userdataFileCheck, nuker, sizeReport, checkAPIKey
from JayTAKObjectLib import DTimeLive, UsageException, WeatherServerException, ActionLogger

# Usage message.
# USAGEMSG = "./finalProj.py\nOptional Flags: -h/--help -u/--user\nTo purge logs use: --purge-logs\nTo purge every file and folder this app has ever created, run --purge-all-logs --CONFIRM-RESET"

# Global constants:
_DEBUG = False
# Global variables:
INFO = False
_MODE = ""
# Start of the links required for the API Calls.
__GEOLINK = "http://api.openweathermap.org/geo/1.0/"
__DATALINK = "https://api.openweathermap.org/data/3.0/onecall?"

# liveTime object to provide accurate time and date data for logging functionality.
liveTime = DTimeLive()
logger = ActionLogger()

# Openweathermap API key.
APIKEY = ""


def main():
    logger.logMsg(f"Function 'main' called.", "TRACE")
    splash("Console Weather App", "larry3d", True)
    print("Thanks to OpenWeatherMap API")
    if INFO:
        print("INFO flag enabled.")
        logger.logMsg(f"Function 'main' INFO flag enabled.")
    elif _DEBUG:
        logger.logMsg(f"Function 'main' DEBUG MODE ENABLED.")
    try:
        logFolderCheck()
        if _MODE == "manual":
            mainModeManual()
        elif _MODE == "savedata":
            mainModeUserData()
        else:
            raise UsageException("Main Mode Invalid!")
        logger.logMsg(f"Function 'main' -> sys.exit(1)")
        sys.exit(1)

    except UsageException as e:
        logger.logMsg(f"Function 'main' caught UsageException: {e}", "ERROR")
        print(f"Caught UsageException:\n{e}")
    except WeatherServerException as e:
        logger.logMsg(f"Function 'main' caught WeatherServerException: {e}", "ERROR")
        print(f"Caught WeatherServerException:\n{e}")
    except SystemExit:
        logger.logMsg(f"Function 'main' caught SystemExit", "WARN")
    except NotImplementedError as e:
        logger.logMsg(f"Function 'main' caught NotImplementedError: {e}", "ERROR")
        print(f"Not Yet Implemented: {e}")
    except PendingDeprecationWarning as e:
        logger.logMsg(f"Function 'main' caught PendingDeprecationWarning: {e}", "ERROR")
        print(f"PendingDeprecationWarning: {e}")
    except ValueError as e:
        logger.logMsg(f"Function 'main' caught ValueError: {e}", "ERROR")
        print(f"ValueError: {e}")
        if _MODE == "manual":
            logger.logMsg(f"Function 'main' Recovering from ValueError. Mode: {_MODE}, calling mainModeManual()", "NOTICE")
            mainModeManual()
        elif _MODE == "savedata":
            logger.logMsg(f"Function 'main' Recovering from ValueError. Mode: {_MODE}, calling mainModeUserData()", "NOTICE")
            mainModeUserData()
        else:
            logger.logMsg(f"Function 'main' Recovering from ValueError. Mode: {_MODE}, calling Main.", "NOTICE")
            main()
    except KeyboardInterrupt:
        logger.logMsg("Interrupted by user using CTRL-C", "WARN")
    except BaseException as e:
        logger.logMsg(f"Function 'main' caught BaseException or child of (it was unexpected): {e}", "ERROR")
        print(f"Caught Unexpected BaseException/Child:\n{e}")


# Function for main manual run mode.
def mainModeManual():
    logger.logMsg(f"Function 'mainModeManual' called.")
    units, unit, spd = getUnits()
    while True:
        lat, lon = askUserLocation()
        print("-------------")
        print("\nProcessing Data. Please Wait...\n")
        response, data = getWeather(True, lat, lon, units)
        if INFO:
            print(f"INFO~ Weather Server Response: {response}")
        name = getLocationNameByCoords(lat, lon, __GEOLINK, APIKEY)
        print(f"Weather for:... {name}")
        parsePrintWeather(response, data, unit, spd, _DEBUG)
        reprompt("Would you like to enter another location?\n [y/N]")

# Function for main mode userdata.


def mainModeUserData():
    logger.logMsg(f"Function 'mainModeUserData' called.")
    if userdataFolderCheck() and userdataFileCheck():
        print("Userdata found, retrieving latest weather data for saved location.")
        units, unit, spd, lat, lon, name = readUserData()
        response, data = getWeather(True, lat, lon, units)
        print(f"Weather for:... {name}")
        parsePrintWeather(response, data, unit, spd, _DEBUG)
    else:
        print("User data file not found, creating one now...")
        units, unit, spd = getUnits()
        lat, lon = askUserLocation()
        writeUserData(lat, lon, units, unit, spd, __GEOLINK, APIKEY)
        print("Userdata saved! Next time you run the program without the manual flag it will automatically show you your saved location.")
        response, data = getWeather(True, lat, lon, units)
        name = getLocationNameByCoords(lat, lon, __GEOLINK, APIKEY)
        print(f"Weather for:... {name}")
        parsePrintWeather(response, data, unit, spd, _DEBUG)


# Function to get current weather data from openweathermap servers
# at specific latitude and longitude coordinates.
def getWeather(parse, lat="33.44", lon="-94.04", units="metric", part=""):
    logger.logMsg(f"Function 'getWeather' called with: {parse}, {lat}, {lon}, {units}, {part}")
    if part:
        url = f"{__DATALINK}lat={lat}&lon={lon}&exclude={part}&units={units}&appid={APIKEY}"
    else:
        url = f"{__DATALINK}lat={lat}&lon={lon}&units={units}&appid={APIKEY}"
    response = requests.get(url)
    logger.logMsg(f"Function 'getWeather' requested from OpenWeather DATA API, received {response}")
    if parse:
        data = response.json()
        with open(f"logs/getWeather/getWeather{liveTime.getFormattedTime(liveTime.getTime())}.json", "w") as file:
            json.dump(data, file, indent=4)
        return response, data
    logger.logMsg(
        f"Function 'getWeather' returning json data. Data can be found in json file logs/getWeather{liveTime.getFormattedTime(liveTime.getTime())}.json")
    return response


# Function to convert location names into coords.
def coordsByLocationName(cityName):
    logger.logMsg(f"Function 'coordsByLocationName' called with: {cityName}")
    url = f"{__GEOLINK}direct?q={cityName}&limit=1&appid={APIKEY}"
    response = requests.get(url)
    logger.logMsg(f"Function 'coordsByLocationName' requested from OpenWeather GEO API, received {response}")
    data = response.json()
    if INFO:
        print(f"INFO~ Coords Server Response: {response}")
    with open(f"logs/coordsByLocationName/coordsByLocationName{liveTime.getFormattedTime(liveTime.getTime())}.json", "w") as file:
        json.dump(data, file, indent=4)
        logger.logMsg(f"Function 'coordsByLocationName' logged file: {file.name}", "NOTICE")
        if INFO:
            print(f"INFO~ File Saved as :{file.name}")
        if _DEBUG:
            print(f"DEBUG~finalProj:coordsByLocationName(): Called codeCheck()")
    codeCheck(response, _DEBUG)
    logger.logMsg(
        f"Function 'coordsByLocationName' calling parseCoords with data that can be found in logs/coordsByLocationName{liveTime.getFormattedTime(liveTime.getTime())}.json")
    lat, lon = parseCoords(data)
    logger.logMsg(f"Function 'coordsByLocationName' returning {lat} {lon}")
    return lat, lon


# Function to convert location name + post/zip code into coords.
def coordsByLocationNameAndPZCode(cityName, zPostCode):
    url = f"{__GEOLINK}direct?q={cityName},{zPostCode}&limit=1&appid={APIKEY}"
    response = requests.get(url)
    logger.logMsg(f"Function 'coordsByLocationNameAndPZCode' requested from OpenWeather GEO API, received {response}")
    data = response.json()
    if INFO:
        print(f"INFO~ Coords Server Response: {response}")
    with open(f"logs/coordsByLocationNameAndPZCode/coordsByLocationNameAndPZCode{liveTime.getFormattedTime(liveTime.getTime())}.json", "w") as file:
        json.dump(data, file, indent=4)
        if INFO:
            print(f"INFO~ File Saved as :{file.name}")
    if _DEBUG:
        print(f"DEBUG~finalProj:coordsByLocationNameAndPZCode(): Called codeCheck()")
    codeCheck(response, _DEBUG)
    lat, lon = parseCoords(data)
    return lat, lon


# Function to convert location zip/post codes into coords.
def coordsByCodes(zipCode, countryCode):
    url = f"{__GEOLINK}zip?zip={zipCode},{countryCode}&appid={APIKEY}"
    response = requests.get(url)
    logger.logMsg(f"Function 'coordsByCodes' requested from OpenWeather GEO API, received {response}")
    data = response.json()
    if INFO:
        print(f"INFO~ Coords Server Response: {response}")
    with open(f"logs/coordsByCodes/coordsByCodes{liveTime.getFormattedTime(liveTime.getTime())}.json", "w") as file:
        json.dump(data, file, indent=4)
        if INFO:
            print(f"INFO~ File Saved as :{file.name}")
    if _DEBUG:
        print(f"DEBUG~finalProj:coordsByCodes(): Called codeCheck()")
    codeCheck(response, _DEBUG)
    lat, lon = parseCoords(data)
    return lat, lon


# Function to ask user how they would like to provide location information, and then return the users desired
# location in latitude and longitude coordinates.
def askUserLocation():
    logger.logMsg(f"Function 'askUserLocation' called.", "TRACE")
    try:
        print("How do you want to provide the location information for the weather?\n(1) City name.\n(2) City name and post/zip code.")
        print("(3) Zip/Post and country code only.\n(4) Latitude and Longitude coordinates.")
        userInput = input("[1/2/3/4]: ")
        print("-------------")
        match(userInput):
            case '1':  # City name only.
                logger.logMsg(f"Function 'askUserLocation' User chose location method 1, city name only.", "DEBUG")
                print("City name only selected. Input the city name only.")
                userCity = input("City Name: ")
                lat, lon = coordsByLocationName(userCity)

            case '2':  # City name and zip/post code.
                logger.logMsg(f"Function 'askUserLocation' User chose location method 2, city name and zip/post code.", "DEBUG")
                print("City name and zip/post code selected.\nPlease input your location information separated by spaces in the following order. City name, zip/post code.")
                cityName, postCode = input("").rsplit(" ", maxsplit=1)
                lat, lon = coordsByLocationNameAndPZCode(cityName, postCode)

            case '3':  # Zip/post code and country code only.
                logger.logMsg(f"Function 'askUserLocation' User chose location method 3, zip/post code and country code.", "DEBUG")
                print("Zip/post code and country code selected.\nPlease input your location information separated by spaces in the following order. Zip/post code, country code.")
                postCode, countryCode = input("").split()
                lat, lon = coordsByCodes(postCode, countryCode)

            case '4':  # Coords.
                logger.logMsg(f"Function 'askUserLocation' User chose location method 4, manual coordinates.", "DEBUG")
                print(
                    "Manual coordinates selected.\nPlease input your Latitude and Longitude coordinates separated by a single space. [lat lon]")
                lat, lon = input("ie: [33.44 -94.04]: ").split()

            case _:
                logger.logMsg(f"Function 'askUserLocation' User input {userInput}, this was not a valid option..", "ERROR")
                raise ValueError(f"Invalid Input. {userInput}")
    except ValueError as e:
        logger.logMsg(f"Function 'askUserLocation' caught ValueError: {e}", "ERROR")
        print(f"ValueError: {e}")
        logger.logMsg(f"Function 'askUserLocation' Recovering from ValueError.", "NOTICE")
        return askUserLocation()

    if INFO:
        print(f"INFO~ Retrieved Lat: {lat} Lon: {lon} using method {userInput}")
    logger.logMsg(f"Function 'askUserLocation' returning {lat} {lon}.", "DEBUG")
    return lat, lon


if __name__ == "__main__":
    logger.logMsg("Logs opening.", "ALERT")
    info, usage = checkUsage(__GEOLINK)
    if info == "NUKE" and usage == "NUKE":
        nuker()
        sys.exit(4)
    _MODE = usage
    APIKEY = checkAPIKey(__GEOLINK)
    main()
    logger.logMsg("Main has quit.", "WARN")
    sizeReport()
    logger.logMsg("Logs closed.", "ALERT")
else:
    logger.logMsg(f"WeatherApp is being imported...", "NOTICE")

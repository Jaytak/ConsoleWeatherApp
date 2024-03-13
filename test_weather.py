import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
#from JayTAKLib import getUnits, convertSize, degToCardinal, degToArrow, mPSToKPH, getLocationNameByCoords, parseCoords
import JayTAKObjectLib
import JayTAKLib
import weather

APIKEY = "" # OpenWeatherMap API Key

# Unit test for getUnits()
class TestGetUnits(unittest.TestCase):

    @patch('builtins.input', side_effect=['m'])
    def test_getUnits_m(self, mock_input):
        units, unit, spd = JayTAKLib.getUnits()
        self.assertEqual(units, 'metric')
        self.assertEqual(unit, '°C')
        self.assertEqual(spd, 'm/s')

    @patch('builtins.input', side_effect=['M'])
    def test_getUnits_M(self, mock_input):
        units, unit, spd = JayTAKLib.getUnits()
        self.assertEqual(units, 'metric')
        self.assertEqual(unit, '°C')
        self.assertEqual(spd, 'm/s')

    @patch('builtins.input', side_effect=['metric'])
    def test_getUnits_metric(self, mock_input):
        units, unit, spd = JayTAKLib.getUnits()
        self.assertEqual(units, 'metric')
        self.assertEqual(unit, '°C')
        self.assertEqual(spd, 'm/s')

    @patch('builtins.input', side_effect=['i'])
    def test_getUnits_i(self, mock_input):
        units, unit, spd = JayTAKLib.getUnits()
        self.assertEqual(units, 'imperial')
        self.assertEqual(unit, '°F')
        self.assertEqual(spd, 'mph')

    @patch('builtins.input', side_effect=['I'])
    def test_getUnits_I(self, mock_input):
        units, unit, spd = JayTAKLib.getUnits()
        self.assertEqual(units, 'imperial')
        self.assertEqual(unit, '°F')
        self.assertEqual(spd, 'mph')

    @patch('builtins.input', side_effect=['imperial'])
    def test_getUnits_imperial(self, mock_input):
        units, unit, spd = JayTAKLib.getUnits()
        self.assertEqual(units, 'imperial')
        self.assertEqual(unit, '°F')
        self.assertEqual(spd, 'mph')

    @patch('builtins.input', side_effect=['mars', 'metric'])
    def test_getUnits_invalid_then_valid_metric(self, mock_input):
        units, unit, spd = JayTAKLib.getUnits()
        self.assertEqual(units, 'metric')
        self.assertEqual(unit, '°C')
        self.assertEqual(spd, 'm/s')
        self.assertEqual(mock_input.call_count, 2)

# Unit test for convertSize()
class TestConvertSize(unittest.TestCase):
    # Check conversion to all units.
    def test_convertSize(self):
        size = JayTAKLib.convertSize(100)
        self.assertEqual(size, '100.0 B')
        size = JayTAKLib.convertSize(1000000)
        self.assertEqual(size, '976.56 KB')
        size = JayTAKLib.convertSize(1048576)
        self.assertEqual(size, '1.0 MB')
        size = JayTAKLib.convertSize(1073741824)
        self.assertEqual(size, '1.0 GB')
        size = JayTAKLib.convertSize(1099511627776)
        self.assertEqual(size, '1.0 TB')
        size = JayTAKLib.convertSize(1125899906842624)
        self.assertEqual(size, '1.0 PB')
        size = JayTAKLib.convertSize(1152921504606846976)
        self.assertEqual(size, '1.0 EB')
        size = JayTAKLib.convertSize(1180591620717411303424)
        self.assertEqual(size, '1.0 ZB')
        size = JayTAKLib.convertSize(1209925819614629174704176)
        self.assertEqual(size, '1.0 YB')


# Unit Test for degToCardinal()
class TestDegreesToCardinal(unittest.TestCase):
    # Multiple test cases for degrees to cardinal
    def test_degToCardinal(self):
        direction = JayTAKLib.degToCardinal(0)
        self.assertEqual(direction, 'N')
        direction = JayTAKLib.degToCardinal(23)
        self.assertEqual(direction, 'NNE')
        direction = JayTAKLib.degToCardinal(40)
        self.assertEqual(direction, 'NE')
        direction = JayTAKLib.degToCardinal(70)
        self.assertEqual(direction, 'ENE')
        direction = JayTAKLib.degToCardinal(90)
        self.assertEqual(direction, 'E')
        direction = JayTAKLib.degToCardinal(111)
        self.assertEqual(direction, 'ESE')
        direction = JayTAKLib.degToCardinal(135)
        self.assertEqual(direction, 'SE')
        direction = JayTAKLib.degToCardinal(167)
        self.assertEqual(direction, 'SSE')
        direction = JayTAKLib.degToCardinal(180)
        self.assertEqual(direction, 'S')
        direction = JayTAKLib.degToCardinal(205)
        self.assertEqual(direction, 'SSW')
        direction = JayTAKLib.degToCardinal(225)
        self.assertEqual(direction, 'SW')
        direction = JayTAKLib.degToCardinal(250)
        self.assertEqual(direction, 'WSW')
        direction = JayTAKLib.degToCardinal(270)
        self.assertEqual(direction, 'W')
        direction = JayTAKLib.degToCardinal(293)
        self.assertEqual(direction, 'WNW')
        direction = JayTAKLib.degToCardinal(320)
        self.assertEqual(direction, 'NW')
        direction = JayTAKLib.degToCardinal(340)
        self.assertEqual(direction, 'NNW')


# Unit Test for degToArrow()
class TestDegreesToArrow(unittest.TestCase):
    # Multiple test cases for degrees to arrow
    def test_degToArrow(self):
        direction = JayTAKLib.degToArrow(0)
        self.assertEqual(direction, '⬆')
        direction = JayTAKLib.degToArrow(45)
        self.assertEqual(direction, '⬈')
        direction = JayTAKLib.degToArrow(90)
        self.assertEqual(direction, '➡')
        direction = JayTAKLib.degToArrow(145)
        self.assertEqual(direction, '⬊')
        direction = JayTAKLib.degToArrow(180)
        self.assertEqual(direction, '⬇')
        direction = JayTAKLib.degToArrow(225)
        self.assertEqual(direction, '⬋')
        direction = JayTAKLib.degToArrow(270)
        self.assertEqual(direction, '⬅')
        direction = JayTAKLib.degToArrow(315)
        self.assertEqual(direction, '⬉')

# Unit Test for mPSToKPH()
class TestMetersPerSecondToKilometersPerHour(unittest.TestCase):
    # Multiple test cases for mpstokph
    def test_mPSToKPH(self):
        output = JayTAKLib.mPSToKPH(1)
        self.assertEqual(output, ' (3.60 km/h)')
        output = JayTAKLib.mPSToKPH(1.5)
        self.assertEqual(output, ' (5.40 km/h)')
        output = JayTAKLib.mPSToKPH(5.9)
        self.assertEqual(output, ' (21.24 km/h)')
        output = JayTAKLib.mPSToKPH(10)
        self.assertEqual(output, ' (36.00 km/h)')
        output = JayTAKLib.mPSToKPH(100)
        self.assertEqual(output, ' (360.00 km/h)')
        output = JayTAKLib.mPSToKPH(100.12)
        self.assertEqual(output, ' (360.43 km/h)')


# Unit test for GetLocationByCoords
class TestGetLocationByCoords(unittest.TestCase):
    # Test getLocationNameByCoords with multiple coords.
    def test_getLocationNameByCoords(self):
        key = weather.APIKEY
        JayTAKLib.readAPIKey()
        locationName = JayTAKLib.getLocationNameByCoords(-36.88780519215509, 174.82131569784545, "http://api.openweathermap.org/geo/1.0/", APIKEY)
        self.assertEqual(locationName, 'Ōrākei')
        locationName = JayTAKLib.getLocationNameByCoords(-31.951993057609286, 115.8709134097519, "http://api.openweathermap.org/geo/1.0/", APIKEY)
        self.assertEqual(locationName, 'Perth')
        locationName = JayTAKLib.getLocationNameByCoords(34.05515701380864, -118.24346639070872, "http://api.openweathermap.org/geo/1.0/", APIKEY)
        self.assertEqual(locationName, 'Los Angeles')
        locationName = JayTAKLib.getLocationNameByCoords(-30.631174984224685, 25.457366112056583, "http://api.openweathermap.org/geo/1.0/", APIKEY)
        self.assertEqual(locationName, 'Umsobomvu Local Municipality')



# Unit Test for ParseCoords()
class TestParseCoords(unittest.TestCase):

    # Test parseCoords with valid list.
    def test_parseCoords_valid_list(self):
        data = [{"lat": 12.34, "lon": 56.78}]
        lat, lon = JayTAKLib.parseCoords(data)
        self.assertEqual(lat, 12.34)
        self.assertEqual(lon, 56.78)

    # Test parseCoords with invalid list.
    def test_parseCoords_invalid_list(self):
        with self.assertRaises(ValueError):
            JayTAKLib.parseCoords([])

    # Test parseCoords with valid dict.
    def test_parseCoords_list(self):
        data = {"lat": 91.45, "lon": 46.75}
        lat, lon = JayTAKLib.parseCoords(data)
        self.assertEqual(lat, 91.45)
        self.assertEqual(lon, 46.75)

    # Test parseCoords with invalid dict.
    def test_parseCoords_invalid_dict(self):
        with self.assertRaises(ValueError):
            JayTAKLib.parseCoords({"invalid key": "value"})

    # Test parseCoords with invalid data type.
    def test_parseCoords_invalid_data_type(self):
        with self.assertRaises(ValueError):
            JayTAKLib.parseCoords("invalid-data")


# Unit test for MainModeManual()
class TestMainModeManual(unittest.TestCase):

    @patch('builtins.input', side_effect=['m', '1', 'auckland', 'n'])
    def test_mainModeManual_valid(self, mock_input):
        with self.assertRaises(SystemExit) as e:
            weather.mainModeManual()
        self.assertEqual(e.exception.code, 1)
        self.assertEqual(mock_input.call_count, 4)

# Unit test for GetWeather()
class TestGetWeather(unittest.TestCase):

    def test_getWeather_valid(self):
        response = weather.getWeather(False)
        self.assertEqual(response.status_code, 200)

# Unit test for CoordsByLocationName()
class TestCoordsByLocationName(unittest.TestCase):

    def test_coordsByLocationName_denver(self):
        lat, lon = weather.coordsByLocationName("Denver")
        self.assertEqual(lat, 39.7392364)
        self.assertEqual(lon, -104.984862)

    def test_coordsByLocationName_seattle(self):
        lat, lon = weather.coordsByLocationName("Seattle")
        self.assertEqual(lat, 47.6038321)
        self.assertEqual(lon, -122.330062)

# Unit test for custom date and time object.
class TestDTimeLive(unittest.TestCase):
    def setUp(self):
        liveTime = JayTAKObjectLib.DTimeLive()
        self.liveTime = liveTime

    def assertDateTimeAlmostEqual(self, dt1, dt2, delta=timedelta(seconds=2)):
        difference = abs(dt1 - dt2)
        self.assertLessEqual(difference, delta, f"Difference exceeds delta of {delta}")

    def test_getTime(self):
        currentTime = self.liveTime.getTime()
        self.assertDateTimeAlmostEqual(currentTime, datetime.now())

    def test_getFormattedTime(self):
        dt = datetime(2024, 1, 1, 12, 30, 45)
        formattedTime = self.liveTime.getFormattedTime(dt)
        self.assertEqual(formattedTime, "[12.30.45][01-01-2024]")

    def test_getSunFormattedTime(self):
        timestamp = 1706367364
        offset = 3600
        expected = datetime.utcfromtimestamp(timestamp + offset)
        sunFormatted = self.liveTime.getSunFormattedTime(timestamp, offset)
        expFormatted = expected.strftime("%H:%M:%S")
        self.assertEqual(sunFormatted, expFormatted)

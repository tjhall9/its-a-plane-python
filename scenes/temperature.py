import urllib.request
import json
from rgbmatrix import graphics
from utilities.animator import Animator
from setup import colours, fonts, frames
from config import TEMPERATURE_LOCATION
from config import DEBUG_TEMP

# Attempt to load config data
try:
    from config import OPENWEATHER_API_KEY

except (ModuleNotFoundError, NameError, ImportError):
    # If there's no config data
    OPENWEATHER_API_KEY = None

try:
    from config import TEMPERATURE_UNITS

except (ModuleNotFoundError, NameError, ImportError):
    # If there's no config data
    TEMPERATURE_UNITS = "metric"

if TEMPERATURE_UNITS != "metric" and TEMPERATURE_UNITS != "imperial":
    TEMPERATURE_UNITS = "metric"

# Weather API
WEATHER_API_URL = "https://taps-aff.co.uk/api/"
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/"


def grab_temperature(location, units='metric'):
    current_temp = None

    try:
        request = urllib.request.Request(WEATHER_API_URL + location)
        raw_data = urllib.request.urlopen(request).read()
        content = json.loads(raw_data.decode("utf-8"))
        current_temp = content["temp_c"]

    except:
        pass

    if units == "imperial":
        current_temp = (current_temp * (9.0 / 5.0)) + 32

    return current_temp


def grab_temperature_openweather(location, apikey, units):
    current_temp = None

    try:
        request = urllib.request.Request(
            OPENWEATHER_API_URL
            + "weather?q="
            + location
            + "&appid="
            + apikey
            + "&units="
            + units
        )
        raw_data = urllib.request.urlopen(request).read()
        content = json.loads(raw_data.decode("utf-8"))
        current_temp = content["main"]["temp"]

    except:
        pass

    return current_temp


# Scene Setup
TEMPERATURE_REFRESH_SECONDS = 60
TEMPERATURE_FONT = fonts.regular
TEMPERATURE_FONT_HEIGHT = 10
TEMPERATURE_POSITION = (38, TEMPERATURE_FONT_HEIGHT + 1)
TEMPERATURE_MIN_COLOUR = colours.BLUE
TEMPERATURE_MID_COLOUR = colours.GREEN
TEMPERATURE_MAX_COLOUR = colours.ORANGE

if TEMPERATURE_UNITS == "metric":
    TEMPERATURE_MIN = 0
    TEMPERATURE_MAX = 25
elif TEMPERATURE_UNITS == "imperial":
    TEMPERATURE_MIN = 60
    TEMPERATURE_MID = 75
    TEMPERATURE_MAX = 90


class TemperatureScene(object):
    def __init__(self):
        super().__init__()
        self._last_temperature = None
        self._last_temperature_str = None

    def colour_gradient(self, colour_A, colour_B, ratio):
        return graphics.Color(
            colour_A.red + ((colour_B.red - colour_A.red) * ratio),
            colour_A.green + ((colour_B.green - colour_A.green) * ratio),
            colour_A.blue + ((colour_B.blue - colour_A.blue) * ratio),
        )

    @Animator.KeyFrame.add(frames.PER_SECOND * 1)
    def temperature(self, count):

        if len(self._data):
            # Ensure redraw when there's new data
            return

        if not (count % TEMPERATURE_REFRESH_SECONDS):

            if OPENWEATHER_API_KEY:
                self.current_temperature = grab_temperature_openweather(
                    TEMPERATURE_LOCATION, OPENWEATHER_API_KEY, TEMPERATURE_UNITS
                )
            else:
                self.current_temperature = grab_temperature(TEMPERATURE_LOCATION, TEMPERATURE_UNITS)

        if self._last_temperature_str is not None:
            # Undraw old temperature
            _ = graphics.DrawText(
                self.canvas,
                TEMPERATURE_FONT,
                TEMPERATURE_POSITION[0],
                TEMPERATURE_POSITION[1],
                colours.BLACK,
                self._last_temperature_str,
            )

        if self.current_temperature:
            temp_str = f"{round(self.current_temperature)}°".rjust(4, " ")
            self.current_temperature = DEBUG_TEMP

            if self.current_temperature > TEMPERATURE_MID:
                if self.current_temperature > TEMPERATURE_MAX:
                    ratio = 1
                elif self.current_temperature > TEMPERATURE_MID:
                    ratio = (self.current_temperature - TEMPERATURE_MID) / TEMPERATURE_MAX

                temp_colour = self.colour_gradient(
                    #TEMPERATURE_MID_COLOUR, TEMPERATURE_MAX_COLOUR, ratio
                    TEMPERATURE_MAX_COLOUR, TEMPERATURE_MID_COLOUR, ratio)
                print("temp > mid, ratio=" + str(ratio))

            else:
                if self.current_temperature > TEMPERATURE_MIN:
                    ratio = (self.current_temperature - TEMPERATURE_MIN) / TEMPERATURE_MID
                else:
                    ratio = 0

                temp_colour = self.colour_gradient(
                    TEMPERATURE_MIN_COLOUR, TEMPERATURE_MID_COLOUR, ratio)
                print("temp < mid, ratio=" + str(ratio))
            # Draw temperature
            _ = graphics.DrawText(
                self.canvas,
                TEMPERATURE_FONT,
                TEMPERATURE_POSITION[0],
                TEMPERATURE_POSITION[1],
                temp_colour,
                temp_str,
            )

            self._last_temperature = self.current_temperature
            self._last_temperature_str = temp_str

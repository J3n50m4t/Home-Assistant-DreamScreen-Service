"""
Adds a service to Home Assistant to control DreamScreen wifi models.

Based on ideas from
https://github.com/avwuff/DreamScreenControl
and
https://github.com/genesisfactor/DreamScreenCommander
"""
import socket
import logging
import asyncio

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_IP_ADDRESS, CONF_MODE, CONF_BRIGHTNESS)

REQUIREMENTS = ["crc8==0.0.4"]

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'dreamscreen'

DREAMSCREEN_CONTROLLER = 'dreamscreen controller'

SERVICE_MODE = 'set_mode'
SERVICE_MODE_SCHEMA = vol.Schema({
    vol.Required(CONF_MODE): vol.All(int, vol.Range(min=0, max=3)),
})

SERVICE_HDMI_SOURCE = 'set_hdmi_source'
CONF_HDMI_SOURCE = 'source'
SERVICE_HDMI_SOURCE_SCHEMA = vol.Schema({
    vol.Required(CONF_HDMI_SOURCE): vol.All(int, vol.Range(min=0, max=2)),
})

SERVICE_BRIGHTNESS = 'set_brightness'
SERVICE_BRIGHTNESS_SCHEMA = vol.Schema({
    vol.Required(CONF_BRIGHTNESS): vol.All(int, vol.Range(min=0, max=100)),
})

SERVICE_AMBIANCE_MODE = 'set_ambiance_mode'
SERVICE_AMBIANCE_MODE_SCHEMA = vol.Schema({
    vol.Required(CONF_MODE): vol.All(int, vol.Range(min=0, max=1)),
})

SERVICE_AMBIANCE_SCENE = 'set_ambiance_scene'
CONF_AMBIANCE_SCENE = 'scene'
SERVICE_AMBIANCE_SCENE_SCHEMA = vol.Schema({
    vol.Required(CONF_AMBIANCE_SCENE): vol.All(int, vol.Range(min=0, max=8)),
})


SERVICE_AMBIANCE_COLOR = 'set_ambiance_color'
CONF_AMBIANCE_COLOR_RED = 'red'
CONF_AMBIANCE_COLOR_GREEN = 'green'
CONF_AMBIANCE_COLOR_BLUE = 'blue'
SERVICE_AMBIANCE_COLOR_SCHEMA = vol.Schema({
    vol.Required(vol.Any(CONF_AMBIANCE_COLOR_RED,
                         CONF_AMBIANCE_COLOR_GREEN,
                         CONF_AMBIANCE_COLOR_BLUE),
                 msg="Need at least 1 color specified."):
    vol.All(int, vol.Range(min=0, max=255))
})

CONF_GROUP = 'group'
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Optional(CONF_GROUP, default=0): int,
    })
}, extra=vol.ALLOW_EXTRA)


class DreamScreen:
    """Control mechanism for the DreamScreen Wifi."""

    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, ip: str, group=0, port=8888) -> None:
        """Init method to gather IP, group, and port."""
        self._ip = ip
        self._port = port
        self._group = group
        _LOGGER.debug("DreamScreen initialized")

    @staticmethod
    def _crc8(data: list) -> int:
        import crc8
        hash = crc8.crc8()
        hash.update(data)
        return hash.digest()

    def _build_packet(self, option: int, value: list) -> bytearray:
        if type(value) not in [list, int]:
            raise TypeError("value type {} not list or int"
                            .format(type(value)))
        if type(value) == int:
            value = [value]
        resp = [252, len(value) + 5, self._group, 17, 3, option]
        resp.extend(value)
        return bytearray(resp) + self._crc8(bytearray(resp))

    def _send_packet(self, packet: bytearray) -> None:
        if type(packet) != bytearray:
            raise TypeError("packet type {} != bytearray"
                            .format(type(packet)))
        self._socket.sendto(packet, (self._ip, self._port))

    def set_mode(self, mode: int) -> None:
        """Set DreamScreen mode.

        0: Off
        1: Video
        2: Music
        3: Ambient
        """
        mode = max(min(mode, 3), 0)
        packet = self._build_packet(1, mode)
        self._send_packet(packet)
        _LOGGER.debug("set mode {}".format(mode))

    def set_hdmi_source(self, hdmi_source: int) -> None:
        """Set DreamScreen HDMI source.

        0: HDMI Source 1
        1: HDMI Source 2
        2: HDMI Source 3
        """
        hdmi_source = max(min(hdmi_source, 2), 0)
        packet = self._build_packet(32, hdmi_source)
        self._send_packet(packet)
        _LOGGER.debug("set hdmi_source {}".format(hdmi_source))

    def set_brightness(self, brightness: int) -> None:
        """Set DreamScreen brightness.

        Brightness values between 0 and 100
        """
        brightness = max(min(brightness, 100), 0)
        packet = self._build_packet(2, brightness)
        self._send_packet(packet)
        _LOGGER.debug("set brightness {}".format(brightness))

    def set_ambiance_mode(self, mode: int) -> None:
        """Set DreamScreen ambiance mode.

        Not sure on clamping/all values
        0: RGB Color
        1: Scenes (Required for setting scene below)
        """
        mode = max(min(mode, 1), 0)
        packet = self._build_packet(8, mode)
        self._send_packet(packet)
        _LOGGER.debug("set ambiance mode {}".format(mode))

    def set_ambiance_scene(self, scene: int) -> None:
        """Set DreamScreen ambient scene.

        Scenes from the app:
        0: Random Colors
        1: Fireside
        2: Twinkle
        3: Ocean
        4: Pride
        5: July 4th
        6: Holiday
        7: Pop
        8: Enchanted Forrest
        """
        scene = max(min(scene, 8), 0)
        packet = self._build_packet(13, scene)
        self._send_packet(packet)
        _LOGGER.debug("set scene {}".format(scene))

    def set_ambiance_color(self,
                           red: int=0,
                           green: int=0,
                           blue: int=0) -> None:
        """Set DreamScreen ambient color."""
        red = max(min(red, 255), 0)
        green = max(min(green, 255), 0)
        blue = max(min(blue, 255), 0)
        packet = self._build_packet(5, [red, green, blue])
        self._send_packet(packet)
        _LOGGER.debug("set ambiance_color R{} G{} B{}".
                      format(red, green, blue))


@asyncio.coroutine
def async_setup(hass, config):
    """Setup DreamScreen."""
    config = config.get(DOMAIN, {})

    ds = DreamScreen(ip=config[CONF_IP_ADDRESS], group=config[CONF_GROUP])

    hass.data[DOMAIN] = {
        DREAMSCREEN_CONTROLLER: ds
    }

    @asyncio.coroutine
    def set_mode(call):
        """Change DreamScreen Mode."""
        mode = call.data.get(CONF_MODE)
        hass.data[DOMAIN][DREAMSCREEN_CONTROLLER].set_mode(mode)

    # Mode Service
    hass.services.async_register(
        DOMAIN,
        SERVICE_MODE,
        set_mode,
        schema=SERVICE_MODE_SCHEMA)

    @asyncio.coroutine
    def set_hdmi_source(call):
        """Change DreamScreen HDMI Source."""
        source = call.data.get(CONF_HDMI_SOURCE)
        hass.data[DOMAIN][DREAMSCREEN_CONTROLLER].set_hdmi_source(source)

    # HDMI Source Service
    hass.services.async_register(
        DOMAIN,
        SERVICE_HDMI_SOURCE,
        set_hdmi_source,
        schema=SERVICE_HDMI_SOURCE_SCHEMA)

    @asyncio.coroutine
    def set_brightness(call):
        """Change DreamScreen Brightness."""
        brightness = call.data.get(CONF_BRIGHTNESS)
        hass.data[DOMAIN][DREAMSCREEN_CONTROLLER].set_brightness(brightness)

    # Brightness Service
    hass.services.async_register(
        DOMAIN,
        SERVICE_BRIGHTNESS,
        set_brightness,
        schema=SERVICE_BRIGHTNESS_SCHEMA)

    @asyncio.coroutine
    def set_ambiance_mode(call):
        """Change DreamScreen Ambiance Mode."""
        mode = call.data.get(CONF_MODE)
        hass.data[DOMAIN][DREAMSCREEN_CONTROLLER].set_ambiance_mode(mode)

    # Ambiance Mode Service
    hass.services.async_register(
        DOMAIN,
        SERVICE_AMBIANCE_MODE,
        set_ambiance_mode,
        schema=SERVICE_AMBIANCE_MODE_SCHEMA)

    @asyncio.coroutine
    def set_ambiance_scene(call):
        """Change DreamScreen Ambiance Scene."""
        scene = call.data.get(CONF_AMBIANCE_SCENE)
        hass.data[DOMAIN][DREAMSCREEN_CONTROLLER].set_ambiance_scene(scene)

    # Ambiance Scene Service
    hass.services.async_register(
        DOMAIN,
        SERVICE_AMBIANCE_SCENE,
        set_ambiance_scene,
        schema=SERVICE_AMBIANCE_SCENE_SCHEMA)

    @asyncio.coroutine
    def set_ambiance_color(call):
        """Change DreamScreen Ambiance Color."""
        red = call.data.get(CONF_AMBIANCE_COLOR_RED) or 0
        green = call.data.get(CONF_AMBIANCE_COLOR_GREEN) or 0
        blue = call.data.get(CONF_AMBIANCE_COLOR_BLUE) or 0
        hass.data[DOMAIN][DREAMSCREEN_CONTROLLER]. \
            set_ambiance_color(red=red, green=green, blue=blue)

    # Ambiance Color Service
    hass.services.async_register(
        DOMAIN,
        SERVICE_AMBIANCE_COLOR,
        set_ambiance_color,
        schema=SERVICE_AMBIANCE_COLOR_SCHEMA)

    return True

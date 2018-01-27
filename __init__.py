"""
Adds a service to Home Assistant to control DreamScreen wifi models.

Based on ideas from
https://github.com/avwuff/DreamScreenControl
and
https://github.com/genesisfactor/DreamScreenCommander
"""
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


@asyncio.coroutine
def async_setup(hass, config):
    """Setup DreamScreen."""
    config = config.get(DOMAIN, {})

    from .dreamscreen import DreamScreen
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

"""Adds a service to Home Assistant to control DreamScreen wifi models."""
import asyncio
import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import ATTR_ENTITY_ID, CONF_MODE, CONF_BRIGHTNESS
from homeassistant.helpers.entity import Entity, generate_entity_id
from homeassistant.helpers.entity_component import EntityComponent

_LOGGER = logging.getLogger(__name__)

DOMAIN = "dreamscreen"

DEVICES_CONF = "devices"
DEVICE_ADDR = "address"
TIMEOUT_CONF = "timeout"
TIMEOUT_DEFAULT = 1
ENTITY_ID_FORMAT = DOMAIN + ".{}"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(TIMEOUT_CONF, default=TIMEOUT_DEFAULT): cv.positive_int,
                vol.Optional(DEVICES_CONF, []): [
                    vol.Schema(
                        {
                            cv.slug: vol.Schema(
                                {
                                    vol.Required(DEVICE_ADDR): str,
                                    vol.Optional(
                                        TIMEOUT_CONF, default=TIMEOUT_DEFAULT
                                    ): cv.positive_int,
                                }
                            )
                        }
                    )
                ],
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_MODE = "set_mode"
SERVICE_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_MODE): vol.All(vol.Coerce(int), vol.Range(min=0, max=3)),
    }
)

SERVICE_HDMI_SOURCE = "set_hdmi_source"
CONF_HDMI_SOURCE = "source"
SERVICE_HDMI_SOURCE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_HDMI_SOURCE): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=2)
        ),
    }
)

SERVICE_BRIGHTNESS = "set_brightness"
SERVICE_BRIGHTNESS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_BRIGHTNESS): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=100)
        ),
    }
)

SERVICE_AMBIENT_SCENE = "set_ambient_scene"
CONF_AMBIENT_SCENE = "scene"
SERVICE_AMBIENT_SCENE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_AMBIENT_SCENE): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=8)
        ),
    }
)

SERVICE_HDR_TONE_REMAPPING = "set_hdr_tone_remapping"
CONF_HDR_TONE_REMAPPING = "hdr_tone_remapping"
SERVICE_HDR_TONE_REMAPPING_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_HDR_TONE_REMAPPING): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=1)
        ),
    }
)

SERVICE_AMBIENT_COLOR = "set_ambient_color"
CONF_AMBIENT_COLOR = "color"
SERVICE_AMBIENT_COLOR_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_AMBIENT_COLOR): vol.Match(r"^#(?:[0-9a-fA-F]{3}){1,2}$"),
    }
)

SERVICE_RESTART = "restart_device"
SERVICE_RESTART_SCHEMA = vol.Schema({vol.Required(ATTR_ENTITY_ID): cv.entity_ids})

SERVICE_TO_ATTRIBUTE = {
    SERVICE_MODE: {
        "attribute": "mode",
        "schema": SERVICE_MODE_SCHEMA,
        "param": CONF_MODE,
    },
    SERVICE_HDMI_SOURCE: {
        "attribute": "hdmi_input",
        "schema": SERVICE_HDMI_SOURCE_SCHEMA,
        "param": CONF_HDMI_SOURCE,
    },
    SERVICE_BRIGHTNESS: {
        "attribute": "brightness",
        "schema": SERVICE_BRIGHTNESS_SCHEMA,
        "param": CONF_BRIGHTNESS,
    },
    SERVICE_AMBIENT_SCENE: {
        "attribute": "ambient_scene",
        "schema": SERVICE_AMBIENT_SCENE_SCHEMA,
        "param": CONF_AMBIENT_SCENE,
    },
    SERVICE_AMBIENT_COLOR: {
        "attribute": "ambient_color",
        "schema": SERVICE_AMBIENT_COLOR_SCHEMA,
        "param": CONF_AMBIENT_COLOR,
    },
    SERVICE_HDR_TONE_REMAPPING: {
        "attribute": "hdr_tone_remapping",
        "schema": SERVICE_HDR_TONE_REMAPPING_SCHEMA,
        "param": CONF_HDR_TONE_REMAPPING,
    },
    SERVICE_RESTART: {"attribute": "restart", "schema": SERVICE_RESTART_SCHEMA},
}


async def async_setup(hass, config):
    """Setup DreamScreen."""
    import pydreamscreen

    config = config.get(DOMAIN, {})

    component = EntityComponent(_LOGGER, DOMAIN, hass)

    async def async_handle_dreamscreen_services(service):
        """Reusable DreamScreen service caller."""
        service_definition = SERVICE_TO_ATTRIBUTE.get(service.service)

        attribute = service_definition["attribute"]
        attribute_value = service.data.get(service_definition.get("param", ""))

        target_entities = await component.async_extract_from_service(service)

        updates = []
        for entity in target_entities:
            if attribute_value:
                _LOGGER.debug(
                    "setting {} {} to {}".format(
                        entity.entity_id, attribute, attribute_value
                    )
                )
            else:
                _LOGGER.debug("calling {} {} ".format(entity.entity_id, attribute))

            setattr(entity.device, attribute, attribute_value)
            updates.append(entity.async_update_ha_state(True))

        if updates:
            """ Removed loop=hass.loop as asyncio.wait() no long accept loop since python 3.10"""
            await asyncio.wait(updates)

    for service_name in SERVICE_TO_ATTRIBUTE:
        schema = SERVICE_TO_ATTRIBUTE[service_name].get("schema")
        hass.services.async_register(
            DOMAIN, service_name, async_handle_dreamscreen_services, schema=schema
        )

    entities = []
    entity_ids = []
    timeout = config[TIMEOUT_CONF]
    configured = config[DEVICES_CONF]
    _LOGGER.debug("Discovery Timeout: %d" % timeout)
    _LOGGER.debug("Configured devices: %d" % len(configured))
    if len(configured) > 0:
        for deviceConf in configured:
            deviceName = list(deviceConf.keys())[0]
            deviceInfo = deviceConf[deviceName]
            address = deviceInfo[DEVICE_ADDR]
            timeout = deviceInfo[TIMEOUT_CONF]
            _LOGGER.debug(
                "Adding %s - %s [Timeout: %d]" % (deviceName, address, timeout)
            )
            device_state = pydreamscreen.get_state(ip=address, timeout=timeout)
            if device_state == None:
                _LOGGER.warn(
                    "Failed to add device [%s] %s. Try setting a 'timeout' in the device config."
                    % (address, deviceName)
                )
            else:
                _LOGGER.debug(
                    "Adding [%s]  %s => State: %s" % (address, deviceName, device_state)
                )
                device = pydreamscreen.get_device(device_state)
                entity = DreamScreenEntity(
                    device=device,
                    current_ids=entity_ids,
                    timeout=timeout,
                    name=deviceName,
                )
                entity_ids.append(entity.entity_id)
                entities.append(entity)
    else:
        _LOGGER.debug("DreamScreen will discover devices.")
        for device in pydreamscreen.get_devices(timeout):
            _LOGGER.info("Discovered device: %s" % device)
            entity = DreamScreenEntity(device=device, current_ids=entity_ids)
            entity_ids.append(entity.entity_id)
            entities.append(entity)

    await component.async_add_entities(entities)
    return True


class DreamScreenEntity(Entity):
    """Wraps DreamScreen in a Home Assistant entity."""

    def __init__(self, device, current_ids, timeout=1, name=None):
        """Initialize state & entity properties."""
        self.device = device
        self.timeout = timeout
        if name == None:
            name = self.device.name
        self.entity_id = generate_entity_id(
            entity_id_format=ENTITY_ID_FORMAT, name=name, current_ids=current_ids
        )
        self._name = name

    @property
    def name(self):
        """Device friendly name from DreamScreen device."""
        return self._name

    @property
    def state(self) -> str:
        """Assume turned on if mode is truthy."""
        return "on" if self.device.mode else "off"

    @property
    def assumed_state(self):
        """If not responding, assume device is off."""
        return "off"

    @property
    def state_attributes(self):
        """Expose DreamScreen device attributes as state properties."""
        import pydreamscreen

        attrs = {
            "group_name": self.device.group_name,
            "group_number": self.device.group_number,
            "device_mode": self.device.mode,
            "brightness": self.device.brightness,
            "ambient_color": "#" + self.device.ambient_color.hex().upper(),
            "ambient_scene": self.device.ambient_scene,
        }

        if isinstance(
            self.device,
            (
                pydreamscreen.DreamScreenHD,
                pydreamscreen.DreamScreen4K,
                pydreamscreen.DreamScreenSolo,
            ),
        ):
            selected_hdmi = None  # type: str
            if self.device.hdmi_input == 0:
                selected_hdmi = self.device.hdmi_input_1_name
            elif self.device.hdmi_input == 1:
                selected_hdmi = self.device.hdmi_input_2_name
            elif self.device.hdmi_input == 2:
                selected_hdmi = self.device.hdmi_input_3_name
            attrs.update(
                {
                    "selected_hdmi": selected_hdmi,
                    "hdmi_input": self.device.hdmi_input,
                    "hdmi_input_1_name": self.device.hdmi_input_1_name,
                    "hdmi_input_2_name": self.device.hdmi_input_2_name,
                    "hdmi_input_3_name": self.device.hdmi_input_3_name,
                    "hdmi_active_channels": self.device.hdmi_active_channels,
                    "hdr_tone_remapping": self.device.hdr_tone_remapping,
                }
            )

        return attrs

    def update(self):
        """When updating entity, call update on the device."""
        self.device.update_current_state(self.timeout)

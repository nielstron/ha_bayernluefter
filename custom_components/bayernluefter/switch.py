"""
Connect to a BL-NET via it's web interface and read and write data
Switch to control digital outputs
"""
import logging
import datetime

from pyernluefter import Bayernluefter

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, CONF_ICON, CONF_RESOURCE
from homeassistant.const import (
    STATE_UNKNOWN,
    STATE_ON, STATE_OFF)
from homeassistant.util import Throttle
from homeassistant.components.switch import SwitchDevice
from homeassistant.helpers import aiohttp_client

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'bayernluefter'

DEFAULT_NAME = "Bayernluefter"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_RESOURCE): cv.url,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Bayernluefter component"""

    session = aiohttp_client.async_get_clientsession(hass)

    bayernluefter = Bayernluefter(config[CONF_RESOURCE], session)
    async_add_entities(
        [
            BayernluefterSwitch(
                name=config[CONF_NAME],
                bayernluefter=bayernluefter
            )
        ]
    )


class BayernluefterSwitch(SwitchDevice):
    """
    Representation of a switch that toggles a digital output of the UVR1611.
    """

    def __init__(self, name, bayernluefter: Bayernluefter):
        """Initialize the switch."""
        self._state = STATE_UNKNOWN
        self._assumed_state = True
        self._bayernluefter = bayernluefter
        self._last_updated = None
        self._name = name

    async def async_update(self):
        """Get the latest data from communication device """
        # check if new data has arrived
        await self._bayernluefter.update()
        self._state = self._bayernluefter.raw_converted()["_SystemOn"]

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._bayernluefter.power_on()
        self._assumed_state = True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self._bayernluefter.power_off()
        self._assumed_state = False

    async def async_toggle(self, **kwargs):
        await self._bayernluefter.power_toggle()
        self._assumed_state = not self._assumed_state

    @property
    def assumed_state(self) -> bool:
        return self._assumed_state


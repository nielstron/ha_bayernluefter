"""
Connect to a Bayernluefter via it's web interface and read and write data
Switch to control the power state
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

try:
    from homeassistant.components.switch import SwitchEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity

from homeassistant.helpers import aiohttp_client

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'bayernluefter'

DEFAULT_NAME = "Bayernluefter"


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Bayernluefter component"""

    if discovery_info is None:
        _LOGGER.warning("Bayernluefter Sensor explicitly configured, should be discovered. Look at documentation for correct setup instructions.")
        return False
    domain = discovery_info["domain"]
    bayernluefter = hass.data["DATA_{}".format(domain)]
    name = DEFAULT_NAME
    ent = [
        BayernluefterPowerSwitch(
            name=f"{name} Power",
            bayernluefter=bayernluefter
        ),
        BayernluefterTimerSwitch(
            name=f"{name} Timer",
            bayernluefter=bayernluefter
        )
    ]
    async_add_entities(ent)


class BayernluefterPowerSwitch(SwitchEntity):
    """
    Representation of a switch that toggles a digital output of the UVR1611.
    """

    def __init__(self, name, bayernluefter: Bayernluefter):
        """Initialize the switch."""
        self._bayernluefter = bayernluefter
        self._name = name

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        try:
            return self._bayernluefter.raw_converted()["_SystemOn"]
        except KeyError:
            return STATE_UNKNOWN

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._bayernluefter.power_on()
        """self._assumed_state = True"""

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self._bayernluefter.power_off()

    async def async_toggle(self, **kwargs):
        await self._bayernluefter.power_toggle()


class BayernluefterTimerSwitch(SwitchEntity):
    """
    Representation of a switch that toggles a digital output of the UVR1611.
    """

    def __init__(self, name, bayernluefter: Bayernluefter):
        """Initialize the switch."""
        self._bayernluefter = bayernluefter
        self._name = name

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        try:
            return self._bayernluefter.raw_converted()["_MaxMode"]
        except KeyError:
            return STATE_UNKNOWN

    async def async_toggle(self, **kwargs):
        await self._bayernluefter.timer_toggle()


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
from homeassistant.components.fan import FanEntity, SUPPORT_SET_SPEED, SPEED_HIGH, SPEED_MEDIUM, SPEED_LOW, SPEED_OFF

_LOGGER = logging.getLogger(__name__)
DEFAULT_NAME = "Bayernluefter"
SPEEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
SUPPORTED_SPEEDS = [
    SPEED_OFF,
    SPEED_LOW,
    SPEED_MEDIUM,
    SPEED_HIGH
]
SPEED_TO_BL = {
    SPEED_OFF: 1,
    SPEED_LOW: 3,
    SPEED_MEDIUM: 6,
    SPEED_HIGH: 9,
}
BL_TO_SPEED = {
    1: SPEED_OFF,
    2: SPEED_OFF,
    3: SPEED_LOW,
    4: SPEED_LOW,
    5: SPEED_MEDIUM,
    6: SPEED_MEDIUM,
    7: SPEED_MEDIUM,
    8: SPEED_HIGH,
    9: SPEED_HIGH,
    10: SPEED_HIGH,
}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Bayernluefter component"""

    if discovery_info is None:
        _LOGGER.warning("Bayernluefter Sensor explicitly configured, should be discovered. Look at documentation for correct setup instructions.")
        return False
    domain = discovery_info["domain"]
    bayernluefter = hass.data["DATA_{}".format(domain)]
    name = DEFAULT_NAME
    ent = [
        BayernluefterFan(
            name=f"{name} Fan Speed",
            bayernluefter=bayernluefter
        ),
    ]
    async_add_entities(ent)


class BayernluefterFan(FanEntity):

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
        # State logs whether the timer mode is active or not
        try:
            return self._bayernluefter.raw_converted()["Speed_Out"] > SPEED_TO_BL[SPEED_OFF]
        except KeyError:
            return STATE_UNKNOWN
 
    @property
    def speed(self) -> str:
        try:
            return BL_TO_SPEED[self._bayernluefter.raw_converted()["Speed_Out"]]
        except KeyError:
            return STATE_UNKNOWN

    async def async_set_speed(self, speed: str) -> None:
        await self._bayernluefter.set_speed(SPEED_TO_BL[speed])

    async def async_turn_off(self, **kwargs):
        await self._bayernluefter.set_speed(SPEED_TO_BL[SPEED_OFF])

    async def async_turn_on(self, **kwargs):
        await self._bayernluefter.set_speed(SPEED_TO_BL[SPEED_MEDIUM])

    @property
    def speed_list(self) -> list:
        return SUPPORTED_SPEEDS
    
    @property
    def supported_features(self) -> int:
        return SUPPORT_SET_SPEED

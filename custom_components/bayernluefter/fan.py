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
from homeassistant.components.fan import FanEntity, SUPPORT_SET_SPEED

DEFAULT_NAME = "Bayernluefter"
SPEEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Bayernluefter component"""

    bayernluefter = discovery_info["bayernluefter"]
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
        return self._bayernluefter.raw_converted()["Speed_In"] > 1

    def speed(self) -> int:
        return self._bayernluefter.raw_converted()["Speed_In"]

    async def async_set_speed(self, speed: int) -> None:
        await self._bayernluefter.set_speed(speed)

    async def async_turn_off(self, **kwargs):
        await self._bayernluefter.set_speed(1)

    async def async_turn_on(self, **kwargs):
        await self._bayernluefter.set_speed(0)

    def speed_list(self) -> list:
        return SPEEDS

    def supported_features(self) -> int:
        return SUPPORT_SET_SPEED

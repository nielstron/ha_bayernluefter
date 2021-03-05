"""
Connect to a Bayernluefter via it's web interface and read and write data
Switch to control the power state
"""
import logging
from typing import Optional

from pyernluefter import Bayernluefter

from homeassistant.components.fan import FanEntity, SUPPORT_SET_SPEED
from homeassistant.util.percentage import (
    ranged_value_to_percentage,
    int_states_in_range,
    percentage_to_ranged_value,
)

_LOGGER = logging.getLogger(__name__)
DEFAULT_NAME = "Bayernluefter"

BAYERNLUEFTER_SPEED_RANGE = (1, 10)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Bayernluefter component"""

    if discovery_info is None:
        _LOGGER.warning(
            "Bayernluefter Sensor explicitly configured, should be discovered. Look at documentation for correct setup instructions."
        )
        return False
    domain = discovery_info["domain"]
    bayernluefter = hass.data["DATA_{}".format(domain)]
    name = DEFAULT_NAME
    ent = [
        BayernluefterFan(name=f"{name} Fan Speed", bayernluefter=bayernluefter),
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
    def speed_count(self):
        return int_states_in_range(BAYERNLUEFTER_SPEED_RANGE)

    def _current_speed(self):
        try:
            return self._bayernluefter.raw_converted()["Speed_Out"]
        except KeyError:
            # TODO currently returns 0 (=off) when not initialized, should (?) be UNKNOWN
            return 0

    @property
    def percentage(self):
        return ranged_value_to_percentage(
            BAYERNLUEFTER_SPEED_RANGE, self._current_speed()
        )

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._current_speed() > 0

    async def async_set_speed(self, percentage: int) -> None:
        await self._bayernluefter.set_speed(
            int(percentage_to_ranged_value(BAYERNLUEFTER_SPEED_RANGE, percentage))
        )

    async def async_turn_off(self, **kwargs):
        await self._bayernluefter.set_speed(0)

    async def async_turn_on(self, percentage: Optional[int] = None, **kwargs):
        await self.async_set_speed(percentage if percentage is not None else 50)

    @property
    def supported_features(self) -> int:
        return SUPPORT_SET_SPEED

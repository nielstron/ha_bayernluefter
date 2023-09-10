"""
Support for Bayernluefter switches.
"""

import logging

from homeassistant.const import STATE_UNKNOWN

try:
    from homeassistant.components.switch import SwitchEntity
except ImportError:
    from homeassistant.components.switch import SwitchDevice as SwitchEntity

from pyernluefter import Bayernluefter

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Bayernluefter component"""

    if discovery_info is None:
        _LOGGER.warning(
            "Bayernluefter Sensor explicitly configured, should be discovered. Look at documentation for correct setup instructions."  # noqa E501
        )
        return False
    domain = discovery_info["domain"]
    name = discovery_info["name"]
    bayernluefter = hass.data[domain][name]
    ent = [
        BayernluefterPowerSwitch(name=f"{name} Power", bayernluefter=bayernluefter),
        BayernluefterTimerSwitch(name=f"{name} Timer", bayernluefter=bayernluefter),
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

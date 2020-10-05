"""Sensor platform for Local Diskspace"""
import datetime
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol 
from homeassistant.components.sensor import PLATFORM_SCHEMA 
from homeassistant.const import CONF_NAME, CONF_ICON, CONF_RESOURCE, TEMP_CELSIUS, CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER, STATE_UNKNOWN

try:  # TODO: Remove for core PR. This ensures compatibility with <0.115
    from homeassistant.const import PERCENTAGE
except Exception:
    from homeassistant.const import UNIT_PERCENTAGE as PERCENTAGE
    
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.helpers import aiohttp_client

from pyernluefter import Bayernluefter

__version__ = "v0.1"
_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=60)

DEFAULT_NAME = "Bayernluefter"

TEMP_MEASURES = [
    "Temp_In",
    "Temp_Out",
    "Temp_Fresh"
]
REL_HUM_MEASURES = [
    "rel_Humidity_In",
    "rel_Humidity_Out",
    "Efficiency",  # technically not humidity but also percent
]
ABS_HUM_MEASURES = [
    "abs_Humidity_In",
    "abs_Humidity_Out",
]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup Platform"""

    if discovery_info is None:
        _LOGGER.warning("Bayernluefter Sensor explicitly configured, should be discovered. Look at documentation for correct setup instructions.")
        return False
    domain = discovery_info["domain"]
    bayernluefter = hass.data["DATA_{}".format(domain)]
    name = DEFAULT_NAME
    ent = [
        BayernluefterSensor(
            name=name,
            bayernluefter=bayernluefter
        )
    ]
    ent.extend([BayernluefterSpecialSensor(name=f"{name} {mt}", measure_type=mt, unit_of_measurement=TEMP_CELSIUS, bayernluefter=bayernluefter) for mt in TEMP_MEASURES])
    ent.extend([BayernluefterSpecialSensor(name=f"{name} {mt}", measure_type=mt, unit_of_measurement=PERCENTAGE, bayernluefter=bayernluefter) for mt in REL_HUM_MEASURES])
    ent.extend([BayernluefterAbsSensor(name=f"{name} {mt}", measure_type=mt, unit_of_measurement=CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER, bayernluefter=bayernluefter) for mt in ABS_HUM_MEASURES])
    async_add_entities(ent)


class BayernluefterSensor(Entity):
    def __init__(self, name: str, bayernluefter: Bayernluefter):
        self._state = None
        self._name = name
        self._attributes = {}
        self._bayernluefter = bayernluefter

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def state_attributes(self):
        return self._attributes

    def update(self):

        self._attributes = self._bayernluefter.raw()
        try:
            self._state = self._bayernluefter.raw_converted()["SystemMode"].value
        except KeyError:
            self._state = STATE_UNKNOWN


class BayernluefterSpecialSensor(BayernluefterSensor):

    def __init__(self, name: str, measure_type: str, unit_of_measurement, bayernluefter: Bayernluefter):
        super().__init__(name, bayernluefter)
        self._type = measure_type
        self._unit_of_measurement = unit_of_measurement

    @property
    def unit_of_measurement(self) -> str:
        return self._unit_of_measurement

    def update(self):
        try:
            self._state = self._bayernluefter.raw_converted()[self._type]
        except KeyError:
            self._state = STATE_UNKNOWN


class BayernluefterAbsSensor(BayernluefterSpecialSensor):

    def update(self):
        # convert grams per cubic meter to milligrams per cubic meter
        try:
            self._state = self._bayernluefter.raw_converted()[self._type]/1000
        except KeyError:
            self._state = STATE_UNKNOWN

"""Sensor platform for Local Diskspace"""
import datetime
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol 
from homeassistant.components.sensor import PLATFORM_SCHEMA 
from homeassistant.const import CONF_NAME, CONF_ICON, CONF_RESOURCE
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.helpers import aiohttp_client

from bayernluefter import Bayernluefter

__version__ = "v0.1"
_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=60)

DEFAULT_NAME = "Bayernluefter"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_RESOURCE): cv.url,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    "Setup Platform"
    session = aiohttp_client.async_get_clientsession(hass)

    bayernluefter = Bayernluefter(config[CONF_RESOURCE], session)
    async_add_entities(
        [
            BayernluefterSensor(
                name=config[CONF_NAME],
                bayernluefter=bayernluefter
            )
        ]
    )

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

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):

        try:
            await self._bayernluefter.update()
            self._attributes = self._bayernluefter.raw_converted()
            self._state = self._attributes["SystemMode"].value
        except ValueError:
            # if an exception is thrown, server does not support bayernluefter
            # and should not be set up
            _LOGGER.info("Device at %s does not support SyncThru", self._bayernluefter.url)




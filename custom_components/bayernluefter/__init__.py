"""
Sensor and Switch for Bayernluefter
"""
import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform

from homeassistant.const import (
    CONF_RESOURCE,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    TEMP_CELSIUS,
)
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import aiohttp_client

from pyernluefter import Bayernluefter

_LOGGER = logging.getLogger(__name__)

DOMAIN = "bayernluefter"

# scan every 30 seconds per default
DEFAULT_SCAN_INTERVAL = 30

DEFAULT_NAME = "Bayernluefter"

UNIT = {"analog": TEMP_CELSIUS, "speed": "rpm", "power": "kW", "energy": "kWh"}
ICON = {
    "analog": "mdi:thermometer",
    "speed": "mdi:speedometer",
    "power": "mdi:power-plug",
    "energy": "mdi:power-plug",
}

BL_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema(
        {
            vol.Required(CONF_RESOURCE): cv.url,
            vol.Optional(
                CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
            ): cv.positive_int,
            vol.Optional(
                CONF_NAME, default=DEFAULT_NAME,
            ): cv.string,
        }
    )},
    extra=vol.ALLOW_EXTRA,
)
CONFIG_SCHEMA = vol.Any([BL_SCHEMA], BL_SCHEMA)


async def async_setup(hass: HomeAssistant, raw_config):
    """Set up the BLNET component"""

    configs = raw_config[DOMAIN]
    if not isinstance(configs, list):
        configs = [configs]
    hass.data[DOMAIN] = {}
    used_names = set()

    for config in configs:
        resource = config.get(CONF_RESOURCE)
        scan_interval = config.get(CONF_SCAN_INTERVAL)
        name = config.get(CONF_NAME)
        session = aiohttp_client.async_get_clientsession(hass)

        # Validate that unique BL entities are created
        if name in used_names:
            _LOGGER.error("Configuration invalid: use unique names when setting up multiple BayernLuefter entities")
            del hass.data[DOMAIN]
            return False
        used_names.add(name)

        # Initialize the BL-NET sensor
        try:
            blnet = Bayernluefter(resource, session)
        except (ValueError, AssertionError) as ex:
            if isinstance(ex, ValueError):
                _LOGGER.error("No Bayernluefter reached at {}".format(resource))
            else:
                _LOGGER.error("Configuration invalid: {}".format(ex))
            del hass.data[DOMAIN]
            return False

        # set the communication entity
        hass.data[DOMAIN][name] = blnet

        # make sure the communication device gets updated once in a while
        async def fetch_data(*_):
            return await blnet.update()

        # Get the latest data from REST API and load
        # sensors and switches accordingly
        disc_info = {
            "domain": DOMAIN,
            "name": name,
        }
        hass.async_create_task(async_load_platform(hass, "sensor", DOMAIN, disc_info, config))
        hass.async_create_task(async_load_platform(hass, "switch", DOMAIN, disc_info, config))
        hass.async_create_task(async_load_platform(hass, "fan", DOMAIN, disc_info, config))

        # Repeat if data fetching fails at first
        async_track_time_interval(hass, fetch_data, timedelta(seconds=scan_interval))

    # Fetch method takes care of adding dicovered sensors
    return True

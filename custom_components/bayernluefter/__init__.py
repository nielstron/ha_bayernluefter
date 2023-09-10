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

BL_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_RESOURCE): cv.url,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): cv.positive_int,
        vol.Optional(
            CONF_NAME, default=DEFAULT_NAME,
        ): cv.string,
    }
)
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(cv.ensure_list, [BL_SCHEMA]),
    },
    extra=vol.ALLOW_EXTRA,
)

def gen_fetch_data(blnet):
    async def fetch_data(*_):
        return await blnet.update()
    return fetch_data


async def async_setup(hass: HomeAssistant, raw_config):
    """Set up the BLNET component"""

    configs = raw_config[DOMAIN]
    used_names = set(config[CONF_NAME] for config in configs)
    # Validate that unique BL entities are created
    if len(used_names) != len(configs):
        _LOGGER.error("Configuration invalid: use unique names when setting up multiple BayernLuefter entities")

    hass.data[DOMAIN] = {}

    session = aiohttp_client.async_get_clientsession(hass)
    for config in configs:
        resource = config.get(CONF_RESOURCE)
        scan_interval = config.get(CONF_SCAN_INTERVAL)
        name = config.get(CONF_NAME)

        # Initialize the BL-NET sensor
        try:
            blnet = Bayernluefter(resource, session)
        except (ValueError, AssertionError) as ex:
            if isinstance(ex, ValueError):
                _LOGGER.error("No Bayernluefter reached at {}".format(resource))
            else:
                _LOGGER.error("Configuration invalid: {}".format(ex))
            continue

        # set the communication entity
        hass.data[DOMAIN][name] = blnet

        disc_info = {
            "domain": DOMAIN,
            "name": name,
        }
        # trigger an initial fetching impulse
        hass.async_create_task(gen_fetch_data(blnet)())
        # load sensors and switches accordingly
        hass.async_create_task(async_load_platform(hass, "sensor", DOMAIN, disc_info, config))
        hass.async_create_task(async_load_platform(hass, "switch", DOMAIN, disc_info, config))
        hass.async_create_task(async_load_platform(hass, "fan", DOMAIN, disc_info, config))

        # make sure the communication device gets updated once in a while
        async_track_time_interval(hass, gen_fetch_data(blnet), timedelta(seconds=scan_interval))

    # Fetch method takes care of adding dicovered sensors
    return True

# __init__.py
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
import logging, time
from .const import DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, update=False):
    """Set up T9plus from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    await async_detect_and_fix_old_entry(hass, entry)  # Tries to detect and fix old entries.
    _LOGGER.debug("Setting up entry %s.", entry.entry_id)

    hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN][entry.entry_id]['entry_data'] = entry.options

    await hass.config_entries.async_forward_entry_setups(entry, ["light"])
    if not update:
        entry.add_update_listener(async_update_entry)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry. Called by HA."""
    _LOGGER.debug("Unload entry %s.", entry.entry_id)

    del hass.data[DOMAIN][entry.entry_id]

    return await hass.config_entries.async_unload_platforms(entry, ["light"])


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Called by HA when the config entry is updated.
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry, True)
    _LOGGER.debug("Updated entry %s.", entry.entry_id)


async def async_detect_and_fix_old_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Detect old entry. Called for every entry when HA find the versions don't match."""


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry. Called for every entry when HA find the versions don't match."""
    return True


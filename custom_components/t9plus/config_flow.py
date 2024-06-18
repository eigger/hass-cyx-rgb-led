import requests
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, OptionsFlow
from homeassistant.helpers.selector import ObjectSelector, ObjectSelectorConfig, TextSelector, TextSelectorConfig, \
    DurationSelector, DurationSelectorConfig, NumberSelector, NumberSelectorConfig, NumberSelectorMode, SelectSelector, \
    SelectSelectorConfig, SelectSelectorMode

from .const import DOMAIN, VERSION
import voluptuous as vol

import logging

_LOGGER = logging.getLogger(__name__)

class ConfigFlowHandler(config_entries.ConfigFlow, config_entries.OptionsFlow, domain=DOMAIN):

    def __init__(self, config_entry: ConfigEntry = None):
        self.entry_options = config_entry.options if config_entry else {"port": "/dev/ttyS2", "baudrate": 9600}
    async def async_step_user(self, user_input: dict = None):
        # Called when the user creates a new entry. This will open a page with discovered new devices if there's any.
        if user_input:
            return await self.async_step_config({"port": user_input["selector"] if not user_input["selector"] == "manual" else "", "dont_test": True})
        return await self.async_step_config()

    async def async_step_config(self, user_input: dict = None):
        errors = {}
        if user_input is not None and not user_input.get("dont_test", False):
            try:
                if await self.verify_unique_device(user_input.get('port')):
                    # TODO: Add config verification
                    return self.async_create_entry(title="T9Plus", data=user_input,
                                                   options=user_input)  # it's required to set
                # data anyways since otherwise the option flow won't save the data. (HA bug?) PS: DATA ISN'T USED HERE.
                else:
                    errors["port"] = "already_configured"
            except Exception as e:
                _LOGGER.error("Error setting up T9Plus: %s", e)
                errors["port"] = "connection"
        else:
            user_input = {} if user_input is None else user_input

        return self.async_show_form(
            step_id="config", errors=errors, data_schema=vol.Schema({
                vol.Required("port",
                             default=user_input.get("port", self.entry_options.get("port"))): str,
                vol.Required("baudrate",
                             default=user_input.get("baudrate", self.entry_options.get("baudrate"))): int,
            })
        )

    # Gives the OptionsFlow class to HA
    def async_get_options_flow(config_entry):
        return ConfigFlowHandler(config_entry)

    async def async_step_init(self, user_input=None):
        # This is set since the Option Flow's first step is always init.
        return await self.async_step_config(user_input)

    async def verify_unique_device(self, port: str):
        """Check if the device is already configured."""

        # return True #DEBUG
        if port == self.entry_options.get("port"):  # If the user didn't change the IP, it's still valid.
            return True

        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.options['port'] == port:
                return False
        return True

from homeassistant.components.light import (LightEntity, ATTR_EFFECT, ATTR_BRIGHTNESS, ATTR_TRANSITION, SUPPORT_BRIGHTNESS, ColorMode, LightEntityFeature)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from . import DOMAIN, VERSION
from . import led
import logging


_LOGGER = logging.getLogger(__name__)
BRIGHTNESS_SCALE = (1, 100)

async def async_setup_entry(hass, config_entry: ConfigEntry, async_add_entities):
    async_add_entities([ CyxRgbLed(config_entry=config_entry) ], True)

class CyxRgbLed(LightEntity):
    def __init__(self, config_entry: ConfigEntry = None):
        self._config_entry = config_entry
        self._port = config_entry.data.get('port')
        self._baudrate = config_entry.data.get('baudrate')
        self._attr_has_entity_name = True
        self._name = "Light"
        self.color_mode = ColorMode.BRIGHTNESS
        self._transition = 3
        self._brightness = 50
        self._state = True
        self.effect_list = ["Rainbow", "Breating", "Color Cycle", "Auto"]
        self.effect = "Rainbow"
        _LOGGER.info(f"CYX RGB LED port from configuration: {self._port}, {self._baudrate}")

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self) -> bool | None:
        return self._state

    @property
    def brightness(self):
        return self._brightness

    def turn_on(self, **kwargs):
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
        if ATTR_EFFECT in kwargs:
            self.effect = kwargs[ATTR_EFFECT]
        if ATTR_TRANSITION in kwargs:
            self._transition = kwargs[ATTR_TRANSITION]
        brightness_percent = int((self._brightness / 255.0) * 100)
        brightness = int(0x05 - (brightness_percent * 0.04))
        mode = 0x05
        if self.effect == "Rainbow": mode = 0x01
        elif self.effect == "Breating": mode = 0x02
        elif self.effect == "Color Cycle": mode = 0x03
        transition = max(1, min(self._transition, 5))
        self._state = True
        led.control(self._port, self._baudrate, mode, brightness, transition)

    def turn_off(self, **kwargs):
        self._state = False
        led.control(self._port, self._baudrate, 0x05, 0x05, 0x03)

    def update(self) -> None:
        pass

    @property
    def supported_color_modes(self) -> set[ColorMode] | set[str] | None:
        return {ColorMode.BRIGHTNESS}
    
    @property
    def supported_features(self) -> LightEntityFeature:
        """Flag supported features."""
        return self._attr_supported_features | LightEntityFeature.EFFECT | LightEntityFeature.TRANSITION
    
    @property
    def unique_id(self):
        return "light_" + str(self._config_entry.entry_id)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._config_entry.entry_id)) if self._config_entry is not None else (DOMAIN, "cyx_rgb_led")},
            name=self._config_entry.title,
            manufacturer="CYX",
            model="RGB LED",
            sw_version=VERSION,
        )

    @property
    def icon(self) -> str | None:
        """Icon of the entity, based on time."""
        if self._state:
            return "mdi:led-on"    
        return "mdi:led-off"
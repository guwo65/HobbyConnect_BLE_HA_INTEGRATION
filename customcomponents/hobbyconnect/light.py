from __future__ import annotations

import math
from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.color import brightness_to_value, value_to_brightness

from .const import DOMAIN, LIGHTS

DIMMER_SCALE = (1, 15)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        HobbyConnectLight(coordinator, entry, *cfg)
        for cfg in LIGHTS
    )


class HobbyConnectLight(CoordinatorEntity, LightEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, name, channel, dimmable, inverted_command):
        super().__init__(coordinator)
        self._entry = entry
        self._channel = channel
        self._dimmable = dimmable
        self._inverted_command = inverted_command
        self._last_nonzero_level = 15
        self._attr_name = name
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_{channel.lower()}"
        self._attr_supported_color_modes = {
            ColorMode.BRIGHTNESS if dimmable else ColorMode.ONOFF
        }

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="HobbyConnect",
            manufacturer="Hobby",
            model="HobbyConnect BLE",
        )

    @property
    def color_mode(self):
        return ColorMode.BRIGHTNESS if self._dimmable else ColorMode.ONOFF

    @property
    def available(self):
        return super().available and self._channel in (self.coordinator.data or {})

    @property
    def is_on(self):
        value = (self.coordinator.data or {}).get(self._channel)
        if value is None:
            return None
        return value > 0

    @property
    def brightness(self):
        if not self._dimmable:
            return None
        value = (self.coordinator.data or {}).get(self._channel)
        if value is None or value <= 0:
            return None
        value = min(15, max(1, value))
        self._last_nonzero_level = value
        return value_to_brightness(DIMMER_SCALE, value)

    async def async_turn_on(self, **kwargs: Any):
        if self._dimmable:
            if ATTR_BRIGHTNESS in kwargs:
                level = math.ceil(
                    brightness_to_value(DIMMER_SCALE, int(kwargs[ATTR_BRIGHTNESS]))
                )
                level = min(15, max(1, level))
            else:
                current = (self.coordinator.data or {}).get(self._channel, 0)
                level = current if 1 <= current <= 15 else self._last_nonzero_level
            self._last_nonzero_level = level
            await self.coordinator.async_set_channel(self._channel, level)
            return

        value = 0 if self._inverted_command else 1
        await self.coordinator.async_set_channel(self._channel, value)
        if self._inverted_command:
            data = dict(self.coordinator.data or {})
            data[self._channel] = 1
            self.coordinator.async_set_updated_data(data)

    async def async_turn_off(self, **kwargs: Any):
        if self._dimmable:
            current = (self.coordinator.data or {}).get(self._channel, 0)
            if 1 <= current <= 15:
                self._last_nonzero_level = current
            await self.coordinator.async_set_channel(self._channel, 0)
            return

        value = 1 if self._inverted_command else 0
        await self.coordinator.async_set_channel(self._channel, value)
        if self._inverted_command:
            data = dict(self.coordinator.data or {})
            data[self._channel] = 0
            self.coordinator.async_set_updated_data(data)

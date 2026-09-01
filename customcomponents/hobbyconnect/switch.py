from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HobbyBinarySwitch(
            coordinator, entry, "Fußbodenerwärmung",
            "FLOOR_HEATER_ON", "FLOOR_HEATER_ON"
        ),
        HobbyBinarySwitch(
            coordinator, entry, "Therme",
            "THERME_ON", "THERME_ON"
        ),
    ])


class HobbyBinarySwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, name, state_key, command_key):
        super().__init__(coordinator)
        self._entry = entry
        self._state_key = state_key
        self._command_key = command_key
        self._attr_name = name
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_{state_key.lower()}"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="HobbyConnect",
            manufacturer="Hobby",
            model="HobbyConnect BLE",
        )

    @property
    def available(self):
        return super().available and self._state_key in (self.coordinator.data or {})

    @property
    def is_on(self):
        value = (self.coordinator.data or {}).get(self._state_key)
        if value is None:
            return None
        return int(value) == 1

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_send_command(f"{self._command_key}-1")
        data = dict(self.coordinator.data or {})
        data[self._state_key] = 1
        self.coordinator.async_set_updated_data(data)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_send_command(f"{self._command_key}-0")
        data = dict(self.coordinator.data or {})
        data[self._state_key] = 0
        self.coordinator.async_set_updated_data(data)

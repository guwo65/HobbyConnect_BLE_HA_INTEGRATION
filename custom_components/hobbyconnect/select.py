from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_OPTIONS, MODE_TO_VALUE


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HobbyOperatingModeSelect(coordinator, entry)])


class HobbyOperatingModeSelect(CoordinatorEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_options = list(MODE_TO_VALUE.keys())

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = "Betriebsmodus"
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_hs_key_state"

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
        return super().available and "HS_KEY_STATE" in (self.coordinator.data or {})

    @property
    def current_option(self):
        value = (self.coordinator.data or {}).get("HS_KEY_STATE")
        if value is None:
            return None
        return MODE_OPTIONS.get(int(value))

    async def async_select_option(self, option: str):
        await self.coordinator.async_set_main_mode(MODE_TO_VALUE[option])

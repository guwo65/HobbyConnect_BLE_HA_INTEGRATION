from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CALIBRATION_TEMP_IN,
    CALIBRATION_TEMP_OUT,
    DOMAIN,
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HobbyTemperatureSensor(
            coordinator,
            entry,
            "Innentemperatur",
            "TEMP_IN",
            CALIBRATION_TEMP_IN,
        ),
        HobbyTemperatureSensor(
            coordinator,
            entry,
            "Außentemperatur",
            "TEMP_OUT",
            CALIBRATION_TEMP_OUT,
        ),
        HobbyWaterSensor(coordinator, entry),
    ])


class BaseHobbySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, name, key):
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_{key.lower()}"

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
        return super().available and self._key in (self.coordinator.data or {})


class HobbyTemperatureSensor(BaseHobbySensor):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry, name, key, calibration_key):
        super().__init__(coordinator, entry, name, key)
        self._calibration_key = calibration_key

    @property
    def native_value(self):
        raw = (self.coordinator.data or {}).get(self._key)
        if raw is None:
            return None

        calibration = float(self._entry.options.get(self._calibration_key, 0.0))
        return round(float(raw) + calibration, 1)


class HobbyWaterSensor(BaseHobbySensor):
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "Wasserstand", "WATER_LEVEL")

    @property
    def native_value(self):
        raw = (self.coordinator.data or {}).get(self._key)
        if raw is None:
            return None
        return max(0, min(4, int(raw))) * 25

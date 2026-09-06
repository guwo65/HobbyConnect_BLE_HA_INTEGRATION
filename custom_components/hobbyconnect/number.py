from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CALIBRATION_TEMP_IN,
    CALIBRATION_TEMP_OUT,
    DOMAIN,
)

CALIBRATION_MIN = -10.0
CALIBRATION_MAX = 10.0
CALIBRATION_STEP = 0.1


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        HobbyTemperatureCalibrationNumber(
            coordinator,
            entry,
            "Kalibrierung Innentemperatur",
            CALIBRATION_TEMP_IN,
        ),
        HobbyTemperatureCalibrationNumber(
            coordinator,
            entry,
            "Kalibrierung Außentemperatur",
            CALIBRATION_TEMP_OUT,
        ),
    ])


class HobbyTemperatureCalibrationNumber(CoordinatorEntity, NumberEntity):
    """Local temperature correction stored in the config entry options."""

    _attr_has_entity_name = True
    _attr_native_min_value = CALIBRATION_MIN
    _attr_native_max_value = CALIBRATION_MAX
    _attr_native_step = CALIBRATION_STEP
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, entry, name, option_key):
        super().__init__(coordinator)
        self._entry = entry
        self._option_key = option_key
        self._attr_name = name
        self._attr_unique_id = (
            f"{entry.unique_id or entry.entry_id}_{option_key}"
        )

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="HobbyConnect",
            manufacturer="Hobby",
            model="HobbyConnect BLE",
        )

    @property
    def native_value(self):
        return float(self._entry.options.get(self._option_key, 0.0))

    async def async_set_native_value(self, value: float) -> None:
        value = round(float(value), 1)
        options = dict(self._entry.options)
        options[self._option_key] = value

        self.hass.config_entries.async_update_entry(
            self._entry,
            options=options,
        )

        # Notify all CoordinatorEntity consumers immediately. This makes the
        # calibrated temperature sensors update without a BLE refresh/write.
        self.coordinator.async_set_updated_data(
            dict(self.coordinator.data or {})
        )

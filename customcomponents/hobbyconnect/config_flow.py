from __future__ import annotations

import logging
from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.const import CONF_ADDRESS
from .const import ADVERTISEMENT_SERVICE_UUID, DOMAIN

_LOGGER = logging.getLogger(__name__)
TARGET_NAME = "HobbyConnect Data"


def _is_hobbyconnect(service_info: bluetooth.BluetoothServiceInfoBleak) -> bool:
    name = service_info.name or service_info.device.name or ""
    uuids = {uuid.lower() for uuid in service_info.service_uuids}
    return (
        ADVERTISEMENT_SERVICE_UUID in uuids
        or name == TARGET_NAME
        or name.startswith("HobbyConnect")
    )


class HobbyConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                await bluetooth.async_request_active_scan(self.hass)
            except Exception as err:
                _LOGGER.debug("Bluetooth active scan request failed: %s", err)

            matched = next(
                (
                    info
                    for info in bluetooth.async_discovered_service_info(
                        self.hass, connectable=True
                    )
                    if _is_hobbyconnect(info)
                ),
                None,
            )

            if matched is None:
                errors["base"] = "cannot_connect"
            else:
                address = matched.address
                ble_device = bluetooth.async_ble_device_from_address(
                    self.hass, address, connectable=True
                )
                if ble_device is None:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(address.lower())
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="HobbyConnect",
                        data={CONF_ADDRESS: address},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=None,
            errors=errors,
        )

    async def async_step_bluetooth(self, discovery_info):
        if not _is_hobbyconnect(discovery_info):
            return self.async_abort(reason="not_hobbyconnect")
        address = discovery_info.address
        await self.async_set_unique_id(address.lower())
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="HobbyConnect",
            data={CONF_ADDRESS: address},
        )

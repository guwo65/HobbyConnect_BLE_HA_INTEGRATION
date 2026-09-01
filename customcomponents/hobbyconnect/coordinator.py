from __future__ import annotations

import asyncio
import logging
import re
from datetime import timedelta
from typing import Any

from bleak import BleakClient

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BT_ID,
    BT_VARS_TIMEOUT_SECONDS,
    CHAR_UUID,
    DOMAIN,
    SCAN_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)
PAIR_RE = re.compile(r"([A-Z][A-Z0-9_]*):(-?\d+)")
TEMP_RE = re.compile(r"(TEMP_(?:IN|OUT)):\s*(-?\d+)[,.](\d+)\^C")


class HobbyConnectCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Persistent BLE coordinator for HobbyConnect."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.address = entry.data["address"]

        self._client: BleakClient | None = None
        self._notify_started = False
        self._ble_lock = asyncio.Lock()
        self._bt_stop = asyncio.Event()
        self._rx_state: dict[str, Any] = {}

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.address}",
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )

    def _parse_notification(self, text: str) -> dict[str, Any]:
        changed: dict[str, Any] = {}

        for name, value_text in PAIR_RE.findall(text):
            try:
                changed[name] = int(value_text)
            except ValueError:
                pass

        for name, whole, frac in TEMP_RE.findall(text):
            try:
                changed[name] = float(f"{whole}.{frac}")
            except ValueError:
                pass

        return changed

    def _notification_handler(self, sender: Any, data: bytearray) -> None:
        text = bytes(data).decode("ascii", errors="ignore")
        changed = self._parse_notification(text)

        if changed:
            self._rx_state.update(changed)

            merged = dict(self.data or {})
            merged.update(changed)

            # This is the key difference in 0.3.3:
            # spontaneous notifications caused by the original panel are
            # immediately reflected in Home Assistant.
            self.async_set_updated_data(merged)

            _LOGGER.debug("HobbyConnect RX state update: %s", changed)

        if "BT_STOP:" in text:
            self._bt_stop.set()

    def _disconnected(self, client: BleakClient) -> None:
        _LOGGER.debug("HobbyConnect BLE disconnected")
        self._notify_started = False
        if self._client is client:
            self._client = None

    async def _ensure_connected(self) -> BleakClient:
        if self._client is not None and self._client.is_connected:
            return self._client

        ble_device = bluetooth.async_ble_device_from_address(
            self.hass,
            self.address,
            connectable=True,
        )
        if ble_device is None:
            raise UpdateFailed(
                f"HobbyConnect device {self.address} is not reachable"
            )

        last_err = None
        for attempt in range(1, 4):
            client = None
            try:
                client = BleakClient(
                    ble_device,
                    disconnected_callback=self._disconnected,
                )
                await client.connect()

                if client.services.get_characteristic(CHAR_UUID) is None:
                    raise UpdateFailed(
                        f"HobbyConnect characteristic {CHAR_UUID} not found"
                    )

                await client.start_notify(
                    CHAR_UUID,
                    self._notification_handler,
                )

                self._client = client
                self._notify_started = True

                # Initialize protocol session once after connection.
                await client.write_gatt_char(
                    CHAR_UUID,
                    f"net-BT_ID-{BT_ID}".encode("ascii"),
                    response=True,
                )
                await asyncio.sleep(0.45)

                _LOGGER.info(
                    "Persistent HobbyConnect BLE connection established to %s",
                    self.address,
                )
                return client

            except UpdateFailed:
                if client is not None:
                    try:
                        await client.disconnect()
                    except Exception:
                        pass
                raise
            except Exception as err:
                last_err = err
                if client is not None:
                    try:
                        await client.disconnect()
                    except Exception:
                        pass
                if attempt < 3:
                    await asyncio.sleep(float(attempt))

        raise UpdateFailed(
            f"Unable to establish HobbyConnect BLE connection: {last_err}"
        )

    async def _drop_connection(self) -> None:
        client = self._client
        self._client = None
        self._notify_started = False

        if client is not None:
            try:
                if client.is_connected:
                    try:
                        await client.stop_notify(CHAR_UUID)
                    except Exception:
                        pass
                    await client.disconnect()
            except Exception:
                pass

    async def async_shutdown(self) -> None:
        async with self._ble_lock:
            await self._drop_connection()

    async def _async_update_data(self) -> dict[str, Any]:
        async with self._ble_lock:
            client = await self._ensure_connected()

            self._rx_state = {}
            self._bt_stop.clear()

            try:
                # Refresh the protocol ID before a full variable request.
                await client.write_gatt_char(
                    CHAR_UUID,
                    f"net-BT_ID-{BT_ID}".encode("ascii"),
                    response=True,
                )
                await asyncio.sleep(0.35)

                await client.write_gatt_char(
                    CHAR_UUID,
                    b"net-BT_VARS",
                    response=True,
                )

                try:
                    await asyncio.wait_for(
                        self._bt_stop.wait(),
                        timeout=BT_VARS_TIMEOUT_SECONDS,
                    )
                except asyncio.TimeoutError:
                    if not self._rx_state and not self.data:
                        raise UpdateFailed(
                            "Timed out waiting for HobbyConnect status"
                        )

                await asyncio.sleep(0.20)

                merged = dict(self.data or {})
                merged.update(self._rx_state)
                return merged

            except UpdateFailed:
                raise
            except Exception as err:
                # Force a fresh session on the next poll/write if this BLE
                # session has become stale.
                await self._drop_connection()
                raise UpdateFailed(
                    f"HobbyConnect communication failed: {err}"
                ) from err

    async def async_send_command(self, command: str) -> None:
        """Send a command over the persistent BLE session."""
        async with self._ble_lock:
            last_err = None

            for attempt in range(1, 4):
                try:
                    client = await self._ensure_connected()

                    # Keep protocol session alive/authorized.
                    await client.write_gatt_char(
                        CHAR_UUID,
                        f"net-BT_ID-{BT_ID}".encode("ascii"),
                        response=True,
                    )
                    await asyncio.sleep(0.20)

                    payload = f"net-{command}"
                    _LOGGER.debug(
                        "HobbyConnect TX attempt %d/3: %s",
                        attempt,
                        payload,
                    )

                    await client.write_gatt_char(
                        CHAR_UUID,
                        payload.encode("ascii"),
                        response=True,
                    )
                    await asyncio.sleep(0.15)
                    return

                except Exception as err:
                    last_err = err
                    _LOGGER.warning(
                        "HobbyConnect write attempt %d/3 failed for %s: %r",
                        attempt,
                        command,
                        err,
                    )
                    await self._drop_connection()
                    if attempt < 3:
                        await asyncio.sleep(float(attempt))

            raise UpdateFailed(
                f"Failed writing HobbyConnect command {command} after 3 attempts: {last_err}"
            )

    async def async_set_channel(self, channel: str, value: int) -> None:
        await self.async_send_command(f"{channel}-{value}")

        # Optimistic update; a real panel/device notification can overwrite it
        # immediately if the device reports a different state.
        new_data = dict(self.data or {})
        new_data[channel] = value
        self.async_set_updated_data(new_data)

    async def async_set_main_mode(self, target_state: int) -> None:
        current = (self.data or {}).get("HS_KEY_STATE")
        if current is None:
            await self.async_request_refresh()
            current = (self.data or {}).get("HS_KEY_STATE")

        if current == target_state:
            return

        # Only transitions already observed during probing are enabled.
        transitions = {
            (0, 1): ["HS_KEY-0"],
            (1, 2): ["HS_KEY-1"],
            (0, 2): ["HS_KEY-0", "HS_KEY-1"],
            (2, 1): ["HS_KEY-2"],
        }

        seq = transitions.get((int(current), int(target_state)))
        if seq is None:
            raise UpdateFailed(
                f"Main-mode transition {current} -> {target_state} "
                "is not yet safely confirmed"
            )

        for command in seq:
            await self.async_send_command(command)
            await asyncio.sleep(0.25)

        # Do not force HS_KEY_STATE optimistically here. The persistent notify
        # listener should report the actual panel/device state.

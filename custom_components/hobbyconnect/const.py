from __future__ import annotations

DOMAIN = "hobbyconnect"

CHAR_UUID = "00000001-0000-1000-8000-00805f9b34fb"
ADVERTISEMENT_SERVICE_UUID = "eaffffff-ffff-ffff-ffff-fffffffffff0"
BT_ID = "02:00:00:00:00:01"
SCAN_INTERVAL_SECONDS = 30
BT_VARS_TIMEOUT_SECONDS = 12

LIGHTS = (
    ("Dusche", "LIGHT_DUSCHE", False, False),
    ("Bad", "LIGHT_WASCH", False, False),
    ("Extra 1", "LIGHT_ZUSATZL", False, False),
    ("Extra 3", "LIGHT_ZUSATZR", False, False),
    ("Küche 1", "LIGHT_KUECHE", False, True),
    ("Küche 2", "LIGHT_KUECHE2", False, False),
    ("Ambiente 1", "LIGHT_AMB1", False, False),
    ("Ambiente 2", "LIGHT_AMB2", False, False),
    ("Ambiente 3", "LIGHT_AMB3", False, False),
    ("Bett 1", "LIGHT_DIM0", True, False),
    ("Bett 2", "LIGHT_DIM1", True, False),
    ("Decke", "LIGHT_DIM2", True, False),
    ("Wand", "LIGHT_DIM3", True, False),
    ("Extra 2", "LIGHT_DIM4", True, False),
)

MODE_OPTIONS = {
    0: "Fahrzeug Standby",
    1: "Nur Geräte",
    2: "Geräte und Lichter",
}
MODE_TO_VALUE = {v: k for k, v in MODE_OPTIONS.items()}

# Local Home Assistant temperature calibration offsets.
# These values are stored in ConfigEntry.options and are never written to BLE.
CALIBRATION_TEMP_IN = "temperature_calibration_inside"
CALIBRATION_TEMP_OUT = "temperature_calibration_outside"

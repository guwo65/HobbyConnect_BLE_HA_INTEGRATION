# HobbyConnect_BLE_HA_INTEGRATION
# HobbyConnect for Home Assistant

[Deutsch](#deutsch) · [English](#english)

A local Home Assistant custom integration for controlling and monitoring a compatible **HobbyConnect** system via **Bluetooth Low Energy (BLE)**.

> Current version / Aktuelle Version: **0.3.4**

---

# Deutsch

## Übersicht

**HobbyConnect for Home Assistant** bindet ein kompatibles HobbyConnect-System direkt per Bluetooth Low Energy in Home Assistant ein.

Die Kommunikation erfolgt lokal. Für diese Integration ist kein ESP32, MQTT-Broker oder zusätzlicher Cloud-Dienst erforderlich.

Die Integration stellt – abhängig von der vorhandenen HobbyConnect-Ausstattung – Lichtkanäle, Temperaturen, Wasserstand, 230-V-Verbraucher und den Haupt-Betriebsmodus als native Home-Assistant-Entitäten bereit.

Entwickelt und getestet in einem Hobby 720WQC(Modelljahr 2023), Lichtsteuersystem 2022( Premium,Excellent,Prestige,Edition), Toptron Artikel-Nr. EL770, und dem neuen Hobby Touchdisplay.
RaspberryPi 4B8GB+SSD, HA: Core 2026.8.3, Supervisor 2026.08.0, OS 18.2

In meinem Hobby habe ich die Stecker Deckenleuchte Dimmer(31) mit Ambiente 2b(20) getauscht, sowie Küche 2b(53) mit Ambiente3a (24). Namen und Nummern vom Kontaktplan Lichtsteuersystem in der Hobby Bedienungsanleitung.


## Funktionen

### Lichtsteuerung

Die aktuell hinterlegten Lichtkanäle sind:

| Licht | Typ |
|---|---|
| Dusche | Ein/Aus |
| Bad | Ein/Aus |
| Extra 1 | Ein/Aus |
| Extra 2 | Dimmbar |
| Extra 3 | Ein/Aus |
| Küche 1 | Ein/Aus |
| Küche 2 | Ein/Aus |
| Ambiente 1 | Ein/Aus |
| Ambiente 2 | Ein/Aus |
| Ambiente 3 | Ein/Aus |
| Bett 1 | Dimmbar |
| Bett 2 | Dimmbar |
| Decke | Dimmbar |
| Wand | Dimmbar |

Änderungen, die am originalen Hobby-Bedienpanel vorgenommen werden, können über die persistente BLE-Benachrichtigungsverbindung unmittelbar in Home Assistant übernommen werden.

### Temperaturen

Es stehen zwei Temperatursensoren zur Verfügung:

- **Innentemperatur**
- **Außentemperatur**

Seit Version **0.3.4** können beide Werte direkt in Home Assistant kalibriert werden.

Dazu gibt es zwei Konfigurationsentitäten:

- **Kalibrierung Innentemperatur**
- **Kalibrierung Außentemperatur**

Einstellbereich:

```text
-10.0 °C bis +10.0 °C
```

Schrittweite:

```text
0.1 °C
```

Die Berechnung erfolgt ausschließlich in Home Assistant:

```text
angezeigte Temperatur = HobbyConnect-Rohwert + Kalibrierwert
```

Der Kalibrierwert wird **nicht** per BLE an die Hobby-Steuerung zurückgeschrieben.

#### Beispiel

HobbyConnect meldet:

```text
24.8 °C
```

Ein Referenzthermometer zeigt:

```text
23.6 °C
```

Dann wird eingestellt:

```text
Kalibrierung Innentemperatur = -1.2 °C
```

Home Assistant zeigt anschließend:

```text
23.6 °C
```

### Wasserstand

Der Frischwasserstand wird als Home-Assistant-Sensor bereitgestellt.

Die Integration bildet die vom Hobby-System gelieferten Stufen auf folgende Werte ab:

```text
0 %
25 %
50 %
75 %
100 %
```

### 230-V-Verbraucher

Derzeit sind folgende Schalter integriert:

- **Fußbodenerwärmung**
- **Therme**

Sie erscheinen als normale Home-Assistant-`switch`-Entitäten.

### Betriebsmodus / Hauptschalter

Der Haupt-Betriebsmodus wird als Home-Assistant-`select` bereitgestellt.

Mögliche Zustände:

- **Fahrzeug Standby**
- **Nur Geräte**
- **Geräte und Lichter**

Aus Sicherheitsgründen werden nur während der Protokollanalyse bestätigte Fernschaltvorgänge gesendet.

Derzeit unterstützt:

```text
Fahrzeug Standby → Nur Geräte
Fahrzeug Standby → Geräte und Lichter
Nur Geräte       → Geräte und Lichter
Geräte und Lichter → Nur Geräte
```

Ein Fernschalten **in Fahrzeug Standby** ist derzeit bewusst nicht implementiert.

Wird Standby direkt am originalen Hobby-Panel gewählt, kann der gemeldete Zustand dennoch von Home Assistant übernommen werden.

## Synchronisation mit dem originalen Panel

Die Integration versucht, eine persistente BLE-Verbindung mit aktivierten Notifications zu halten.

Dadurch können Änderungen des Hobby-Systems zwischen den regulären Aktualisierungen unmittelbar verarbeitet werden.

```text
Originales Hobby-Panel
        ↓
HobbyConnect
        ↓ BLE Notification
Home Assistant
```

Bei unterstützten Schaltvorgängen funktioniert die Steuerung auch in Gegenrichtung:

```text
Home Assistant
        ↓ BLE-Befehl
HobbyConnect
        ↓
Hobby-System
```

Der tatsächlich vom Hobby-System zurückgemeldete Zustand hat Vorrang vor einem angenommenen Zustand.

## Bluetooth-Kommunikation

Die Integration verwendet den HobbyConnect-BLE-Service:

```text
eaffffff-ffff-ffff-ffff-fffffffffff0
```

und die Characteristic:

```text
00000001-0000-1000-8000-00805f9b34fb
```

Die Kommunikation erfolgt lokal über Home Assistants Bluetooth-Infrastruktur.

Es ist keine Cloud-Verbindung erforderlich.

## Voraussetzungen

- Home Assistant
- funktionierender Bluetooth-Adapter bzw. eine von Home Assistant nutzbare Bluetooth-Verbindung
- kompatibles HobbyConnect-System
- ausreichende Bluetooth-Reichweite zwischen Home Assistant und HobbyConnect

## Installation

### Manuelle Installation

Den Ordner

```text
custom_components/hobbyconnect
```

nach

```text
/config/custom_components/hobbyconnect/
```

kopieren.

Anschließend Home Assistant vollständig neu starten.

Die Installationsmethode über das Release habe ich noch nicht getestet.

Danach unter:

```text
Einstellungen
→ Geräte & Dienste
→ Integration hinzufügen
→ HobbyConnect
```

die Integration einrichten.

> Bei einem Update vorhandene HobbyConnect-Dateien durch die Dateien der neuen Version ersetzen und Home Assistant anschließend neu starten.

## Home-Assistant-Plattformen

Version 0.3.4 registriert folgende Plattformen:

```text
light
sensor
switch
select
number
```

### Sensoren

- Innentemperatur
- Außentemperatur
- Wasserstand

### Konfiguration

- Kalibrierung Innentemperatur
- Kalibrierung Außentemperatur

### Schalter

- Fußbodenerwärmung
- Therme

### Auswahl

- Betriebsmodus

### Lichter

Mehrere binäre und dimmbare Hobby-Lichtkanäle.

## Technische Hinweise

Die Integration fordert regelmäßig den aktuellen Systemzustand an und verarbeitet zusätzlich spontane BLE-Notifications.

Zu den von der Integration ausgewerteten Variablen gehören unter anderem:

```text
TEMP_IN
TEMP_OUT
WATER_LEVEL
HS_KEY_STATE
LIGHT_*
FLOOR_HEATER_ON
THERME_ON
```

Das HobbyConnect-Protokoll ist nicht öffentlich dokumentiert. Die Implementierung entstand durch kontrollierte Beobachtung und Tests der BLE-Kommunikation.

## Bekannte Einschränkungen

### Fahrzeug Standby

Der Zustand **Fahrzeug Standby** wird erkannt, wenn ihn das Hobby-System meldet.

Das aktive Fernschalten **in Standby** ist aktuell nicht freigegeben, da dafür während der bisherigen Protokolltests kein ausreichend sicher bestätigter Befehl gefunden wurde.

### Hardware-Kompatibilität

Die Entwicklung und Protokollanalyse erfolgte an einer konkreten HobbyConnect-Installation.

Andere Hobby-Modelle, Modelljahre oder Steuergeräte-Versionen können andere Kanalbelegungen oder ein abweichendes Verhalten aufweisen.

Kompatibilitätsberichte und reproduzierbare Testergebnisse sind willkommen.

### Undokumentiertes Protokoll

Die Implementierung basiert auf Reverse Engineering durch Beobachtung und kontrollierte Tests.

Eine vollständige Kompatibilität mit allen HobbyConnect-Versionen kann deshalb nicht garantiert werden.

## Versionshistorie

### 0.3.4

- Kalibrierung der Innentemperatur hinzugefügt
- Kalibrierung der Außentemperatur hinzugefügt
- Einstellbereich `-10.0 °C` bis `+10.0 °C`
- Schrittweite `0.1 °C`
- Kalibrierwerte werden dauerhaft in Home Assistant gespeichert
- Änderungen der Kalibrierung aktualisieren die Temperatursensoren ohne BLE-Schreibvorgang
- Home-Assistant-Plattform `number` ergänzt

### 0.3.3

- persistente BLE-Verbindung
- Verarbeitung spontaner HobbyConnect-Notifications
- schnellere Übernahme von Änderungen am originalen Hobby-Panel
- verbesserte Synchronisation zwischen Home Assistant und HobbyConnect

## Datenschutz und lokale Kommunikation

Die Integration selbst benötigt für die HobbyConnect-Kommunikation keinen Cloud-Dienst.

Bluetooth-Kommunikation und Kalibrierung erfolgen lokal innerhalb der Home-Assistant-Installation.

## Fehlerberichte und Beiträge

Bei Fehlerberichten sind insbesondere hilfreich:

- Hobby-Modell
- Modelljahr
- vorhandene HobbyConnect-/Steuergeräte-Version
- Home-Assistant-Version
- verwendete Bluetooth-Hardware
- relevante Home-Assistant-Logmeldungen
- genaue Beschreibung, welcher Schaltvorgang durchgeführt wurde

Bitte vor dem Veröffentlichen von Logs persönliche oder installationsspezifische Kennungen prüfen und gegebenenfalls entfernen.

## Haftungsausschluss

Dieses Projekt ist ein unabhängiges Community-Projekt.

Es steht in keiner Verbindung zu Hobby-Wohnwagenwerk Ing. Harald Striewski GmbH oder zu Herstellern der verwendeten Steuerelektronik und wird von diesen weder unterstützt noch bestätigt.

Die Nutzung erfolgt auf eigene Verantwortung.

Insbesondere bei elektrischen Verbrauchern sollten Schaltvorgänge zunächst unter Aufsicht an der eigenen Installation geprüft werden.

## Lizenz

Dieses Projekt steht unter der **MIT License**. Siehe [`LICENSE`](LICENSE).

---

# English

## Overview

**HobbyConnect for Home Assistant** integrates a compatible HobbyConnect system directly into Home Assistant via Bluetooth Low Energy.

Communication is local. No ESP32, MQTT broker or additional cloud service is required for this integration.

Depending on the installed HobbyConnect equipment, the integration exposes lighting channels, temperatures, water level, 230 V consumers and the main operating mode as native Home Assistant entities.

## Features

### Lighting

The currently configured lighting channels are:

| Light | Type |
|---|---|
| Shower | On/Off |
| Bathroom | On/Off |
| Extra 1 | On/Off |
| Extra 2 | Dimmable |
| Extra 3 | On/Off |
| Kitchen 1 | On/Off |
| Kitchen 2 | On/Off |
| Ambient 1 | On/Off |
| Ambient 2 | On/Off |
| Ambient 3 | On/Off |
| Bed 1 | Dimmable |
| Bed 2 | Dimmable |
| Ceiling | Dimmable |
| Wall | Dimmable |

Changes made on the original Hobby control panel can be reflected in Home Assistant immediately through the persistent BLE notification connection.

### Temperatures

Two temperature sensors are available:

- **Interior temperature**
- **Exterior temperature**

Since version **0.3.4**, both values can be calibrated locally in Home Assistant.

Two configuration entities are provided:

- **Interior temperature calibration**
- **Exterior temperature calibration**

Range:

```text
-10.0 °C to +10.0 °C
```

Step:

```text
0.1 °C
```

Calibration is performed entirely inside Home Assistant:

```text
displayed temperature = HobbyConnect raw value + calibration offset
```

The calibration value is **not** written back to the Hobby controller via BLE.

#### Example

HobbyConnect reports:

```text
24.8 °C
```

A reference thermometer shows:

```text
23.6 °C
```

Set:

```text
Interior temperature calibration = -1.2 °C
```

Home Assistant will then display:

```text
23.6 °C
```

### Water Level

The fresh-water level is exposed as a Home Assistant sensor.

The integration maps the levels reported by the Hobby system to:

```text
0 %
25 %
50 %
75 %
100 %
```

### 230 V Consumers

The following switches are currently integrated:

- **Floor heating**
- **Boiler / Therme**

They are exposed as normal Home Assistant `switch` entities.

### Operating Mode / Main Switch

The main operating mode is exposed as a Home Assistant `select`.

Possible states:

- **Vehicle Standby**
- **Devices only**
- **Devices and lights**

For safety, only remote transitions that were confirmed during protocol analysis are sent.

Currently supported:

```text
Vehicle Standby    → Devices only
Vehicle Standby    → Devices and lights
Devices only       → Devices and lights
Devices and lights → Devices only
```

Remote switching **into Vehicle Standby** is intentionally not implemented at this time.

If Standby is selected on the original Hobby panel, the reported state can still be reflected in Home Assistant.

## Original Panel Synchronization

The integration attempts to keep a persistent BLE connection with notifications enabled.

This allows changes reported by the Hobby system to be processed immediately between regular refresh cycles.

```text
Original Hobby panel
        ↓
HobbyConnect
        ↓ BLE notification
Home Assistant
```

For supported commands, control also works in the opposite direction:

```text
Home Assistant
        ↓ BLE command
HobbyConnect
        ↓
Hobby system
```

The state actually reported by the Hobby system takes precedence over an assumed state.

## Bluetooth Communication

The integration uses the HobbyConnect BLE service:

```text
eaffffff-ffff-ffff-ffff-fffffffffff0
```

and the characteristic:

```text
00000001-0000-1000-8000-00805f9b34fb
```

Communication is local through Home Assistant's Bluetooth infrastructure.

No cloud connection is required.

## Requirements

- Home Assistant
- a working Bluetooth adapter or Bluetooth connection usable by Home Assistant
- a compatible HobbyConnect system
- sufficient Bluetooth range between Home Assistant and HobbyConnect

## Installation

### Manual Installation

Copy the folder

```text
custom_components/hobbyconnect
```

to

```text
/config/custom_components/hobbyconnect/
```

Then restart Home Assistant completely.


Installing the release directly in HA has not been tested so far.
Afterwards go to:

```text
Settings
→ Devices & services
→ Add integration
→ HobbyConnect
```

and configure the integration.

> When updating, replace the existing HobbyConnect files with the files from the new version and restart Home Assistant afterwards.

## Home Assistant Platforms

Version 0.3.4 registers the following platforms:

```text
light
sensor
switch
select
number
```

### Sensors

- Interior temperature
- Exterior temperature
- Water level

### Configuration

- Interior temperature calibration
- Exterior temperature calibration

### Switches

- Floor heating
- Boiler / Therme

### Select

- Operating mode

### Lights

Multiple binary and dimmable Hobby lighting channels.

## Technical Notes

The integration periodically requests the current system state and additionally processes spontaneous BLE notifications.

Variables evaluated by the integration include, among others:

```text
TEMP_IN
TEMP_OUT
WATER_LEVEL
HS_KEY_STATE
LIGHT_*
FLOOR_HEATER_ON
THERME_ON
```

The HobbyConnect protocol is not publicly documented. The implementation was derived from controlled observation and testing of the BLE communication.

## Known Limitations

### Vehicle Standby

The **Vehicle Standby** state is detected when it is reported by the Hobby system.

Actively switching **into Standby** remotely is currently disabled because no sufficiently confirmed safe command for this transition was identified during the protocol tests performed so far.

### Hardware Compatibility

Development and protocol analysis were performed on a specific HobbyConnect installation.

Other Hobby models, model years or control-unit revisions may use different channel assignments or behaviour.

Compatibility reports and reproducible test results are welcome.

### Undocumented Protocol

The implementation is based on reverse engineering through observation and controlled testing.

Full compatibility with every HobbyConnect version therefore cannot be guaranteed.

## Version History

### 0.3.4

- Added interior temperature calibration
- Added exterior temperature calibration
- Calibration range from `-10.0 °C` to `+10.0 °C`
- Calibration step of `0.1 °C`
- Calibration values are stored persistently in Home Assistant
- Calibration changes update the temperature sensors without a BLE write
- Added the Home Assistant `number` platform

### 0.3.3

- Persistent BLE connection
- Processing of spontaneous HobbyConnect notifications
- Faster reflection of changes made on the original Hobby control panel
- Improved synchronization between Home Assistant and HobbyConnect

## Privacy and Local Communication

The integration itself does not require a cloud service for HobbyConnect communication.

Bluetooth communication and temperature calibration take place locally within the Home Assistant installation.

## Issues and Contributions

Useful information for issue reports includes:

- Hobby model
- model year
- installed HobbyConnect/control-system version
- Home Assistant version
- Bluetooth hardware used
- relevant Home Assistant log messages
- an exact description of the action that was performed

Before publishing logs, please check for personal or installation-specific identifiers and remove them if necessary.

## Disclaimer

This is an independent community project.

It is not affiliated with, endorsed by or supported by Hobby-Wohnwagenwerk Ing. Harald Striewski GmbH or the manufacturers of the installed control electronics.

Use this integration at your own risk.

Especially when controlling electrical consumers, verify the behaviour of your own installation under supervision before relying on automations.

## License

This project is licensed under the **MIT License**. See [`LICENSE`](LICENSE).

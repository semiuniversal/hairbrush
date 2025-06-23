
# Duet Endstop Monitoring Guide

This document describes how to monitor and interpret endstop (limit switch) status on a Duet 2 WiFi board running RepRapFirmware 3.4.6, using the configuration below.

## 📄 Current Endstop Configuration (from `config.g`)

```gcode
M574 X1 S1 P"!xstop"           ; X min, active-low
M574 Y1 S1 P"!ystop"           ; Y min, active-low
M574 Z2 S1 P"!zstop"           ; Z max, active-low

M208 X0 Y0 Z0 S1               ; Set axis minima
M208 X1200 Y1500 Z300 S0       ; Set axis maxima (adjust to actual)
```

### Interpretation

| Axis | Endstop Position | Pin     | Logic   | M119 Output when TRIGGERED |
|------|------------------|---------|---------|-----------------------------|
| X    | Min              | xstop   | Inverted (active-low) | `X: at min stop` |
| Y    | Min              | ystop   | Inverted (active-low) | `Y: at min stop` |
| Z    | Max              | zstop   | Inverted (active-low) | `Z: at max stop` |

- `!` = active-low logic (signal reads `low` when pressed)
- `S1` = digital input

## 🔍 How to Query Endstop Status

Send the following G-code command over the HTTP API or serial connection:

```gcode
M119
```

### Using HTTP (Python Example)

```python
import requests

DUET_IP = "192.168.1.xxx"
session = requests.Session()

# Connect to Duet (no password)
session.get(f"http://{DUET_IP}/rr_connect?password=")

# Query endstops
session.get(f"http://{DUET_IP}/rr_gcode?gcode=M119")
r = session.get(f"http://{DUET_IP}/rr_reply")
print(r.text.strip())
```

## 🧾 Sample Responses

- All endstops untriggered:
  ```
  Endstops - X: not stopped, Y: not stopped, Z: not stopped
  ```

- X and Y triggered (e.g., after homing):
  ```
  Endstops - X: at min stop, Y: at min stop, Z: not stopped
  ```

- Z at max (e.g., Z fully raised):
  ```
  Endstops - X: not stopped, Y: not stopped, Z: at max stop
  ```

## 🧠 Notes

- `M119` reflects **configured endstops only**; if an axis has no endstop defined, it will report `no endstop`.
- Inverted logic requires normally closed switches or pull-up resistors.
- You can safely poll `M119` during homing or troubleshooting.

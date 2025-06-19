
# 🖨️ G-Code & M-Code Reference – CoreXY-H Dual-Airbrush Plotter

Firmware: **RepRapFirmware 3.4.6**  
Controller: **Duet 2 WiFi**  
Motion System: **CoreXY-H**  
Mode: **CNC**

---

## 🧭 Machine Setup & Homing

```gcode
G28         ; Home all axes
G28 X Y     ; Home X and Y only
G28 Z       ; Home Z only
```

---

## 🎯 Motion & Positioning

```gcode
G0 Xnnn Ynnn Znnn Fnnn   ; Rapid move to position at feedrate F
G1 Xnnn Ynnn Znnn Fnnn   ; Linear move (used for plotting)
G90                     ; Use absolute positioning
G91                     ; Use relative positioning
G92 X0 Y0 Z0            ; Set current position to (0,0,0)
```

---

## 🧰 Coordinate System & Units

```gcode
G21   ; Set units to mm
G20   ; Set units to inches
G90   ; Absolute positioning (default)
G91   ; Relative positioning
```

---

## 🖨️ Tool / Plotter Configuration

### Define triggers (in `config.g`):

```gcode
M950 S0 C"exp.heater3"    ; Servo A (trigger A)
M950 S1 C"exp.heater4"    ; Servo B (trigger B)
```

### Define air solenoids (via GPIO):

```gcode
M950 P0 C"exp.heater5"    ; Solenoid A
M950 P1 C"exp.heater6"    ; Solenoid B
M42 P0 S1                 ; Turn on solenoid A
M42 P0 S0                 ; Turn off solenoid A
M42 P1 S1                 ; Turn on solenoid B
M42 P1 S0                 ; Turn off solenoid B
```

---

## 🎮 Servo Control (Airbrush trigger actuation)

```gcode
M280 P0 Snnn   ; Servo A to angle nnn (0–180)
M280 P1 Snnn   ; Servo B to angle nnn
```

Example:

```gcode
M280 P0 S90    ; Pull trigger
M280 P0 S0     ; Release trigger
```

---

## 🔧 Mode Selection

```gcode
M451   ; Set CNC mode
```

---

## 💨 Airbrush Head Control (Optional)

```gcode
M3       ; Turn on primary air (if mapped)
M5       ; Turn off all air
```

---

## 🔍 Status & Diagnostics

```gcode
M115      ; Report firmware version
M122      ; Detailed diagnostics
M119      ; Endstop status
```

---

## 🧪 Example Paint Stroke (Head A)

```gcode
G90
G1 X10 Y10 F3000        ; Move to start
M42 P0 S1               ; Turn on air A
M280 P0 S90             ; Pull trigger
G1 X100 Y10 F1500       ; Paint stroke
M280 P0 S0              ; Release trigger
M42 P0 S0               ; Turn off air
```

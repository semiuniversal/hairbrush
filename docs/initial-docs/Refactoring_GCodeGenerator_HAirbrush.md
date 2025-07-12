
# Refactoring Guide: GCodeGenerator for H.Airbrush Plotter

This guide provides **line-by-line upgrade instructions** to align the `GCodeGenerator` with the canonical Duet G-code behavior described in `Duet Plotter G-Code Reference v2`.

---

## 1. Remove Tool Offsets from Motion

**Current:**
```python
self.output_lines.append("G0 X{:.2f} Y{:.2f} F3000".format(x + offset_x, y + offset_y))
```

**Replace with:**
```python
self.output_lines.append("G0 X{:.2f} Y{:.2f} F3000".format(x, y))
```

**Also remove:**
```python
offset_x, offset_y = ...
```

🟡 *Let the firmware handle tool offsets via tfree/tpost scripts.*

---

## 2. Issue Tool Selection via `T` Commands

**Before each path**, insert:
```python
if brush_index != self.current_brush:
    self.output_lines.append(f"T{brush_index} ; Select {brush}")
    self.current_brush = brush_index
```

🔵 *Keeps tool changes in sync with motion logic.*

---

## 3. Remove Redundant Homing

**In `add_header()`**, remove:
```python
"G28 ; Home all axes",
"G92 X0 Y0 Z0 ; Set current position as origin",
```

🟢 *Homing is already handled later in initialization; duplicate resets cause confusion.*

---

## 4. Avoid Applying G92 to XY After Homing

**Do not include:**
```python
G92 X0 Y0
```

🔴 *Only allow Z-axis resets where explicitly needed. The firmware handles X/Y via `G92` in `homeall.g`.*

---

## 5. Make Brush Activation Stateless

Before every air-on command, add:

```python
self.output_lines.append(f"M42 P{brush_index} S0 ; Ensure {brush} air off before starting")
self.output_lines.append(f"M280 P{brush_index} S0 ; Ensure trigger off")
```

Then follow with:
```python
self.output_lines.append(f"M42 P{brush_index} S1 ; Air on")
self.output_lines.append(f"M280 P{brush_index} S{servo_angle} ; Trigger on")
```

🟤 *Prevents contamination from residual state.*

---

## 6. Add Macro Support (Optional)

Add this class flag:
```python
self.use_macros = False
```

Wrap brush commands:
```python
if self.use_macros:
    self.output_lines.append(f"M98 P\"{brush}_air_on.g\"")
    self.output_lines.append(f"M98 P\"{brush}_flow_on.g\"")
else:
    ...
```

⚪ *Allows external macro integration later with no core logic changes.*

---

## 7. Clarify `generate_gcode()` output

Insert tool comments:
```python
self.output_lines.append(f"; Using brush: {brush} (tool {brush_index})")
```

Add at beginning of each path section.

---

## 8. Don’t Embed Tool Selection in `add_path()`

✅ *Only do tool changes in `add_path_with_attributes()`.*  
❌ Do not change tool state deep in the stroke loop.

---

## 9. Safe Travel Movement

Add guard clause before XY motion:
```python
self.output_lines.append("G0 Z{:.2f} F3000".format(travel_z))
self.output_lines.append("M400 ; Wait for Z up")
```

Always raise Z before moving XY.

---

## 10. Homing Logic Should Be Configurable

Allow skipping homing for live control sessions:
```python
if not self.skip_homing:
    self.output_lines.append("G28 ; Home")
```

🟢 Can be set using `.set_skip_homing(True)`

---

This staged guide ensures your G-code generator conforms to clean, safe, and modular practices while preserving compatibility with Duet firmware expectations.

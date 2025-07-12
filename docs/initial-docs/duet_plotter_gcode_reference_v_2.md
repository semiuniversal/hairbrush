# Duet Plotter G-Code Reference v2

## Purpose

This reference defines the G-code behavior expected by the H.Airbrush dual-airbrush CoreXY plotter system. It is structured to align with CNC and 3D printer conventions, with stateless, device-independent motion logic. The system supports Brush A (Black, Tool 0) and Brush B (White, Tool 1) as interchangeable tools, each with a separate air/flow control mechanism.

## Conventions

- **Absolute Positioning** is used (`G90`).
- **Tool Offsets are applied via tpost/tfree scripts**, not via `G10`.
- **No tool should alter the logical coordinate system.**
- The G-code generator assumes a flat, rectangular working envelope starting at logical X0 Y0.
- **Z heights must be explicitly specified in the G-code.** Tool changes do not imply Z movement.
- **Air and paint flow are controlled separately** via dedicated commands.

## Tool Selection

Use:

- `T0` — Select Brush A
- `T1` — Select Brush B

These commands trigger physical movement to compensate for head offset using:

- `tfree0.g`, `tpost0.g` — No offset
- `tfree1.g`, `tpost1.g` — Offset Tool B: +X100, -Y25 from Tool A

Tool offsets are implemented *as real motion*, not via coordinate shifts (`G10`). This ensures consistency with physical layout and toolpath expectations.

## Brush Activation

Brush heads have two actuation channels:

- **Air solenoid (on/off):**
  - `M42 P0 S1` / `M42 P0 S0` — Brush A air on/off
  - `M42 P1 S1` / `M42 P1 S0` — Brush B air on/off
- **Servo paint flow (trigger angle):**
  - `M280 P0 Snn` — Set Brush A servo angle (10–180°)
  - `M280 P1 Snn` — Set Brush B servo angle

**Important:** G-code must explicitly enable air and flow before drawing.

## Z Heights

- **Safe travel height:** `Z10` mm
- **Drawing range:** `Z1.0`–`Z15.0` mm depending on stroke width and opacity
- **Z must be moved safely before any XY motion.**

## Homing Sequence (via `G28`)

- Homes Z to max (`G1 H1 Z100`) then backs off.
- Moves Y +150 before homing X to avoid steppers.
- Applies X and Y endstop sequences.
- Sets logical origin to `X81 Y120` → declared as `X0 Y0`

## Reserved Macros

These are callable in user code or via G-code generator:

- `a-air-on.g`, `a-air-off.g`
- `b-air-on.g`, `b-air-off.g`

Each macro enables or disables the correct solenoid with safety logic (e.g., shutting off the opposite color).

## Motion Limits

These are set in firmware (`config.g`) to match the physical working envelope:

```gcode
M208 X0 Y0 Z0 S1        ; Min (logical origin)
M208 X695 Y1080 Z84 S0  ; Max (excludes parking offsets)
```

## Coordinate System and Positioning

- **All coordinates are relative to Tool A**.
- Tool changes shift the actual head position *but not* the reported logical coordinates.
- The drawing should be registered so that the *lower-left corner of the paper aligns with Brush A’s origin*.

## Best Practices

- Always move to Z-safe height before tool changes.
- Set Z explicitly after each move.
- Never apply `G92` outside of homing sequences.
- Avoid `G10` tool offsets.
- Use macros to activate air and flow — never embed this logic inside tool selection.

## Known Limitations

- Tool switches must be carefully timed. Extraneous `T0`/`T1` commands will cause unintended motion.
- The airbrush flow servo cannot currently confirm position. Use visible housing for calibration.

## Example G-Code Snippet

```gcode
G28                    ; Home machine
T0                     ; Select Brush A
M42 P0 S1              ; Turn on air
G0 Z10 F3000           ; Travel height
G0 X50 Y50 F3000       ; Move to start
G1 Z2.0 F1500          ; Drawing height
M280 P0 S170           ; Flow on
G1 X100 Y50 F300       ; Draw
M280 P0 S0             ; Flow off
M42 P0 S0              ; Air off
```

---

This reference should be bundled with any G-code generator or toolpath planner for the H.Airbrush system. Avoid assumptions about brush behavior — all logic must be explicit and mechanical state transitions must be controlled with precision.


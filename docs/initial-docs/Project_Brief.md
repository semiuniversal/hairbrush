
# 🎨 Dual-Airbrush Plotter Project Brief

## 🧠 Intent and Vision

The software is designed to control a **custom-built dual-airbrush CoreXY plotter** driven by a **Duet 2 WiFi board**. It provides an intuitive workflow for artists who work in vector graphics (e.g., SVGs from Inkscape) to produce high-precision, expressive paintings using black and white ink channels. The system abstracts away the technical details of G-code and machine control, offering both beginner-friendly and power-user modes.

Ultimately, this aims to be both:
- A **general-purpose open source painting plotter controller**
- A potentially **commercially viable, artist-ready creative tool**

---

## 🧩 Core Software Components

### 1. 🔌 Inkscape Extension

**Goal**: Let users export multi-layer SVGs as Duet-compatible G-code with minimal configuration.

**Inputs (via `.inx` GUI)**:
- Layer names for Brush A (Black) and Brush B (White)
- Z-height (airbrush distance to paper)
- Brush offsets in X and Y
- Feedrate (mm/min)
- Output G-code file path

**Backend Implementation (`inkex`)**:
- Traverses SVG DOM to extract `<path>` elements by layer
- Uses Inkscape’s transformation matrix to flatten all paths
- Future support for:
  - `stroke-width` → line width modulation
  - `stroke-opacity` → flow intensity
  - `transform` attributes → canvas positioning
- Emits G-code to file using a command mapping template

---

### 2. 🛠 G-code Backend Generator

**Goal**: Convert parsed paths into Duet-friendly G-code.

**Command Template** (`command_templates.yaml`):

```yaml
brush_a:
  offset: [0, 0]
  air_on: "M42 P0 S1"
  air_off: "M42 P0 S0"
  paint_on: "M280 P0 S90"
  paint_off: "M280 P0 S0"

brush_b:
  offset: [50, 50]
  air_on: "M42 P1 S1"
  air_off: "M42 P1 S0"
  paint_on: "M280 P1 S90"
  paint_off: "M280 P1 S0"
```

**Output Logic**:
- Inserts `G0/G1` commands with `Z` height control
- Wraps strokes with:
  - Air on/off commands
  - Servo trigger pull/release
- Applies per-brush offsets transparently

---

### 3. 🌐 Telnet Controller (Optional)

**Goal**: Send G-code to Duet in real time, without needing Duet Web Control (DWC).

**Features**:
- Python tool using `telnetlib`
- Streams `.gcode` file line by line with delay/retry logic
- Manual jog and command input modes for:
  - Brush test
  - Priming
  - Position calibration

---

### 4. 🧪 Calibration & Manual Mode (Optional GUI)

**Goal**: Assist in setup, alignment, and troubleshooting.

**Features**:
- Jog X/Y/Z using arrow buttons or text input
- Trigger individual brush actions (air/paint)
- Test brush offset accuracy
- Optionally use a laser pointer for alignment

**Tooling**:
- Implement in Python (Tkinter or PyQt)
- Communicate via Telnet or HTTP to Duet

---

## 🔄 Workflow Summary

1. **Create Artwork in Inkscape**
   - Two labeled layers: `black`, `white`

2. **Export G-code**
   - Using `Extensions > Export Dual Airbrush G-code`
   - Generates `.gcode` file with custom Duet commands

3. **Send to Machine**
   - Via Duet Web Control (manually)
   - Or via the optional Python Telnet sender

4. **Observe / Calibrate**
   - Optionally use GUI for Z-height, brush offset, stroke test, etc.

---

## 💡 Implementation Notes

- Built to allow **hardware abstraction**: Duet, Marlin, GRBL supported via config.
- Modular and readable codebase, structured for future open-source release.
- Starts with **black/white**, but designed for expansion to **multi-material (e.g. CMYK)**.
- Emphasizes **dry-run, simulation, and separation of concerns** during early hardware development.


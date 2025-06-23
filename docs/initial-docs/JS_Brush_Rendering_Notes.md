
# 🎨 Brush-Based G-code Rendering in JavaScript

This guide summarizes how to track and render dual-airbrush G-code in a JS canvas viewer such as `gcode-viewer` by ScorchWorks.

---

## 🧠 Brush Activation Markers

G-code commands signal which brush is active:

- `M42 P0 S1` → Air ON for Brush A
- `M42 P1 S1` → Air ON for Brush B
- `M280 P0 S180` → Trigger Brush A
- `M280 P1 S180` → Trigger Brush B

Track the most recent `P0` or `P1` to determine the active brush.

---

## ✅ JavaScript Parsing Example

```javascript
let currentBrush = 'A';  // Default

const match = line.match(/M(42|280)\s+P(\d+)/);
if (match) {
  const brushIndex = parseInt(match[2], 10);
  currentBrush = brushIndex === 0 ? 'A' : 'B';
}
```

---

## 🖌 Toolpath Coloring Rules

Set `strokeStyle` based on `currentBrush`:

```javascript
if (currentBrush === 'A') {
  ctx.strokeStyle = '#000000'; // Black
} else {
  ctx.strokeStyle = '#FFFFFF'; // White
  ctx.shadowColor = '#888';    // Outline for visibility
  ctx.shadowBlur = 2;
}
```

This allows black/white strokes to render distinctly even on white paper backgrounds.

---

## 🔍 Optional Comment-Based Parsing

If your G-code includes lines like:
```gcode
; Brush: A
```

You can parse them with:

```javascript
if (line.includes("Brush: A")) currentBrush = 'A';
if (line.includes("Brush: B")) currentBrush = 'B';
```

---

Use this as part of your G-code visualizer to provide intuitive feedback on brush usage, tool changes, and painted path differentiation.

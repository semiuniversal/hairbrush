
# 🧠 Duet Flask Controller – Design Notes

This document outlines key recommendations and best practices for building a Flask-based web controller that streams G-code to a Duet 2 WiFi board over Telnet, with real-time execution awareness.

---

## 🎯 Objective

Ensure that the web application:
- Sends G-code commands reliably to the Duet board via Telnet.
- Knows **when a physical move or action has been completed**.
- Can optionally query position or status in real-time for UI display or diagnostics.

---

## ✅ Core Recommendation: Use `M400`

### 🔹 `M400` – Wait for Motion to Complete

Send this command after each block of motion-related G-code:
```gcode
M400 ; Wait for all buffered moves to complete
```

Duet will respond only **after** all motion has physically finished.

---

## 🔁 Suggested Protocol Flow

1. Open Telnet connection to Duet on port `23`.
2. Send G-code lines:
   ```gcode
   G0 X100 Y100
   G1 Z2.0
   M280 P0 S90
   G1 X200 Y200
   M280 P0 S0
   M400
   ```
3. Read Telnet responses until an "ok" or newline is returned.
4. Proceed with the next command set only after confirmation.

---

## 🧪 Optional: Use `M114` to Query Position

For UI or diagnostics, send:
```gcode
M114 ; Request current position
```

Duet will return something like:
```
X:200.0 Y:200.0 Z:2.0 E:0.0 Count 20000 20000 800
```

You can use this in polling mode to update a real-time display of machine position.

---

## ⚠️ Important Constraints

- Duet **does not push events**: there is no interrupt or asynchronous signal when motion completes.
- Telnet communication is **stateless** and **line-buffered**.
- You must **poll or wait** explicitly for `M400` or use `M114` to monitor status.

---

## 🧰 Suggested Python Functions

### Send G-code and wait for result:
```python
def send_and_wait(sock, gcode):
    sock.write((gcode + "\n").encode())
    sock.flush()
    while True:
        response = sock.readline().decode().strip()
        if "ok" in response or response == "":
            break
```

### Wait for `M400`:
```python
def wait_for_m400(sock):
    sock.write(b"M400\n")
    while True:
        response = sock.readline().decode().strip()
        if "ok" in response or response == "":
            break
```

---

## 🧱 Summary

- Use `M400` to synchronize on motion completion.
- Use `M114` for passive polling of position (if desired).
- Do not rely on implicit timing or response buffering.
- All coordination logic must be managed by your controller.

---

These guidelines will help ensure safe, responsive control of your airbrush plotter through a browser-based interface.



---

## 🧠 Best Practice: Where to Insert `M400`?

There are two possible approaches to inserting `M400`:

### ✅ Option 1: Insert in G-code Generation Phase

**Advantages:**
- G-code files are self-contained and safe to execute independently (e.g. via Duet Web Control).
- Easier offline debugging and testing.
- Guarantees motion-complete behavior even without a smart controller.

**Disadvantages:**
- Reduced flexibility at runtime.
- May include unnecessary waits that reduce performance.

### ✅ Option 2: Insert in Python Controller (Runtime)

**Advantages:**
- Greater control over timing and grouping.
- Cleaner G-code files for other use cases (e.g. preview).
- Dynamic `M400` injection allows batching or parallel planning.

**Disadvantages:**
- Easy to forget to call `M400`, leading to desynchronization.
- More complex G-code interpretation logic required in controller.

### ✅ Recommended Hybrid Strategy

Use a **hybrid approach**:
- Insert `M400` **after each complete stroke or major motion block** in the G-code generator.
- Let the Python controller **recognize and act on `M400` commands** as blocking synchronization points.
- Allow the controller to optionally **inject additional `M400`** when needed for live-streamed or segmented operations.

This provides:
- Safe standalone G-code
- Flexible and intelligent runtime behavior


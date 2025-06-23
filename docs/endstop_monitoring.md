# Endstop Monitoring Feature

This document describes the endstop monitoring feature implemented in the H.Airbrush web controller.

## Overview

The endstop monitoring feature allows users to monitor the status of the machine's limit switches (endstops) in real-time. This is useful for:

- Troubleshooting homing issues
- Verifying endstop functionality
- Monitoring machine position during operation
- Ensuring safety during manual movements

## Implementation Details

### Backend

The endstop status is queried by sending the `M119` G-code command to the Duet board via the HTTP API. The response is parsed and returned to the client.

```python
# Example M119 response
"Endstops - X: not stopped, Y: not stopped, Z: not stopped"
```

### Frontend

The frontend displays the endstop status using color-coded badges:
- Green: Not triggered
- Red: Triggered (at min/max stop)
- Yellow: Warning or unknown state
- Gray: Loading/checking status

The status is automatically polled every 5 seconds and can be manually refreshed using the "Refresh" button.

## Usage

1. Navigate to the Machine Control page
2. Connect to the Duet board
3. The endstop status will be displayed in the "Endstop Status" section
4. Click the "Refresh" button to manually update the status

## Troubleshooting

If endstop status shows as "Error" or "Parse error", check the following:
- Ensure the Duet board is properly connected
- Verify the firmware version is compatible (RRF 3.4.6+)
- Check the browser console for any JavaScript errors
- Look at the server logs for any backend errors

## Configuration

The endstop configuration is defined in the Duet's `config.g` file. The current configuration is:

```gcode
M574 X1 S1 P"!xstop"           ; X min, active-low
M574 Y1 S1 P"!ystop"           ; Y min, active-low
M574 Z2 S1 P"!zstop"           ; Z max, active-low
```

For more details on endstop configuration, see the [Duet Endstop Monitoring Guide](docs/initial-docs/Duet_Endstop_Monitoring_Guide.md). 
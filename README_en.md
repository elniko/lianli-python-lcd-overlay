# LCD Overlay

Module for displaying sensor data (CPU, GPU, RAM, FAN) over video on Lian Li 8.8" Universal Screen.

## Project Structure

```
lcd-overlay/
├── lcd_overlay/           # Main module
│   ├── __init__.py
│   ├── colors.py          # Color and gradient parsing
│   ├── config.py          # Configuration loading/saving
│   ├── sensors.py        # Sensor data collection
│   ├── renderer.py       # Ring and progress bar rendering
│   ├── overlay.py        # Overlay assembly
│   ├── stream.py         # H264 streaming and LCD communication
│   └── configs/
│       └── default.json  # Default configuration
├── Linx/                  # LCD communication library
│   └── linx.py
└── run_overlay.py        # Entry point
```

## Installation

1. Install dependencies:
```bash
pip3 install pillow psutil pynvml --break-system-packages
```

2. Connect Lian Li 8.8" Universal Screen via USB

## Running

```bash
cd /home/nicolas/lcd-overlay
sudo python3 run_overlay.py
```

With custom config:
```bash
sudo python3 run_overlay.py -c /path/to/config.json
```

## Configuration

JSON config file. Default location: `lcd_overlay/configs/default.json`

### Example Config

```json
{
  "video": "/path/to/video.h264",
  "background": "/path/to/background.png",
  "positions": {
    "cpu": 30,
    "gpu": 335,
    "ram_fan": 645
  },
  "fan_max": {
    "cpu": 2057,
    "gpu": 3260
  },
  "colors": {
    "cpu_ring": {
      "background": "#ffffff",
      "border": "#331933",
      "separator": "transparent",
      "fill": "cyan_magenta"
    },
    "gpu_ring": {
      "background": "#ffffff",
      "border": "#331933",
      "separator": "transparent",
      "fill": "cyan_magenta"
    },
    "ram_ring": {
      "background": "#ffffff",
      "border": "#331933",
      "separator": "transparent",
      "fill": "cyan_magenta"
    },
    "cpu_temp": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "transparent",
      "style": "segmented",
      "fill": "cyan_magenta"
    },
    "gpu_temp": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "transparent",
      "style": "segmented",
      "fill": "cyan_magenta"
    },
    "cpu_clock": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "transparent",
      "style": "solid",
      "fill": "#ff00fe"
    },
    "gpu_clock": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "transparent",
      "style": "solid",
      "fill": "#ff00fe"
    },
    "cpu_fan": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "transparent",
      "style": "segmented",
      "fill": "cyan_magenta"
    },
    "gpu_fan": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "transparent",
      "style": "segmented",
      "fill": "cyan_magenta"
    },
    "text": {
      "title": "#ffffff",
      "data": "#ffffff"
    },
    "separator": "#331933"
  }
}
```

### Configuration Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `video` | string | Path to H264 file. Empty = overlay only |
| `background` | string | Path to PNG background. Empty = transparent (with video) or black (without video) |

### Positions (overlay vertical positions)

| Parameter | Type | Description |
|-----------|------|-------------|
| `cpu` | int | CPU monitor Y position (default: 30) |
| `gpu` | int | GPU monitor Y position (default: 335) |
| `ram_fan` | int | RAM/FAN section Y position (default: 645) |

### Fan Max Values

| Parameter | Type | Description |
|-----------|------|-------------|
| `cpu` | int | CPU fan max RPM (default: 2057) |
| `gpu` | int | GPU fan max RPM (default: 3260) |

### Colors

#### Rings (circular charts)

Each ring section (`cpu_ring`, `gpu_ring`, `ram_ring`) contains:
- `background` - segment background color (#ffffff)
- `border` - outer border color (#331933)
- `separator` - divider line color (transparent = no lines)
- `fill` - fill color (gradient or solid)

#### Progress Bars

Each progress bar (`cpu_temp`, `gpu_temp`, `cpu_clock`, `gpu_clock`, `cpu_fan`, `gpu_fan`) contains:
- `background` - bar background color (transparent = transparent)
- `border` - bar border color
- `separator` - gap color between segments (transparent = no gaps)
- `style` - `segmented` (with dividers) or `solid` (continuous)
- `fill` - fill color (gradient or solid)

### Fill (Unified Fill System)

The `fill` parameter is unified for all elements and accepts:

**Gradient Presets:**
- `"cyan_magenta"` - cyan → blue → purple → magenta (6 colors)
- `"green_red"` - green → yellow → orange → red (5 colors)

**Solid Color (hex):**
- `"#ff00fe"`
- `"#00ff00"`

**Custom Gradient:**
```json
"fill": ["#00c8f8", "#ff00fe", "#00ff00"]
```

### Color Formats

Supported formats:
- Hex: `"#ff0000"`, `"#ff0000ff"`
- Named: `"white"`, `"black"`, `"red"`, `"green"`, `"blue"`, `"cyan"`, `"magenta"`, `"yellow"`, `"orange"`
- Transparent: `"transparent"`

## Operation Modes

1. **Video + overlay** - video plays in background, overlays on top
2. **Overlay only** - overlays only on black background (set `video: ""` in config)

## Sensors

### CPU
- Load % - ring chart
- Temperature °C - progress bar
- Clock MHz - progress bar

### GPU (requires NVML)
- Load % - ring chart
- Temperature °C - progress bar
- Clock MHz - progress bar
- Fan RPM - progress bar

### RAM
- Usage % - ring chart

### FAN
- CPU FAN RPM - progress bar
- GPU FAN RPM - progress bar

## Demo

```bash
# Run with default settings
sudo python3 run_overlay.py

# Overlay-only mode (no video)
# In config: "video": ""

# With custom config
sudo python3 run_overlay.py -c /path/to/my_config.json
```

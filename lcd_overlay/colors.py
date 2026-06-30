"""Color parsing and gradient definitions for LCD overlay."""

from typing import Union, List, Tuple, Dict, Any

ColorValue = Union[str, List[str], Tuple[int, int, int], Tuple[int, int, int, int]]

TRANSPARENT = "transparent"

GRADIENTS = {
    "cyan_magenta": [
        (0x00, 0xc8, 0xf8),
        (0x3d, 0x9b, 0xde),
        (0x7a, 0x71, 0xc6),
        (0xb6, 0x46, 0xae),
        (0xf4, 0x1a, 0x95),
        (0xff, 0x00, 0xfe),
    ],
    "green_red": [
        (0x00, 0xff, 0x00),
        (0x7f, 0xff, 0x00),
        (0xff, 0xff, 0x00),
        (0xff, 0x7f, 0x00),
        (0xff, 0x00, 0x00),
    ],
}

SOLID_COLORS = {
    "white": (255, 255, 255, 255),
    "black": (0, 0, 0, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "cyan": (0, 255, 255, 255),
    "magenta": (255, 0, 255, 255),
    "yellow": (255, 255, 0, 255),
    "orange": (255, 165, 0, 255),
}


def parse_hex(hex_str: str) -> Tuple[int, int, int, int]:
    """Parse hex color string to RGBA tuple."""
    hex_str = hex_str.lstrip('#')
    
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return (r, g, b, 255)
    elif len(hex_str) == 8:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        a = int(hex_str[6:8], 16)
        return (r, g, b, a)
    else:
        raise ValueError(f"Invalid hex color: #{hex_str}")


def parse_color(color: str) -> Tuple[int, int, int, int]:
    """Parse a color string to RGBA tuple.
    
    Supports:
    - Hex colors: "#ff0000", "#ff0000ff"
    - Named colors: "white", "black", "red", etc.
    - Special: "transparent"
    """
    if color == TRANSPARENT:
        return (0, 0, 0, 0)
    
    if color.startswith("#"):
        return parse_hex(color)
    
    color_lower = color.lower()
    if color_lower in SOLID_COLORS:
        return SOLID_COLORS[color_lower]
    
    raise ValueError(f"Unknown color: {color}")


def is_gradient(color: Any) -> bool:
    """Check if color is a gradient (preset or list)."""
    if isinstance(color, list):
        return True
    if isinstance(color, str):
        color_lower = color.lower()
        if color_lower in GRADIENTS:
            return True
        if "," in color_lower or color_lower.startswith("#"):
            return True
    return False


def parse_fill(color: Any) -> List[Tuple[int, int, int, int]]:
    """Parse fill value to gradient color list.
    
    Supports:
    - Gradient preset name: "cyan_magenta", "green_red"
    - Hex color: "#ff0000"
    - Named color: "red", "magenta", etc.
    - Custom gradient list: ["#00c8f8", "#ff00fe"]
    - Comma-separated hex: "#00c8f8,#ff00fe"
    """
    if isinstance(color, list):
        return [parse_color(c) if isinstance(c, str) else (*c, 255) for c in color]
    
    if isinstance(color, str):
        color_lower = color.lower().strip()
        
        if color_lower in GRADIENTS:
            return [(*c, 255) for c in GRADIENTS[color_lower]]
        
        if "," in color_lower:
            colors = color_lower.replace(" ", "").split(",")
            return [parse_color(c) for c in colors]
        
        if color_lower.startswith("#") or color_lower in SOLID_COLORS:
            return [parse_color(color)]
    
    raise ValueError(f"Invalid fill value: {color}")


def parse_gradient(gradient: Union[str, List[str]]) -> List[Tuple[int, int, int, int]]:
    """Parse a gradient specification.
    
    Supports:
    - Preset names: "cyan_magenta", "green_red"
    - List of hex colors: ["#00c8f8", "#ff00fe"]
    """
    if isinstance(gradient, str):
        gradient_lower = gradient.lower()
        if gradient_lower in GRADIENTS:
            return [(*c, 255) for c in GRADIENTS[gradient_lower]]
        elif gradient_lower.startswith("#") or "," in gradient:
            colors = gradient.replace(" ", "").split(",")
            return [parse_color(c) for c in colors]
        else:
            raise ValueError(f"Unknown gradient preset: {gradient}")
    
    if isinstance(gradient, list):
        return [parse_color(c) if isinstance(c, str) else (*c, 255) for c in gradient]
    
    raise ValueError(f"Invalid gradient specification: {gradient}")


def interpolate_color(c1: Tuple[int, int, int, int], 
                      c2: Tuple[int, int, int, int], 
                      t: float) -> Tuple[int, int, int, int]:
    """Interpolate between two colors."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
        int(c1[3] + (c2[3] - c1[3]) * t),
    )


def get_gradient_color(gradient: List[Tuple[int, int, int, int]], 
                       position: float) -> Tuple[int, int, int, int]:
    """Get color from gradient at given position (0.0 to 1.0)."""
    if not gradient:
        return (0, 0, 0, 0)
    
    if len(gradient) == 1:
        return gradient[0]
    
    position = max(0.0, min(1.0, position))
    scaled_pos = position * (len(gradient) - 1)
    index = int(scaled_pos)
    t = scaled_pos - index
    
    if index >= len(gradient) - 1:
        return gradient[-1]
    
    return interpolate_color(gradient[index], gradient[index + 1], t)


class ColorScheme:
    """Container for parsed color scheme."""
    
    def __init__(self, colors: dict):
        self._colors = colors
        self._parse_colors()
    
    def _parse_colors(self):
        colors = self._colors
        
        self.cpu_ring = self._parse_ring_config(colors.get("cpu_ring", {}))
        self.gpu_ring = self._parse_ring_config(colors.get("gpu_ring", {}))
        self.ram_ring = self._parse_ring_config(colors.get("ram_ring", {}))
        
        self.cpu_temp = self._parse_progress_config(colors.get("cpu_temp", {}))
        self.gpu_temp = self._parse_progress_config(colors.get("gpu_temp", {}))
        self.cpu_clock = self._parse_progress_config(colors.get("cpu_clock", {}))
        self.gpu_clock = self._parse_progress_config(colors.get("gpu_clock", {}))
        self.cpu_fan = self._parse_progress_config(colors.get("cpu_fan", {}))
        self.gpu_fan = self._parse_progress_config(colors.get("gpu_fan", {}))
        
        text_colors = colors.get("text", {})
        self.text_title = parse_color(text_colors.get("title", "#ffffff"))
        self.text_data = parse_color(text_colors.get("data", "#ffffff"))
        
        self.separator = parse_color(colors.get("separator", "#331933"))
    
    def _parse_ring_config(self, config: dict) -> dict:
        fill = config.get("fill", "cyan_magenta")
        return {
            "background": parse_color(config.get("background", "#ffffff")),
            "border": parse_color(config.get("border", "#331933")),
            "separator": parse_color(config.get("separator", "#000000")),
            "fill": parse_fill(fill),
        }
    
    def _parse_progress_config(self, config: dict) -> dict:
        if isinstance(config, str):
            fill = config
            config_dict = {}
        else:
            fill = config.get("fill", "cyan_magenta")
            config_dict = config
        
        return {
            "background": parse_color(config_dict.get("background", "transparent")),
            "border": parse_color(config_dict.get("border", "#ffffff")),
            "separator": parse_color(config_dict.get("separator", "#000000")),
            "style": config_dict.get("style", "segmented"),
            "fill": parse_fill(fill),
        }
    
    @property
    def default_ring(self) -> dict:
        """Get default ring config."""
        return self.cpu_ring

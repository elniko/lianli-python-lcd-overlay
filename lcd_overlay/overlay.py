"""Overlay assembly for LCD display."""

from typing import Dict, Any, Tuple

from PIL import Image, ImageDraw, ImageFont

from .colors import ColorScheme, TRANSPARENT, parse_color
from .renderer import Renderer


class OverlayBuilder:
    """Builder for LCD overlay images."""
    
    def __init__(self, colors: ColorScheme, fan_max: dict = None):
        self.colors = colors
        self.renderer = Renderer(colors)
        self.fan_max = fan_max or {"cpu": 2057, "gpu": 3260}
        self._fonts = None
    
    def _get_fonts(self) -> dict:
        """Lazy-load fonts."""
        if self._fonts is None:
            try:
                self._fonts = {
                    "title": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22),
                    "value": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48),
                    "label": ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16),
                }
            except Exception:
                self._fonts = {
                    "title": ImageFont.load_default(),
                    "value": ImageFont.load_default(),
                    "label": ImageFont.load_default(),
                }
        return self._fonts
    
    def create_cpu_overlay(self, sensors: Dict[str, Any], y_offset: int = 30) -> Image.Image:
        """Create CPU monitor overlay."""
        overlay = Image.new('RGBA', (480, 300), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        fonts = self._get_fonts()
        white = self.colors.text_title
        
        draw.text((40, 10), "CPU MONITOR", fill=white, font=fonts["title"])
        
        load = sensors.get('cpu', 0)
        ring_center = (120, 145)
        ring_radius = 70
        
        self.renderer.draw_ring(
            draw, ring_center, ring_radius, load,
            self.colors.cpu_ring, width=20
        )
        
        bbox = fonts["label"].getbbox("LOAD")
        label_width = bbox[2] - bbox[0]
        draw.text((ring_center[0] - label_width // 2, ring_center[1] - 55), "LOAD", fill=white, font=fonts["label"])
        
        load_num = f"{load:.0f}"
        bbox = fonts["value"].getbbox(load_num)
        num_width = bbox[2] - bbox[0]
        draw.text((ring_center[0] - num_width // 2, ring_center[1] - 30), load_num, fill=white, font=fonts["value"])
        
        percent = "%"
        bbox = fonts["label"].getbbox(percent)
        pct_width = bbox[2] - bbox[0]
        draw.text((ring_center[0] - pct_width // 2, ring_center[1] + 25), percent, fill=white, font=fonts["label"])
        
        temp = sensors.get('temp', 0)
        temp_x = 230
        bar_y = 90
        bar_width_total = 200
        bar_height = 25
        temp_segments = 15
        
        draw.text((temp_x, bar_y - 22), "TEMP", fill=white, font=fonts["label"])
        
        temp_text = f"{temp:.0f}C"
        bbox = fonts["label"].getbbox(temp_text)
        temp_text_width = bbox[2] - bbox[0]
        draw.text((temp_x + bar_width_total - temp_text_width, bar_y - 22), temp_text, fill=white, font=fonts["label"])
        
        self.renderer.draw_progress_bar(
            draw, temp_x, bar_y, bar_width_total, bar_height,
            temp, 100, self.colors.cpu_temp,
            num_segments=temp_segments
        )
        
        clock = sensors.get('clock', 0)
        clock_bar_y = 155
        clock_segments = 15
        
        draw.text((temp_x, clock_bar_y - 22), "CLOCK", fill=white, font=fonts["label"])
        
        if clock >= 1000:
            clock_text = f"{clock/1000:.2f}G"
        else:
            clock_text = f"{clock:.0f}M"
        bbox = fonts["label"].getbbox(clock_text)
        clock_text_width = bbox[2] - bbox[0]
        draw.text((temp_x + bar_width_total - clock_text_width, clock_bar_y - 22), clock_text, fill=white, font=fonts["label"])
        
        self.renderer.draw_progress_bar(
            draw, temp_x, clock_bar_y, bar_width_total, bar_height,
            clock, 5000, self.colors.cpu_clock,
            num_segments=clock_segments
        )
        
        return overlay
    
    def create_gpu_overlay(self, sensors: Dict[str, Any], y_offset: int = 60) -> Image.Image:
        """Create GPU monitor overlay."""
        overlay = Image.new('RGBA', (480, 300), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        fonts = self._get_fonts()
        white = self.colors.text_title
        
        draw.text((40, 10), "GPU MONITOR", fill=white, font=fonts["title"])
        
        load = sensors.get('gpu', 0)
        ring_center = (120, 145)
        ring_radius = 70
        
        self.renderer.draw_ring(
            draw, ring_center, ring_radius, load,
            self.colors.gpu_ring, width=20
        )
        
        bbox = fonts["label"].getbbox("LOAD")
        label_width = bbox[2] - bbox[0]
        draw.text((ring_center[0] - label_width // 2, ring_center[1] - 55), "LOAD", fill=white, font=fonts["label"])
        
        load_num = f"{load:.0f}"
        bbox = fonts["value"].getbbox(load_num)
        num_width = bbox[2] - bbox[0]
        draw.text((ring_center[0] - num_width // 2, ring_center[1] - 30), load_num, fill=white, font=fonts["value"])
        
        percent = "%"
        bbox = fonts["label"].getbbox(percent)
        pct_width = bbox[2] - bbox[0]
        draw.text((ring_center[0] - pct_width // 2, ring_center[1] + 25), percent, fill=white, font=fonts["label"])
        
        temp = sensors.get('gpu_temp', 0)
        temp_x = 230
        bar_y = 90
        bar_width_total = 200
        bar_height = 25
        temp_segments = 15
        
        draw.text((temp_x, bar_y - 22), "TEMP", fill=white, font=fonts["label"])
        
        temp_text = f"{temp:.0f}C"
        bbox = fonts["label"].getbbox(temp_text)
        temp_text_width = bbox[2] - bbox[0]
        draw.text((temp_x + bar_width_total - temp_text_width, bar_y - 22), temp_text, fill=white, font=fonts["label"])
        
        self.renderer.draw_progress_bar(
            draw, temp_x, bar_y, bar_width_total, bar_height,
            temp, 100, self.colors.gpu_temp,
            num_segments=temp_segments
        )
        
        clock = sensors.get('gpu_clock', 0)
        clock_bar_y = 155
        
        draw.text((temp_x, clock_bar_y - 22), "CLOCK", fill=white, font=fonts["label"])
        
        if clock >= 1000:
            clock_text = f"{clock/1000:.2f}G"
        else:
            clock_text = f"{clock:.0f}M"
        bbox = fonts["label"].getbbox(clock_text)
        clock_text_width = bbox[2] - bbox[0]
        draw.text((temp_x + bar_width_total - clock_text_width, clock_bar_y - 22), clock_text, fill=white, font=fonts["label"])
        
        self.renderer.draw_progress_bar(
            draw, temp_x, clock_bar_y, bar_width_total, bar_height,
            clock, 2500, self.colors.gpu_clock,
            num_segments=15
        )
        
        return overlay
    
    def create_ram_fan_overlay(self, sensors: Dict[str, Any], y_offset: int = 60) -> Image.Image:
        """Create RAM and FAN monitor overlay - RAM on left, FAN on right."""
        overlay = Image.new('RGBA', (480, 300), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        fonts = self._get_fonts()
        white = self.colors.text_title
        
        draw.text((40, 10), "RAM", fill=white, font=fonts["title"])
        draw.text((230, 10), "FAN", fill=white, font=fonts["title"])
        
        ram = sensors.get('ram', 0)
        ram_center = (120, 145)
        ram_radius = 70
        
        self.renderer.draw_ring(
            draw, ram_center, ram_radius, ram,
            self.colors.ram_ring, width=20
        )
        
        bbox = fonts["label"].getbbox("USED")
        label_width = bbox[2] - bbox[0]
        draw.text((ram_center[0] - label_width // 2, ram_center[1] - 55), "USED", fill=white, font=fonts["label"])
        
        ram_text = f"{ram:.0f}"
        bbox = fonts["value"].getbbox(ram_text)
        num_width = bbox[2] - bbox[0]
        draw.text((ram_center[0] - num_width // 2, ram_center[1] - 30), ram_text, fill=white, font=fonts["value"])
        
        percent = "%"
        bbox = fonts["label"].getbbox(percent)
        pct_width = bbox[2] - bbox[0]
        draw.text((ram_center[0] - pct_width // 2, ram_center[1] + 25), percent, fill=white, font=fonts["label"])
        
        cpu_fan = sensors.get('cpu_fan', 0)
        fan_x = 230
        fan_bar_y = 90
        fan_bar_width = 200
        fan_bar_height = 25
        fan_segments = 15
        cpu_fan_max = self.fan_max.get("cpu", 2057)
        
        draw.text((fan_x, fan_bar_y - 22), "CPU FAN", fill=white, font=fonts["label"])
        
        fan_text = f"{cpu_fan:.0f} RPM"
        bbox = fonts["label"].getbbox(fan_text)
        fan_text_width = bbox[2] - bbox[0]
        draw.text((fan_x + fan_bar_width - fan_text_width, fan_bar_y - 22), fan_text, fill=white, font=fonts["label"])
        
        self.renderer.draw_progress_bar(
            draw, fan_x, fan_bar_y, fan_bar_width, fan_bar_height,
            cpu_fan, cpu_fan_max, self.colors.cpu_fan,
            num_segments=fan_segments
        )
        
        gpu_fan_percent = sensors.get('gpu_fan', 0)
        gpu_fan_max_rpm = self.fan_max.get("gpu", 3260)
        gpu_fan_rpm = int((gpu_fan_percent / 100.0) * gpu_fan_max_rpm)
        fan2_x = 230
        fan2_bar_y = 155
        fan2_bar_width = 200
        fan2_bar_height = 25
        fan2_segments = 15
        
        draw.text((fan2_x, fan2_bar_y - 22), "GPU FAN", fill=white, font=fonts["label"])
        
        fan2_text = f"{gpu_fan_rpm} RPM"
        bbox = fonts["label"].getbbox(fan2_text)
        fan2_text_width = bbox[2] - bbox[0]
        draw.text((fan2_x + fan2_bar_width - fan2_text_width, fan2_bar_y - 22), fan2_text, fill=white, font=fonts["label"])
        
        self.renderer.draw_progress_bar(
            draw, fan2_x, fan2_bar_y, fan2_bar_width, fan2_bar_height,
            gpu_fan_percent, 100, self.colors.gpu_fan,
            num_segments=fan2_segments
        )
        
        return overlay
    
    def draw_separator(self, draw: ImageDraw.ImageDraw, y: int, width: int = 480) -> None:
        """Draw separator line between sections."""
        draw.line([(0, y), (width, y)], fill=self.colors.separator, width=2)

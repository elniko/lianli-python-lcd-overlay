"""Rendering utilities for LCD overlay."""

import math
from typing import List, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont

from .colors import ColorScheme, TRANSPARENT, get_gradient_color


DEFAULT_FONT_TITLE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEFAULT_FONT_VALUE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEFAULT_FONT_LABEL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


class Renderer:
    """Renderer for LCD overlay elements."""
    
    def __init__(self, colors: ColorScheme):
        self.colors = colors
        self._fonts = None
    
    def _get_fonts(self) -> dict:
        """Lazy-load fonts."""
        if self._fonts is None:
            try:
                self._fonts = {
                    "title": ImageFont.truetype(DEFAULT_FONT_TITLE, 22),
                    "value": ImageFont.truetype(DEFAULT_FONT_VALUE, 48),
                    "label": ImageFont.truetype(DEFAULT_FONT_LABEL, 16),
                }
            except Exception:
                self._fonts = {
                    "title": ImageFont.load_default(),
                    "value": ImageFont.load_default(),
                    "label": ImageFont.load_default(),
                }
        return self._fonts
    
    def draw_ring(
        self,
        draw: ImageDraw.ImageDraw,
        center: Tuple[int, int],
        radius: int,
        percentage: float,
        config: dict,
        width: int = 20,
        num_segments: int = 20,
    ) -> None:
        """Draw a ring chart with segments and radial borders."""
        cx, cy = center
        inner_radius = radius - 5
        
        background = config["background"]
        border_color = config["border"]
        separator_color = config.get("separator", (0, 0, 0, 255))
        fill = config["fill"]
        
        segment_angle = 360.0 / num_segments
        total_filled = (percentage / 100.0) * num_segments
        
        for i in range(num_segments):
            start_deg = 90 - i * segment_angle
            end_deg = start_deg - segment_angle
            
            points = self._create_arc_points(
                cx, cy, inner_radius, radius + width,
                start_deg, end_deg
            )
            
            draw.polygon(points, fill=background)
        
        for i in range(int(total_filled)):
            t = i / (num_segments - 1) if num_segments > 1 else 0
            color = get_gradient_color(fill, t)
            
            start_deg = 90 - i * segment_angle
            end_deg = start_deg - segment_angle
            
            points = self._create_arc_points(
                cx, cy, inner_radius, radius + width,
                start_deg, end_deg
            )
            
            draw.polygon(points, fill=color)
        
        if total_filled > int(total_filled) and total_filled > 0:
            i = int(total_filled)
            fill_ratio = total_filled - int(total_filled)
            
            t = i / (num_segments - 1) if num_segments > 1 else 0
            color = get_gradient_color(fill, t)
            
            start_deg = 90 - i * segment_angle
            end_deg = start_deg - segment_angle
            partial_end_deg = start_deg - segment_angle * fill_ratio
            
            points = self._create_partial_arc(
                cx, cy, inner_radius, radius + width,
                start_deg, partial_end_deg
            )
            draw.polygon(points, fill=color)
        
        for i in range(num_segments):
            angle = math.radians(90 - i * segment_angle)
            draw.line(
                [
                    (cx + inner_radius * math.cos(angle), cy - inner_radius * math.sin(angle)),
                    (cx + (radius + width) * math.cos(angle), cy - (radius + width) * math.sin(angle))
                ],
                fill=separator_color,
                width=5
            )
        
        draw.ellipse(
            [cx - inner_radius, cy - inner_radius, cx + inner_radius, cy + inner_radius],
            outline=border_color,
            width=3
        )
    
    def _create_arc_points(
        self, cx: int, cy: int,
        inner_r: int, outer_r: int,
        start_deg: float, end_deg: float
    ) -> List[Tuple[int, int]]:
        """Create points for an arc segment."""
        points = []
        
        arc_start = math.radians(start_deg)
        arc_end = math.radians(end_deg)
        
        for j in range(11):
            angle = arc_start - (arc_start - arc_end) * j / 10
            points.append((
                cx + outer_r * math.cos(angle),
                cy - outer_r * math.sin(angle)
            ))
        
        for j in range(11):
            angle = arc_end + (arc_start - arc_end) * j / 10
            points.append((
                cx + inner_r * math.cos(angle),
                cy - inner_r * math.sin(angle)
            ))
        
        return points
    
    def _create_partial_arc(
        self, cx: int, cy: int,
        inner_r: int, outer_r: int,
        start_deg: float, end_deg: float
    ) -> List[Tuple[int, int]]:
        """Create points for a partially filled arc segment from start_deg to end_deg (clockwise)."""
        points = []
        
        arc_start = math.radians(start_deg)
        arc_end = math.radians(end_deg)
        
        for j in range(11):
            t = j / 10
            angle = arc_start + (arc_end - arc_start) * t
            points.append((
                cx + outer_r * math.cos(angle),
                cy - outer_r * math.sin(angle)
            ))
        
        for j in range(11):
            t = j / 10
            angle = arc_end + (arc_start - arc_end) * t
            points.append((
                cx + inner_r * math.cos(angle),
                cy - inner_r * math.sin(angle)
            ))
        
        return points
    
    def draw_progress_bar(
        self,
        draw: ImageDraw.ImageDraw,
        x: int, y: int,
        width: int, height: int,
        value: float, max_value: float,
        config: dict,
        num_segments: int = 15,
        gap: int = 2,
    ) -> None:
        """Draw a segmented progress bar with border around entire bar."""
        style = config.get("style", "segmented")
        border_color = config.get("border", (255, 255, 255, 255))
        separator_color = config.get("separator", (0, 0, 0, 255))
        background_color = config.get("background", (30, 30, 30, 255))
        fill = config.get("fill", [(0, 200, 248, 255)])
        
        filled_ratio = min(value / max_value, 1.0) if max_value > 0 else 0
        
        if style == "solid":
            filled_width = int(width * filled_ratio)
            if filled_width > 0:
                color = get_gradient_color(fill, 1.0)
                draw.rectangle(
                    [x, y, x + filled_width, y + height],
                    fill=color
                )
        else:
            segment_width = width // num_segments
            filled_segments = int(filled_ratio * num_segments)
            
            for i in range(num_segments):
                seg_x = x + i * segment_width
                seg_width = segment_width - gap
                is_filled = i < filled_segments
                
                if is_filled:
                    t = i / (num_segments - 1) if num_segments > 1 else 0
                    color = get_gradient_color(fill, t)
                else:
                    color = background_color
                
                draw.rectangle(
                    [seg_x, y, seg_x + seg_width, y + height],
                    fill=color
                )
            
            for i in range(num_segments - 1):
                sep_x = x + (i + 1) * segment_width - gap // 2
                if separator_color[3] > 0:
                    draw.rectangle(
                        [sep_x, y, sep_x + gap, y + height],
                        fill=separator_color
                    )
        
        draw.rectangle(
            [x, y, x + width, y + height],
            outline=border_color,
            width=1
        )
    
    def draw_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        pos: Tuple[int, int],
        color: Tuple[int, int, int, int],
        font_key: str = "label"
    ) -> None:
        """Draw text."""
        fonts = self._get_fonts()
        draw.text(pos, text, fill=color, font=fonts[font_key])
    
    def text_size(self, text: str, font_key: str = "label") -> Tuple[int, int]:
        """Get text bounding box."""
        fonts = self._get_fonts()
        bbox = fonts[font_key].getbbox(text)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])

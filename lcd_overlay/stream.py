"""H264 streaming and LCD communication."""

import io
import os
import sys
import time
import signal
import threading
from pathlib import Path
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Linx'))

from linx import LCDDevice, _make_header, CMD_START_PLAY

from .sensors import SensorData
from .overlay import OverlayBuilder


class LCDStreamer:
    """H264 video streamer with sensor overlay."""
    
    def __init__(self, config, colors):
        self.config = config
        self.colors = colors
        self.running = False
        
        self.lcd: Optional[LCDDevice] = None
        self.sensors = SensorData()
        self.overlay_builder = OverlayBuilder(colors, config.fan_max if hasattr(config, 'fan_max') else None)
        
        self.frame = None
        self.has_video = False
    
    def connect(self) -> None:
        """Connect to LCD device."""
        self.lcd = LCDDevice()
        if not self.lcd.connect():
            raise RuntimeError("Failed to connect to LCD")
        
        self.lcd.init()
        self.lcd.prepare_display()
        self.lcd.check_h264_block()
    
    def load_background(self) -> None:
        """Load background frame."""
        from PIL import Image
        
        self.has_video = bool(self.config.video and os.path.exists(self.config.video))
        
        if self.config.background and os.path.exists(self.config.background):
            self.frame = Image.open(self.config.background).convert('RGBA')
        elif self.has_video:
            self.frame = Image.new('RGBA', (480, 1920), (0, 0, 0, 0))
        else:
            self.frame = Image.new('RGBA', (480, 1920), (0, 0, 0, 255))
    
    def start(self) -> None:
        """Start streaming."""
        self.connect()
        self.lcd.stop_play()
        self.load_background()
        
        if self.has_video:
            print(f"Buffer: {self.lcd.h264_buf_len}")
            print(f"Streaming video: {self.config.video}")
        else:
            print("No video file, overlay only mode")
        
        self.running = True
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("Starting stream... (Ctrl+C to stop)")
        
        self._stream_loop()
    
    def _signal_handler(self, sig, frame) -> None:
        """Handle shutdown signals."""
        print("\nStopping...")
        self.running = False
    
    def _stream_loop(self) -> None:
        """Main streaming loop."""
        if self.has_video:
            self._stream_with_video()
        else:
            self._stream_overlay_only()
    
    def _stream_with_video(self) -> None:
        """Stream video with overlay using play_h264."""
        video_path = self.config.video
        
        video_thread = threading.Thread(
            target=self.lcd.play_h264,
            args=(video_path, True),
            kwargs={'play_cmd': CMD_START_PLAY},
            daemon=True
        )
        video_thread.start()
        
        while self.running:
            self._send_overlay()
            time.sleep(0.1)
    
    def _stream_overlay_only(self) -> None:
        """Stream overlay only without video."""
        while self.running:
            self._send_overlay()
            time.sleep(0.1)
    
    def _send_overlay(self) -> None:
        """Update sensor data and send overlay to display."""
        self.sensors.update()
        sensors_data = self.sensors.to_dict()
        
        cpu_overlay = self.overlay_builder.create_cpu_overlay(sensors_data)
        gpu_overlay = self.overlay_builder.create_gpu_overlay(sensors_data)
        ram_fan_overlay = self.overlay_builder.create_ram_fan_overlay(sensors_data)
        
        positions = self.config.positions
        
        result = self.frame.copy()
        result.paste(cpu_overlay, (0, positions.get("cpu", 30)), cpu_overlay)
        result.paste(gpu_overlay, (0, positions.get("gpu", 335)), gpu_overlay)
        result.paste(ram_fan_overlay, (0, positions.get("ram_fan", 645)), ram_fan_overlay)
        
        buf_io = io.BytesIO()
        result.save(buf_io, format='PNG')
        self.lcd.push_png(buf_io.getvalue())
    
    def _stop(self) -> None:
        """Stop streaming and cleanup."""
        if self.lcd:
            self.lcd.stop_play()
            self.lcd.close()
        print("Done")

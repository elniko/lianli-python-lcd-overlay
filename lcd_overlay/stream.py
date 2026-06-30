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
        
        # Failure tracking
        self._fail_count = 0
        self._last_heartbeat = 0
        self._consecutive_recoveries = 0
        self._video_thread: Optional[threading.Thread] = None
    
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
        self._last_heartbeat = time.time()
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("Starting stream... (Ctrl+C to stop)")
        
        self._stream_loop()
    
    def _signal_handler(self, sig, frame) -> None:
        """Handle shutdown signals."""
        print("\nStopping...")
        self.running = False
    
    def _stream_loop(self) -> None:
        """Main streaming loop with failure detection and auto-recovery."""
        if self.has_video:
            self._start_video_thread()
        
        while self.running:
            # Heartbeat check every 10 seconds
            now = time.time()
            if now - self._last_heartbeat >= 10:
                self._last_heartbeat = now
                if not self.lcd.health_check():
                    print("[stream] Health check failed, initiating recovery...")
                    if not self._recover():
                        print("[stream] Recovery failed, waiting before retry...")
                        time.sleep(5)
                        continue
            
            try:
                self._send_overlay()
                self._fail_count = 0
            except Exception as e:
                self._fail_count += 1
                print(f"[stream] Overlay error ({self._fail_count}/3): {e}")
                if self._fail_count >= 3:
                    print("[stream] Too many failures, initiating recovery...")
                    if not self._recover():
                        print("[stream] Recovery failed, waiting before retry...")
                        time.sleep(5)
                    self._fail_count = 0
            
            time.sleep(0.1)
        
        self._stop()
    
    def _start_video_thread(self) -> None:
        """Start the H.264 video playback thread."""
        video_path = self.config.video
        self._video_thread = threading.Thread(
            target=self.lcd.play_h264,
            args=(video_path, True),
            kwargs={'play_cmd': CMD_START_PLAY},
            daemon=True
        )
        self._video_thread.start()
    
    def _recover(self) -> bool:
        """Recover from USB disconnection after sleep/hibernate.

        Sequence:
        1. Stop any active playback
        2. Close current USB handle
        3. Hard reset (usbreset or sysfs power-cycle)
        4. Reconnect and reinitialize
        5. Restart video thread if needed

        Returns True if recovery succeeded.
        """
        self._consecutive_recoveries += 1
        backoff = min(self._consecutive_recoveries * 2, 10)
        print(f"[recover] Attempt {self._consecutive_recoveries} (backoff {backoff}s)...")
        
        # 1. Stop playback
        try:
            if self.lcd:
                self.lcd.stop_play()
        except Exception as e:
            print(f"[recover] stop_play failed (expected): {e}")
        
        # 2. Close handle
        try:
            if self.lcd:
                self.lcd.close()
        except Exception as e:
            print(f"[recover] close failed (expected): {e}")
        
        time.sleep(1)
        
        # 3. Hard reset (usbreset binary or sysfs power-cycle)
        try:
            reset_ok = self.lcd.hard_reset()
        except Exception as e:
            print(f"[recover] hard_reset failed: {e}")
            reset_ok = False
        
        if not reset_ok:
            # If hard_reset fails, try one more time after a longer wait
            print("[recover] First reset attempt failed, retrying in 3s...")
            time.sleep(3)
            try:
                reset_ok = self.lcd.hard_reset()
            except Exception as e:
                print(f"[recover] Second reset attempt failed: {e}")
        
        if not reset_ok:
            print("[recover] Could not reset USB device")
            return False
        
        # 4. Reconnect
        time.sleep(1)
        try:
            if not self.lcd.connect():
                print("[recover] Reconnect failed")
                return False
        except Exception as e:
            print(f"[recover] Connect error: {e}")
            return False
        
        # 5. Reinitialize
        try:
            self.lcd.init()
            self.lcd.prepare_display()
            self.lcd.check_h264_block()
        except Exception as e:
            print(f"[recover] Re-init error: {e}")
            return False
        
        # 6. Restart video if needed
        if self.has_video:
            self._start_video_thread()
        
        print("[recover] Recovery successful!")
        self._consecutive_recoveries = 0
        self._last_heartbeat = time.time()
        return True
    
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
        
        resp = self.lcd.push_png(buf_io.getvalue())
        if resp is None:
            raise RuntimeError("push_png returned None (device unresponsive)")
    
    def _stop(self) -> None:
        """Stop streaming and cleanup."""
        if self.lcd:
            try:
                self.lcd.stop_play()
            except Exception:
                pass
            try:
                self.lcd.close()
            except Exception:
                pass
        print("Done")

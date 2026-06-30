"""Sensor data collection for LCD overlay."""

import psutil
from typing import Dict, Any, Optional

try:
    import pynvml
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except Exception:
    NVML_AVAILABLE = False


class SensorData:
    """Container for sensor readings."""
    
    def __init__(self):
        self.cpu_load: float = 0.0
        self.cpu_temp: float = 0.0
        self.cpu_clock: float = 0.0
        self.cpu_fan: float = 0.0
        
        self.gpu_load: float = 0.0
        self.gpu_temp: float = 0.0
        self.gpu_clock: float = 0.0
        self.gpu_fan: float = 0.0
        
        self.ram_usage: float = 0.0
        
        self._nvml_handle = None
        
        if NVML_AVAILABLE:
            try:
                self._nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            except Exception:
                self._nvml_handle = None
    
    def update(self) -> None:
        """Update all sensor readings."""
        self._update_cpu()
        self._update_gpu()
        self._update_ram()
        self._update_fans()
    
    def _update_cpu(self) -> None:
        """Update CPU sensors."""
        self.cpu_load = psutil.cpu_percent(interval=0)
        
        self.cpu_temp = 0.0
        temps = psutil.sensors_temperatures()
        
        sensor_names = ['k10temp', 'coretemp', 'cpu_thermal', 'cpu']
        for sensor_name in sensor_names:
            if sensor_name in temps:
                for entry in temps[sensor_name]:
                    if hasattr(entry, 'current') and entry.current is not None:
                        self.cpu_temp = float(entry.current)
                        break
                if self.cpu_temp > 0:
                    break
        
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                self.cpu_clock = cpu_freq.current
        except Exception:
            self.cpu_clock = 0.0
    
    def _update_gpu(self) -> None:
        """Update GPU sensors via NVML."""
        self.gpu_load = 0.0
        self.gpu_temp = 0.0
        self.gpu_clock = 0.0
        self.gpu_fan = 0.0
        
        if not NVML_AVAILABLE or self._nvml_handle is None:
            return
        
        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(self._nvml_handle)
            self.gpu_load = float(util.gpu)
            
            self.gpu_temp = float(pynvml.nvmlDeviceGetTemperature(
                self._nvml_handle, pynvml.NVML_TEMPERATURE_GPU
            ))
            
            self.gpu_clock = float(pynvml.nvmlDeviceGetClockInfo(
                self._nvml_handle, pynvml.NVML_CLOCK_SM
            ))
            
            self.gpu_fan = float(pynvml.nvmlDeviceGetFanSpeed(self._nvml_handle))
        except Exception:
            pass
    
    def _update_ram(self) -> None:
        """Update RAM usage."""
        self.ram_usage = psutil.virtual_memory().percent
    
    def _update_fans(self) -> None:
        """Update fan speeds."""
        self.cpu_fan = 0.0
        
        try:
            fans = psutil.sensors_fans()
            for name, entries in fans.items():
                if name == "it8696" and len(entries) > 0:
                    self.cpu_fan = entries[0].current
                    break
        except Exception:
            pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cpu": self.cpu_load,
            "temp": self.cpu_temp,
            "clock": self.cpu_clock,
            "gpu": self.gpu_load,
            "gpu_temp": self.gpu_temp,
            "gpu_clock": self.gpu_clock,
            "gpu_fan": self.gpu_fan,
            "ram": self.ram_usage,
            "cpu_fan": self.cpu_fan,
        }


def get_sensor_data() -> Dict[str, Any]:
    """Get current sensor readings."""
    sensors = SensorData()
    sensors.update()
    return sensors.to_dict()

"""Configuration loading and saving for LCD overlay."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_CONFIG = {
    "video": "/home/nicolas/diplay-linux/universal-screen-8.8-inch/video/88022__10040302.h264",
    "background": "/home/nicolas/diplay-linux/previews/88022__preview_4.png",
    "positions": {
        "cpu": 30,
        "gpu": 335,
        "ram_fan": 645,
    },
    "fan_max": {
        "cpu": 2057,
        "gpu": 3260,
    },
    "colors": {
        "cpu_ring": {
            "background": "#ffffff",
            "border": "#331933",
            "gradient": "cyan_magenta",
        },
        "gpu_ring": {
            "background": "#ffffff",
            "border": "#331933",
            "gradient": "cyan_magenta",
        },
        "ram_ring": {
            "background": "#ffffff",
            "border": "#331933",
            "gradient": "cyan_magenta",
        },
        "cpu_temp": "cyan_magenta",
        "gpu_temp": "cyan_magenta",
        "cpu_clock": "#ff00fe",
        "gpu_clock": "#ff00fe",
        "cpu_fan": "cyan_magenta",
        "gpu_fan": "cyan_magenta",
        "text": {
            "title": "#ffffff",
            "data": "#ffffff",
        },
        "progress_bar": {
            "background": "transparent",
            "border": "#ffffff",
            "separator": "#000000",
            "style": "segmented",
        },
    },
}


def merge_with_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user config with defaults."""
    result = DEFAULT_CONFIG.copy()
    
    for key, value in config.items():
        if key == "colors":
            result[key] = _merge_colors(result.get(key, {}), value)
        elif key == "positions":
            result[key] = {**result.get(key, {}), **value}
        else:
            result[key] = value
    
    return result


def _merge_colors(default_colors: Dict[str, Any], user_colors: Dict[str, Any]) -> Dict[str, Any]:
    """Merge color configs."""
    result = default_colors.copy()
    
    for key, value in user_colors.items():
        if key in ("text", "progress_bar") and isinstance(value, dict):
            result[key] = {**result.get(key, {}), **value}
        elif key == "cpu_ring" and isinstance(value, dict):
            result[key] = {**result.get(key, {}), **value}
        elif key == "gpu_ring" and isinstance(value, dict):
            result[key] = {**result.get(key, {}), **value}
        elif key == "ram_ring" and isinstance(value, dict):
            result[key] = {**result.get(key, {}), **value}
        else:
            result[key] = value
    
    return result


class Config:
    """LCD Overlay configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._config = DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self.load(config_path)
    
    def load(self, path: Optional[str] = None) -> None:
        """Load configuration from JSON file."""
        path = path or self.config_path
        if not path:
            raise ValueError("No config path specified")
        
        with open(path, 'r') as f:
            user_config = json.load(f)
        
        self._config = merge_with_defaults(user_config)
    
    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to JSON file."""
        path = path or self.config_path
        if not path:
            raise ValueError("No config path specified")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    @property
    def video(self) -> str:
        return self._config["video"]
    
    @property
    def background(self) -> str:
        return self._config["background"]
    
    @property
    def positions(self) -> Dict[str, int]:
        return self._config["positions"]
    
    @property
    def colors(self) -> Dict[str, Any]:
        return self._config["colors"]
    
    @property
    def fan_max(self) -> Dict[str, int]:
        return self._config.get("fan_max", {"cpu": 2057, "gpu": 3260})
    
    @property
    def raw(self) -> Dict[str, Any]:
        return self._config


def get_default_config_path() -> str:
    """Get path to default config file."""
    return os.path.join(os.path.dirname(__file__), "configs", "default.json")


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or use defaults."""
    if config_path is None:
        config_path = get_default_config_path()
    
    config = Config(config_path)
    
    if not os.path.exists(config_path):
        config.save()
    
    return config

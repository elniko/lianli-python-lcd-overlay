#!/usr/bin/env python3
"""Entry point for LCD overlay."""

import argparse
import os

from lcd_overlay.config import load_config
from lcd_overlay.stream import LCDStreamer
from lcd_overlay.colors import ColorScheme


def main():
    parser = argparse.ArgumentParser(description='LCD Overlay with sensor data')
    parser.add_argument(
        '-c', '--config',
        help='Path to config file',
        default=None
    )
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    print("Loading assets...")
    print(f"Config: {config.video}")
    
    colors = ColorScheme(config.colors)
    streamer = LCDStreamer(config, colors)
    
    streamer.start()


if __name__ == "__main__":
    main()

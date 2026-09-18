import json
import os

DEFAULT_CONFIG = {
    "camera_index": 0,
    "frame_width": 640,
    "frame_height": 480,
    "ear_threshold": 0.22,
    "consecutive_blink_frames": 3,
    "long_blink_frames": 18,
    "selection_options": [
        {"id": 1, "label": "Need Water", "color": [255, 105, 65]},
        {"id": 2, "label": "Need Food", "color": [0, 215, 255]},
        {"id": 3, "label": "Washroom Assistance", "color": [50, 205, 50]},
        {"id": 4, "label": "Medical Emergency", "color": [0, 0, 255]}
    ],
    "hardware": {
        "enable_rpi_gpio": False,
        "buzzer_pin": 18,
        "led_pins": {
            "Water": 23,
            "Food": 24,
            "Washroom": 25,
            "Emergency": 12
        }
    },
    "voice_feedback": True
}

def load_config(filepath="config/settings.json"):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

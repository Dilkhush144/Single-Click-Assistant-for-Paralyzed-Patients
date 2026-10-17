"""
Configuration parameters for Single-Click Assistant for Paralyzed Patients
Project: NIT Manipur - Dept. of Electronics and Communication Engineering (2026-27)
Team: Gaurav Kumar Chaudhary (23105026), Rahul Deb (23105031), Dilkhush Raj (23105008)
Advisor: Prof. L. Lolitkumar Singh
"""

import json
import os

DEFAULT_CONFIG = {
    # Video & Landmark Parameters
    "camera_index": 0,
    "frame_width": 640,
    "frame_height": 480,
    "target_fps": 30,
    
    # Eye Aspect Ratio (EAR) Calibration
    "ear_threshold": 0.22,
    
    # Blink Gesture Timing Thresholds (Frames at ~30 FPS)
    # Short Blink: 3 - 12 frames (~0.1s - 0.4s) -> Next Item
    # Medium Blink: 15 - 40 frames (~0.5s - 1.3s) -> Select Item
    # Long Blink: >= 55 frames (~1.8s - 3.0s) -> Back / Cancel
    "blink_timings": {
        "short_min_frames": 3,
        "short_max_frames": 13,
        "medium_min_frames": 16,
        "medium_max_frames": 45,
        "long_min_frames": 55
    },

    # Hierarchical Menu Tree according to Slide 8
    "menu_tree": {
        "id": "root",
        "title": "Main Menu",
        "items": [
            {
                "id": "needs",
                "label": "Needs",
                "speech": "Needs",
                "type": "submenu",
                "color": [245, 130, 48],
                "items": [
                    {"id": "water", "label": "Water", "speech": "Need Water", "type": "action", "action": "ALERT_WATER"},
                    {"id": "food", "label": "Food", "speech": "Need Food", "type": "action", "action": "ALERT_FOOD"},
                    {"id": "pain", "label": "Pain", "speech": "Severe Pain assistance needed", "type": "action", "action": "ALERT_PAIN"},
                    {"id": "washroom", "label": "Washroom", "speech": "Washroom assistance needed", "type": "action", "action": "ALERT_WASHROOM"}
                ]
            },
            {
                "id": "emergency",
                "label": "Emergency",
                "speech": "Emergency Alert",
                "type": "action",
                "action": "ALERT_EMERGENCY",
                "color": [0, 0, 240]
            },
            {
                "id": "entertainment",
                "label": "Entertainment",
                "speech": "Entertainment",
                "type": "submenu",
                "color": [60, 180, 75],
                "items": [
                    {"id": "music", "label": "Music", "speech": "Playing soothing music", "type": "action", "action": "MEDIA_MUSIC"},
                    {"id": "movies", "label": "Movies", "speech": "Starting audio movie stream", "type": "action", "action": "MEDIA_MOVIES"}
                ]
            },
            {
                "id": "room",
                "label": "Room Control",
                "speech": "Room Control",
                "type": "submenu",
                "color": [230, 25, 75],
                "items": [
                    {"id": "light", "label": "Light (Toggle)", "speech": "Toggling room light", "type": "action", "action": "TOGGLE_LIGHT"},
                    {"id": "fan", "label": "Fan Speed", "speech": "Adjusting fan speed", "type": "action", "action": "CYCLE_FAN"}
                ]
            }
        ]
    },

    # Hardware & Raspberry Pi Pin Mapping
    "hardware": {
        "enable_rpi_gpio": False,
        "buzzer_pin": 18,
        "light_relay_pin": 23,
        "fan_relay_pins": [24, 25],
        "ack_button_pin": 17,
        "status_led_pin": 27
    },

    # Audio & Feedback settings
    "voice_feedback": True,
    "eyes_free_audio_prompts": True,
    "speech_rate": 160
}

def load_config(filepath="config/settings.json"):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

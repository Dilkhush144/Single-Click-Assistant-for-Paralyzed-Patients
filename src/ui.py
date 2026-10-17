"""
Assistive User Interface (UI) rendering OpenCV dashboard for the patient and caregiver.
Displays hierarchical menu cards, real-time gesture hold telemetry, and virtual appliance statuses.
"""

import cv2
import numpy as np
import math
import time

class AssistiveUI:
    """Renders hierarchical menus, blink gesture hold meter, and virtual appliance states onto video frames."""

    def __init__(self, config):
        self.config = config
        self.fan_rotation_angle = 0
        self.blink_timings = config.get("blink_timings", {})
        self.long_min = self.blink_timings.get("long_min_frames", 55)

    def draw_fan_icon(self, frame, center_x, center_y, radius, speed):
        """Draws an animated virtual fan spinning according to current speed (0, 1, 2, 3)."""
        # Outer circle
        cv2.circle(frame, (center_x, center_y), radius, (180, 180, 180), 2)

        # Update angle if fan is spinning
        if speed > 0:
            self.fan_rotation_angle = (self.fan_rotation_angle + speed * 12) % 360

        # Draw 3 fan blades
        for i in range(3):
            blade_angle = math.radians(self.fan_rotation_angle + i * 120)
            end_x = int(center_x + (radius - 4) * math.cos(blade_angle))
            end_y = int(center_y + (radius - 4) * math.sin(blade_angle))
            color = (0, 255, 255) if speed > 0 else (100, 100, 100)
            cv2.line(frame, (center_x, center_y), (end_x, end_y), color, 3)

        cv2.circle(frame, (center_x, center_y), 4, (255, 255, 255), -1)

    def draw_interface(self, frame, system_state, ear_value, closed_frames, hold_status_str):
        h, w, _ = frame.shape

        # 1. Header Bar with System Info and Breadcrumb Path
        header_h = 75
        header_overlay = frame.copy()
        cv2.rectangle(header_overlay, (0, 0), (w, header_h), (25, 25, 25), -1)
        cv2.addWeighted(header_overlay, 0.85, frame, 0.15, 0, frame)

        # Title
        cv2.putText(frame, "Single-Click Assistant | NIT Manipur", (15, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        # Breadcrumb trail
        breadcrumb = system_state.get_breadcrumb()
        cv2.putText(frame, f"PATH: {breadcrumb}", (15, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 220, 255), 1)

        # Live EAR Readout
        ear_str = f"EAR: {ear_value:.2f}" if ear_value is not None else "No Face"
        ear_color = (0, 255, 0) if (ear_value is not None and ear_value >= self.config.get("ear_threshold", 0.22)) else (0, 0, 255)
        cv2.putText(frame, ear_str, (w - 180, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, ear_color, 2)

        # 2. Gesture Hold Progress Bar
        bar_x1, bar_y1 = w - 210, 42
        bar_w, bar_h = 195, 16
        cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x1 + bar_w, bar_y1 + bar_h), (60, 60, 60), -1)

        # Fill ratio capped at 1.0 (long blink threshold)
        fill_ratio = min(closed_frames / max(self.long_min, 1), 1.0)
        fill_w = int(bar_w * fill_ratio)

        # Color shifts based on target gesture: Blue -> Green -> Orange -> Red
        if fill_ratio < 0.25:
            bar_color = (255, 100, 0)
        elif fill_ratio < 0.65:
            bar_color = (0, 255, 120)
        else:
            bar_color = (0, 0, 255)

        if fill_w > 0:
            cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x1 + fill_w, bar_y1 + bar_h), bar_color, -1)
        cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x1 + bar_w, bar_y1 + bar_h), (200, 200, 200), 1)

        cv2.putText(frame, hold_status_str, (bar_x1, bar_y1 + bar_h + 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1)

        # 3. Virtual Room Appliance & Hardware Dashboard Panel (Slide 7, 8 & 11)
        dash_y = header_h + 10
        dash_w, dash_h = 190, 110
        dash_x = w - dash_w - 15

        dash_overlay = frame.copy()
        cv2.rectangle(dash_overlay, (dash_x, dash_y), (dash_x + dash_w, dash_y + dash_h), (30, 30, 30), -1)
        cv2.addWeighted(dash_overlay, 0.75, frame, 0.25, 0, frame)
        cv2.rectangle(frame, (dash_x, dash_y), (dash_x + dash_w, dash_y + dash_h), (120, 120, 120), 1)

        cv2.putText(frame, "APPLIANCE / IOT STATUS", (dash_x + 10, dash_y + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 255, 180), 1)

        # Light status
        light_on = system_state.light_state
        light_color = (0, 255, 255) if light_on else (100, 100, 100)
        cv2.circle(frame, (dash_x + 25, dash_y + 45), 10, light_color, -1 if light_on else 2)
        cv2.putText(frame, f"Light: {'ON (Relay 1)' if light_on else 'OFF'}", (dash_x + 45, dash_y + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)

        # Fan status with spinning icon
        self.draw_fan_icon(frame, dash_x + 25, dash_y + 82, 12, system_state.fan_speed)
        fan_text = f"Fan: Speed {system_state.fan_speed}" if system_state.fan_speed > 0 else "Fan: OFF"
        cv2.putText(frame, fan_text, (dash_x + 45, dash_y + 87),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)

        # 4. Hierarchical Menu Cards at Bottom (Slide 8)
        items = system_state.current_items
        if items:
            box_area_y1 = h - 95
            box_area_y2 = h - 35
            spacing = 10
            avail_w = w - 30
            card_w = (avail_w - (len(items) - 1) * spacing) // len(items)

            for i, item in enumerate(items):
                x1 = 15 + i * (card_w + spacing)
                x2 = x1 + card_w
                is_selected = (i == system_state.current_index)

                # Card background & border
                card_overlay = frame.copy()
                bg_color = (55, 55, 55) if not is_selected else (0, 110, 0)
                if item.get("id") == "emergency":
                    bg_color = (0, 0, 120) if not is_selected else (0, 0, 220)

                cv2.rectangle(card_overlay, (x1, box_area_y1), (x2, box_area_y2), bg_color, -1)
                cv2.addWeighted(card_overlay, 0.8, frame, 0.2, 0, frame)

                border_color = (0, 255, 0) if is_selected else (140, 140, 140)
                border_thick = 3 if is_selected else 1
                cv2.rectangle(frame, (x1, box_area_y1), (x2, box_area_y2), border_color, border_thick)

                # Label & indicator
                label = item.get("label", "")
                if is_selected:
                    cv2.circle(frame, (x1 + 14, box_area_y1 + 16), 5, (0, 255, 0), -1)

                cv2.putText(frame, label, (x1 + 10, box_area_y1 + 38),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)

        # 5. Bottom Gesture Instruction Bar
        foot_y1, foot_y2 = h - 30, h
        cv2.rectangle(frame, (0, foot_y1), (w, foot_y2), (20, 20, 20), -1)
        gesture_guide = "Short: NEXT (with voice) | Medium: SELECT | Long (>=3s): BACK | 'q': Exit"
        cv2.putText(frame, gesture_guide, (15, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)

        # 6. Active Alert / Caregiver Notification Banner
        if system_state.active_alert:
            banner_y1, banner_y2 = h // 2 - 45, h // 2 + 45
            is_emergency = "EMERGENCY" in system_state.active_alert.upper()
            banner_color = (0, 0, 220) if is_emergency else (0, 140, 0)

            banner_overlay = frame.copy()
            cv2.rectangle(banner_overlay, (30, banner_y1), (w - 30, banner_y2), banner_color, -1)
            cv2.addWeighted(banner_overlay, 0.9, frame, 0.1, 0, frame)
            cv2.rectangle(frame, (30, banner_y1), (w - 30, banner_y2), (255, 255, 255), 2)

            cv2.putText(frame, system_state.active_alert, (50, h // 2 + 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)

        return frame

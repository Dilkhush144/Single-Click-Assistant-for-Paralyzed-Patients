import cv2
import numpy as np

class AssistiveUI:
    """Renders menu items, selection states, and EAR diagnostics onto OpenCV frames."""

    def __init__(self, options):
        self.options = options
        self.selected_index = 0

    def next_option(self):
        self.selected_index = (self.selected_index + 1) % len(self.options)

    def get_current_option(self):
        return self.options[self.selected_index]

    def draw_interface(self, frame, ear_value, blink_counter, alert_text=None):
        h, w, _ = frame.shape

        # Semi-transparent overlay panel on top
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 110), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Title
        cv2.putText(frame, "AI Assistive Communicator", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Status telemetry
        ear_str = f"EAR: {ear_value:.2f}" if ear_value is not None else "Face Not Found"
        cv2.putText(frame, ear_str, (w - 220, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        progress_str = f"Hold Blink: {blink_counter}"
        cv2.putText(frame, progress_str, (w - 220, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Draw option boxes
        box_width = (w - 40) // len(self.options)
        for i, opt in enumerate(self.options):
            x1 = 20 + i * box_width
            x2 = x1 + box_width - 10
            y1, y2 = h - 90, h - 20

            is_active = (i == self.selected_index)
            border_color = (0, 255, 0) if is_active else (80, 80, 80)
            thickness = 3 if is_active else 1

            # Background
            cv2.rectangle(frame, (x1, y1), (x2, y2), (40, 40, 40), -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, thickness)

            # Indicator dot
            if is_active:
                cv2.circle(frame, (x1 + 15, y1 + 20), 6, (0, 255, 0), -1)

            # Option text
            cv2.putText(frame, opt["label"], (x1 + 10, y1 + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        # Triggered alert notification banner
        if alert_text:
            cv2.rectangle(frame, (50, h // 2 - 40), (w - 50, h // 2 + 40), (0, 0, 180), -1)
            cv2.putText(frame, f"DISPATCHED: {alert_text}", (70, h // 2 + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        return frame

"""
Finite State Machine (FSM) implementation as specified in Slide 8:
- Mealy FSM for blink duration gesture classification (Input: continuous EAR -> Output: SHORT, MEDIUM, LONG event).
- Moore FSM for menu navigation, room appliance states (Light, Fan), and Caregiver Alerts.
"""

from enum import Enum
import time

class BlinkGesture(Enum):
    NONE = 0
    SHORT = 1      # Move to next menu item
    MEDIUM = 2     # Select item / enter submenu
    LONG = 3       # Go back / Cancel (>= 3s)

class MealyBlinkClassifier:
    """Mealy FSM that observes continuous eye closure frames and generates discrete blink gesture events upon eye reopening."""

    def __init__(self, config):
        timings = config.get("blink_timings", {})
        self.short_min = timings.get("short_min_frames", 3)
        self.short_max = timings.get("short_max_frames", 13)
        self.medium_min = timings.get("medium_min_frames", 16)
        self.medium_max = timings.get("medium_max_frames", 45)
        self.long_min = timings.get("long_min_frames", 55)

        self.ear_threshold = config.get("ear_threshold", 0.22)
        self.closed_frames = 0
        self.is_eye_closed = False

    def update(self, ear_value):
        """Processes current frame's EAR. Returns (BlinkGesture, current_closed_frames, current_hold_status_str)."""
        if ear_value is None:
            # Face not detected, maintain state
            return BlinkGesture.NONE, self.closed_frames, "Face Not Found"

        if ear_value < self.ear_threshold:
            self.closed_frames += 1
            self.is_eye_closed = True

            # Real-time state feedback for UI meter
            if self.closed_frames >= self.long_min:
                hold_status = "HOLD: CANCEL / BACK [>=3s]"
            elif self.closed_frames >= self.medium_min:
                hold_status = "HOLD: SELECT [Medium]"
            elif self.closed_frames >= self.short_min:
                hold_status = "HOLD: NEXT [Short]"
            else:
                hold_status = "HOLD..."
            return BlinkGesture.NONE, self.closed_frames, hold_status

        else:
            # Eyes are currently open
            gesture = BlinkGesture.NONE
            if self.is_eye_closed:
                # Transition event on eye reopening
                frames = self.closed_frames
                if frames >= self.long_min:
                    gesture = BlinkGesture.LONG
                elif self.medium_min <= frames <= self.medium_max:
                    gesture = BlinkGesture.MEDIUM
                elif self.short_min <= frames <= self.short_max:
                    gesture = BlinkGesture.SHORT

                self.closed_frames = 0
                self.is_eye_closed = False

            return gesture, 0, "EYES OPEN"


class SystemState:
    """Moore FSM maintaining system state: Menu position, Room appliance states, and Alert triggers."""

    def __init__(self, config):
        self.menu_root = config["menu_tree"]
        self.menu_stack = [self.menu_root] # Stack for hierarchical menu navigation
        self.current_index = 0

        # Room appliances state (Slide 7 & 8: Light & Fan speed)
        self.light_state = False          # False = OFF, True = ON
        self.fan_speed = 0                # 0 = OFF, 1 = Low, 2 = Medium, 3 = High
        self.media_status = "Idle"        # "Playing Music", "Playing Movie", "Idle"

        # Alert state
        self.active_alert = None
        self.alert_timestamp = 0
        self.alert_duration = 4.0          # seconds to display alert message

    @property
    def current_menu(self):
        return self.menu_stack[-1]

    @property
    def current_items(self):
        return self.current_menu.get("items", [])

    @property
    def current_item(self):
        items = self.current_items
        if 0 <= self.current_index < len(items):
            return items[self.current_index]
        return None

    def get_breadcrumb(self):
        """Returns string breadcrumb path, e.g. 'Main Menu > Room Control'."""
        titles = [m.get("title", m.get("label", "Menu")) for m in self.menu_stack]
        return " > ".join(titles)

    def handle_gesture(self, gesture):
        """Executes state transition based on classified gesture. Returns action dictionary or None."""
        if gesture == BlinkGesture.NONE:
            return None

        # 1. SHORT BLINK: Cycle to Next Item
        if gesture == BlinkGesture.SHORT:
            items = self.current_items
            if items:
                self.current_index = (self.current_index + 1) % len(items)
            return {"type": "NAVIGATION", "item": self.current_item}

        # 2. LONG BLINK: Go Back / Cancel (Slide 8)
        elif gesture == BlinkGesture.LONG:
            if len(self.menu_stack) > 1:
                self.menu_stack.pop()
                self.current_index = 0
                return {"type": "BACK", "item": self.current_item, "msg": "Returned to previous menu"}
            else:
                return {"type": "CANCEL", "msg": "Already at Main Menu"}

        # 3. MEDIUM BLINK: Select current item
        elif gesture == BlinkGesture.MEDIUM:
            item = self.current_item
            if not item:
                return None

            if item.get("type") == "submenu":
                # Enter submenu
                self.menu_stack.append(item)
                self.current_index = 0
                return {"type": "ENTER_SUBMENU", "item": self.current_item}

            elif item.get("type") == "action":
                action_code = item.get("action")
                return self._execute_action(action_code, item)

        return None

    def _execute_action(self, action_code, item):
        """Applies Moore state changes for room appliances and caregiver alerts."""
        if action_code == "TOGGLE_LIGHT":
            self.light_state = not self.light_state
            state_str = "ON" if self.light_state else "OFF"
            self.trigger_alert(f"Room Light Switched {state_str}")
            return {"type": "DEVICE_UPDATE", "device": "LIGHT", "state": self.light_state, "speech": f"Light turned {state_str}"}

        elif action_code == "CYCLE_FAN":
            self.fan_speed = (self.fan_speed + 1) % 4
            speed_names = ["OFF", "Low (1)", "Medium (2)", "High (3)"]
            speed_name = speed_names[self.fan_speed]
            self.trigger_alert(f"Fan Speed Set to {speed_name}")
            return {"type": "DEVICE_UPDATE", "device": "FAN", "speed": self.fan_speed, "speech": f"Fan set to {speed_name}"}

        elif action_code == "MEDIA_MUSIC":
            self.media_status = "Playing Music"
            self.trigger_alert("Entertainment: Playing Soothing Music")
            return {"type": "MEDIA", "status": self.media_status, "speech": "Playing music"}

        elif action_code == "MEDIA_MOVIES":
            self.media_status = "Playing Movies"
            self.trigger_alert("Entertainment: Audio Entertainment Started")
            return {"type": "MEDIA", "status": self.media_status, "speech": "Starting audio movie stream"}

        elif action_code == "ALERT_EMERGENCY":
            self.trigger_alert("PRIORITY EMERGENCY ALERT DISPATCHED!", duration=8.0)
            return {"type": "EMERGENCY", "speech": "Emergency Alert! Caregiver assistance requested immediately!", "emergency": True}

        else:
            # Routine needs: Water, Food, Pain, Washroom
            label = item.get("label", "Request")
            speech = item.get("speech", label)
            self.trigger_alert(f"Request: {label}")
            return {"type": "CAREGIVER_ALERT", "item": item, "speech": speech}

    def trigger_alert(self, text, duration=4.0):
        self.active_alert = text
        self.alert_timestamp = time.time()
        self.alert_duration = duration

    def check_alert_timeout(self):
        if self.active_alert and (time.time() - self.alert_timestamp > self.alert_duration):
            self.active_alert = None

"""
Notifier, Text-to-Speech (TTS), and Hardware Relay / Alarm Controller.
Supports both real Raspberry Pi GPIO and Windows/PC software simulation.
"""

import threading
import time
import queue

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

class CaretakerNotifier:
    """Dispatches spoken audio prompts, caregiver alarms, and room appliance relays."""

    def __init__(self, config):
        self.config = config
        self.rpi_enabled = False
        self.speech_queue = queue.Queue()
        self.is_running = True

        # Check for Raspberry Pi GPIO
        if config.get("hardware", {}).get("enable_rpi_gpio", False):
            try:
                import RPi.GPIO as GPIO
                self.GPIO = GPIO
                self.GPIO.setmode(self.GPIO.BCM)
                self.buzzer_pin = config["hardware"].get("buzzer_pin", 18)
                self.light_pin = config["hardware"].get("light_relay_pin", 23)
                self.fan_pins = config["hardware"].get("fan_relay_pins", [24, 25])
                self.status_led = config["hardware"].get("status_led_pin", 27)

                self.GPIO.setup(self.buzzer_pin, self.GPIO.OUT, initial=self.GPIO.LOW)
                self.GPIO.setup(self.light_pin, self.GPIO.OUT, initial=self.GPIO.LOW)
                for p in self.fan_pins:
                    self.GPIO.setup(p, self.GPIO.OUT, initial=self.GPIO.LOW)
                self.GPIO.setup(self.status_led, self.GPIO.OUT, initial=self.GPIO.HIGH)

                self.rpi_enabled = True
                print("[HARDWARE] Raspberry Pi GPIO initialized successfully.")
            except ImportError:
                print("[HARDWARE] RPi.GPIO not found; operating in PC Software Simulation Mode.")

        # Start background TTS worker thread
        if HAS_TTS and config.get("voice_feedback", True):
            self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
            self.tts_thread.start()

    def _tts_worker(self):
        """Dedicated thread to handle text-to-speech without freezing the OpenCV frame rate."""
        try:
            engine = pyttsx3.init()
            rate = self.config.get("speech_rate", 160)
            engine.setProperty('rate', rate)
        except Exception as e:
            print(f"[TTS Initialization Error]: {e}")
            return

        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=0.2)
                if text:
                    try:
                        engine.say(text)
                        engine.runAndWait()
                    except Exception as e:
                        print(f"[TTS Run Error]: {e}")
                self.speech_queue.task_done()
            except queue.Empty:
                continue

    def speak(self, text, interrupt=False):
        """Queues speech feedback for eyes-free navigation and alert notifications."""
        if not self.config.get("voice_feedback", True) or not HAS_TTS:
            return

        # Slide 8: "Each item is read aloud, so no screen is needed."
        if interrupt:
            # Clear previous pending items if an urgent prompt or alert arrives
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except Exception:
                    break

        self.speech_queue.put(text)

    def trigger_buzzer(self, duration=0.5, pattern=1):
        """Fires local acoustic alarm (Slide 4, 7 & 11: Local alarm LED + buzzer)."""
        if self.rpi_enabled:
            def _beep():
                for _ in range(pattern):
                    self.GPIO.output(self.buzzer_pin, self.GPIO.HIGH)
                    time.sleep(duration)
                    self.GPIO.output(self.buzzer_pin, self.GPIO.LOW)
                    time.sleep(0.1)
            threading.Thread(target=_beep, daemon=True).start()
        else:
            print(f"[LOCAL ALARM] Buzzer beep ({pattern}x, {duration}s) triggered in simulation mode.")

    def set_light_relay(self, state: bool):
        """Controls room light physical relay or logs simulation status."""
        if self.rpi_enabled:
            level = self.GPIO.HIGH if state else self.GPIO.LOW
            self.GPIO.output(self.light_pin, level)
        print(f"[RELAY 1 - ROOM LIGHT]: {'POWER ON [CLOSED]' if state else 'POWER OFF [OPEN]'}")

    def set_fan_relays(self, speed: int):
        """Controls room fan multi-speed relay pins (0=Off, 1=Low, 2=Med, 3=High)."""
        if self.rpi_enabled:
            # 2-bit binary control on relay pins
            b0 = self.GPIO.HIGH if (speed & 1) else self.GPIO.LOW
            b1 = self.GPIO.HIGH if (speed & 2) else self.GPIO.LOW
            self.GPIO.output(self.fan_pins[0], b0)
            self.GPIO.output(self.fan_pins[1], b1)
        speed_labels = ["OFF", "LOW (1)", "MEDIUM (2)", "HIGH (3)"]
        print(f"[RELAY 2 - FAN CONTROLLER]: Speed set to {speed_labels[speed]}")

    def notify_action(self, action_result):
        """Processes dispatched action and triggers speech, buzzer, and relays."""
        action_type = action_result.get("type")

        if action_type == "NAVIGATION":
            item = action_result.get("item")
            if item and self.config.get("eyes_free_audio_prompts", True):
                speech_text = item.get("speech", item.get("label", ""))
                self.speak(speech_text, interrupt=True)

        elif action_type == "BACK":
            item = action_result.get("item")
            label = item.get("label", "Main Menu") if item else "Main Menu"
            self.speak(f"Back to {label}", interrupt=True)

        elif action_type == "ENTER_SUBMENU":
            item = action_result.get("item")
            label = item.get("label", "Submenu") if item else "Submenu"
            self.speak(f"Entered {label}", interrupt=True)

        elif action_type == "EMERGENCY":
            print("\n" + "!" * 50)
            print(" [CRITICAL] EMERGENCY ALARM DISPATCHED TO CAREGIVER!")
            print("!" * 50 + "\n")
            self.trigger_buzzer(duration=0.8, pattern=3)
            self.speak("Emergency! Caregiver assistance needed immediately!", interrupt=True)

        elif action_type == "CAREGIVER_ALERT":
            item = action_result.get("item", {})
            label = item.get("label", "Routine Request")
            speech = action_result.get("speech", label)
            print(f"\n[CAREGIVER ALERT]: {label} dispatched via local alarm & network.")
            self.trigger_buzzer(duration=0.4, pattern=1)
            self.speak(speech, interrupt=True)

        elif action_type == "DEVICE_UPDATE":
            device = action_result.get("device")
            speech = action_result.get("speech", "")
            if device == "LIGHT":
                self.set_light_relay(action_result.get("state", False))
            elif device == "FAN":
                self.set_fan_relays(action_result.get("speed", 0))
            self.speak(speech, interrupt=True)

        elif action_type == "MEDIA":
            speech = action_result.get("speech", "")
            self.speak(speech, interrupt=True)

    def cleanup(self):
        self.is_running = False
        if self.rpi_enabled:
            self.GPIO.cleanup()
        print("[HARDWARE] Relays and Notifier cleaned up.")

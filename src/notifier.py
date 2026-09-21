import threading
import time

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

class CaretakerNotifier:
    """Dispatches alerts via voice audio, simulated or real Raspberry Pi GPIO pins."""

    def __init__(self, config):
        self.config = config
        self.rpi_enabled = False

        if config.get("hardware", {}).get("enable_rpi_gpio", False):
            try:
                import RPi.GPIO as GPIO
                self.GPIO = GPIO
                self.GPIO.setmode(self.GPIO.BCM)
                self.buzzer_pin = config["hardware"].get("buzzer_pin", 18)
                self.GPIO.setup(self.buzzer_pin, self.GPIO.OUT, initial=self.GPIO.LOW)
                self.rpi_enabled = True
                print("[HARDWARE] Raspberry Pi GPIO initialized successfully.")
            except ImportError:
                print("[HARDWARE] RPi.GPIO not found; operating in software simulation mode.")

    def trigger_buzzer(self, duration=0.5):
        if self.rpi_enabled:
            def _beep():
                self.GPIO.output(self.buzzer_pin, self.GPIO.HIGH)
                time.sleep(duration)
                self.GPIO.output(self.buzzer_pin, self.GPIO.LOW)
            threading.Thread(target=_beep, daemon=True).start()
        else:
            print(f"[ALERT] Buzzer triggered for {duration}s")

    def speak(self, text):
        if not self.config.get("voice_feedback", True) or not HAS_TTS:
            return

        def _worker():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[TTS Error]: {e}")

        threading.Thread(target=_worker, daemon=True).start()

    def notify(self, selected_item):
        label = selected_item["label"]
        print(f"\n========================================")
        print(f" [PATIENT REQUEST NOTIFIED]: {label}")
        print(f"========================================\n")

        self.trigger_buzzer(duration=0.6)
        self.speak(label)

    def cleanup(self):
        if self.rpi_enabled:
            self.GPIO.cleanup()

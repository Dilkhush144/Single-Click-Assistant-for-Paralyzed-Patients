import cv2
import time
from config.settings import load_config
from src.detector import EyeDetector
from src.ui import AssistiveUI
from src.notifier import CaretakerNotifier

def main():
    config = load_config()
    print("=" * 60)
    print(" AI Assistive Vision Communicator - Patient Assistance System")
    print(" Author: Dilkhush Raj | Raspberry Pi & MediaPipe Pipeline")
    print("=" * 60)

    cap = cv2.VideoCapture(config.get("camera_index", 0))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.get("frame_width", 640))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.get("frame_height", 480))

    if not cap.isOpened():
        print("[ERROR] Camera stream could not be initialized.")
        return

    detector = EyeDetector()
    ui = AssistiveUI(config["selection_options"])
    notifier = CaretakerNotifier(config)

    closed_frame_count = 0
    alert_display_timer = 0
    current_alert = None

    EAR_THRESHOLD = config.get("ear_threshold", 0.22)
    NORMAL_BLINK_FRAMES = config.get("consecutive_blink_frames", 3)
    LONG_BLINK_FRAMES = config.get("long_blink_frames", 18)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Mirror view for intuitive user experience
            frame = cv2.flip(frame, 1)

            avg_ear, left_eye, right_eye = detector.get_average_ear(frame)

            # Draw eye contours for visual feedback
            if left_eye and right_eye:
                for pt in left_eye + right_eye:
                    cv2.circle(frame, pt, 1, (0, 255, 0), -1)

            # Blink state machine logic
            if avg_ear is not None:
                if avg_ear < EAR_THRESHOLD:
                    closed_frame_count += 1
                else:
                    if NORMAL_BLINK_FRAMES <= closed_frame_count < LONG_BLINK_FRAMES:
                        # Short blink: Next option
                        ui.next_option()
                    elif closed_frame_count >= LONG_BLINK_FRAMES:
                        # Long blink: Select and dispatch request
                        selected = ui.get_current_option()
                        notifier.notify(selected)
                        current_alert = selected["label"]
                        alert_display_timer = time.time()

                    closed_frame_count = 0

            # Expire alert overlay after 3 seconds
            if current_alert and (time.time() - alert_display_timer > 3.0):
                current_alert = None

            output_frame = ui.draw_interface(
                frame,
                avg_ear,
                closed_frame_count,
                alert_text=current_alert
            )

            cv2.imshow("AI Patient Communicator - Assistive View", output_frame)

            # Exit key: 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        notifier.cleanup()
        print("[INFO] Program terminated gracefully.")

if __name__ == "__main__":
    main()

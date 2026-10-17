"""
Single-Click Assistant for Paralyzed Patients
An Eye-Blink Controlled Smart Assistance and Caregiver Alert System
Department of Electronics and Communication Engineering, National Institute of Technology, Manipur (2026-27)

Authors:
1) Gaurav Kumar Chaudhary (23105026)
2) Rahul Deb (23105031)
3) Dilkhush Raj (23105008)

Under the Guidance of:
Prof. L. Lolitkumar Singh, Dept. of ECE, NIT Manipur
"""

import cv2
import time
from config.settings import load_config
from src.detector import EyeDetector
from src.fsm import MealyBlinkClassifier, SystemState, BlinkGesture
from src.notifier import CaretakerNotifier
from src.ui import AssistiveUI

def main():
    config = load_config()

    print("=" * 72)
    print(" NATIONAL INSTITUTE OF TECHNOLOGY, MANIPUR")
    print(" Department of Electronics and Communication Engineering (2026-27)")
    print(" Single-Click Assistant for Paralyzed Patients")
    print(" Eye-Blink Controlled Smart Assistance & Caregiver Alert System")
    print(" Team: Gaurav Kr. Chaudhary, Rahul Deb, Dilkhush Raj | Guide: Prof. L. Lolitkumar Singh")
    print("=" * 72)

    # 1. Initialize Camera Stream (Slide 11: Step 1 Frame Capture)
    cap = cv2.VideoCapture(config.get("camera_index", 0))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.get("frame_width", 640))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.get("frame_height", 480))

    if not cap.isOpened():
        print("[ERROR] Camera stream could not be initialized. Please check camera index.")
        return

    # 2. Initialize Core Subsystems
    detector = EyeDetector()
    classifier = MealyBlinkClassifier(config)
    state = SystemState(config)
    notifier = CaretakerNotifier(config)
    ui = AssistiveUI(config)

    # Initial eyes-free speech welcome prompt (Slide 8)
    initial_item = state.current_item
    if initial_item and config.get("eyes_free_audio_prompts", True):
        notifier.speak(f"Assistant active. Current option: {initial_item.get('label')}")

    print("\n[READY] System running. Controls:")
    print(" - Short Blink (< 0.5s): Move to Next Option (Read aloud)")
    print(" - Medium Blink (~1.0s): Select Option / Enter Submenu")
    print(" - Long Blink (>= 3.0s): Go Back / Cancel")
    print(" - Press 'q' or 'ESC' on the OpenCV window to terminate.\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARNING] Frame capture dropped.")
                break

            # Mirror frame horizontally for intuitive patient interaction
            frame = cv2.flip(frame, 1)

            # Step 2 & 3: Landmark Extraction & EAR Calculation (MediaPipe + Soukupová & Čech 2016)
            avg_ear, left_eye, right_eye = detector.get_average_ear(frame)

            # Draw subtle green landmarks around eye contours
            if left_eye and right_eye:
                for pt in left_eye + right_eye:
                    cv2.circle(frame, pt, 1, (0, 255, 0), -1)

            # Step 4: Mealy FSM Blink Duration Classification
            gesture, closed_frames, hold_status = classifier.update(avg_ear)

            # Step 5: Moore FSM Menu Navigation & Device Execution
            if gesture != BlinkGesture.NONE:
                action_result = state.handle_gesture(gesture)
                if action_result:
                    notifier.notify_action(action_result)

            # Handle alert message display timeout
            state.check_alert_timeout()

            # Step 6: Render Assistive Dashboard (Menus, Virtual Appliances, Gesture Hold Meter)
            display_frame = ui.draw_interface(
                frame,
                state,
                avg_ear,
                closed_frames,
                hold_status
            )

            cv2.imshow("Single-Click Assistant - Assistive View [NIT Manipur]", display_frame)

            # Keybindings for manual keyboard simulation / exit
            key = cv2.waitKey(1) & 0xFF
            if key in [ord('q'), 27]: # 'q' or ESC
                break
            elif key == ord('n'):     # Keyboard shortcut simulation: Next
                action = state.handle_gesture(BlinkGesture.SHORT)
                if action: notifier.notify_action(action)
            elif key == ord('s'):     # Keyboard shortcut simulation: Select
                action = state.handle_gesture(BlinkGesture.MEDIUM)
                if action: notifier.notify_action(action)
            elif key == ord('b'):     # Keyboard shortcut simulation: Back
                action = state.handle_gesture(BlinkGesture.LONG)
                if action: notifier.notify_action(action)

    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        notifier.cleanup()
        print("[INFO] Application terminated gracefully.")

if __name__ == "__main__":
    main()

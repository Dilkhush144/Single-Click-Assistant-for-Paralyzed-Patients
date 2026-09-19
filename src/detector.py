import cv2
import mediapipe as mp
from src.ear_calculator import LEFT_EYE_LANDMARKS, RIGHT_EYE_LANDMARKS, calculate_ear

class EyeDetector:
    def __init__(self, max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def extract_landmarks(self, frame):
        """Processes RGB video frame and extracts pixel coordinates for both eyes."""
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None, None

        landmarks = results.multi_face_landmarks[0].landmark

        left_eye = [(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in LEFT_EYE_LANDMARKS]
        right_eye = [(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in RIGHT_EYE_LANDMARKS]

        return left_eye, right_eye

    def get_average_ear(self, frame):
        """Calculates combined average EAR across left and right eyes."""
        left_eye, right_eye = self.extract_landmarks(frame)
        if left_eye is None or right_eye is None:
            return None, None, None

        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0

        return avg_ear, left_eye, right_eye

    def close(self):
        self.face_mesh.close()

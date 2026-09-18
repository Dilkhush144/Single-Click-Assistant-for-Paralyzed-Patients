import numpy as np

# MediaPipe 468/478 Face Mesh eye landmark indices
LEFT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]

def euclidean_distance(point_a, point_b):
    """Calculate Euclidean distance between two coordinate pairs."""
    return np.linalg.norm(np.array(point_a) - np.array(point_b))

def calculate_ear(eye_points):
    """
    Compute Eye Aspect Ratio (EAR) based on Soukupová and Čech algorithm.
    EAR = (|p2 - p6| + |p3 - p5|) / (2 * |p1 - p4|)
    """
    if len(eye_points) < 6:
        return 0.0

    p1, p2, p3, p4, p5, p6 = eye_points

    vertical_dist_1 = euclidean_distance(p2, p6)
    vertical_dist_2 = euclidean_distance(p3, p5)
    horizontal_dist = euclidean_distance(p1, p4)

    if horizontal_dist == 0:
        return 0.0

    ear = (vertical_dist_1 + vertical_dist_2) / (2.0 * horizontal_dist)
    return float(ear)

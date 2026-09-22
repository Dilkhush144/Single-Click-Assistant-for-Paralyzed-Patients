# System Architecture & Concurrency Model

## 1. High-Level System Architecture

```text
       [ Live Video Input ] (Pi Camera / Webcam)
                 │
                 ▼
   [ OpenCV Frame Ingestion & Mirroring ]
                 │
                 ▼
     [ MediaPipe FaceMesh Engine ]
                 │ (Extracts 468 3D landmarks)
                 ▼
   [ Eye Landmark Vector Extraction ]
       - Left Eye : [33, 160, 158, 133, 153, 144]
       - Right Eye: [362, 385, 387, 263, 373, 380]
                 │
                 ▼
     [ EAR (Eye Aspect Ratio) Calculator ]
        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
                 │
                 ▼
    [ Temporal Blink State Machine ]
    ├── EAR < Threshold (0.22)  ──> Increment Closed Frames
    └── EAR >= Threshold
         ├── 3 <= Frames < 18   ──> Normal Blink (Next Menu Option)
         └── Frames >= 18       ──> Long Blink (Confirm Selection)
                 │
                 ├───> [ Assistive UI Overlay ] (OpenCV Frame Render)
                 │
                 └───> [ Multithreaded Notifier Engine ]
                         ├── Audio TTS Engine (pyttsx3 Speech Synthesizer)
                         ├── Hardware Buzzer Alarm (RPi GPIO 18)
                         └── LED Indicators (GPIO 23/24/25/12)
```

---

## 2. Mathematical Foundation: Eye Aspect Ratio (EAR)

Traditional blink detection using simple frame differencing fails under fluctuating ambient lighting. This project implements the geometry-invariant Eye Aspect Ratio (EAR) formulation:

$$\text{EAR} = \frac{\|p_2 - p_6\| + \|p_3 - p_5\|}{2 \cdot \|p_1 - p_4\|}$$

Where:
- $p_1, p_4$ represent horizontal boundary corner landmarks of the palpebral fissure.
- $p_2, p_6$ and $p_3, p_5$ represent vertical coordinate pairs across the upper and lower eyelids.

When the eye is open, $\text{EAR}$ hovers between $0.28 - 0.35$. Upon eyelid closure, $\text{EAR}$ plummets rapidly below $0.20$.

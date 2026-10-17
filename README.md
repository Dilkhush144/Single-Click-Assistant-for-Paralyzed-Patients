# 👁️ Single-Click Assistant for Paralyzed Patients
### *Real-Time Eye-Blink Controlled Assistive Workstation & IoT Caregiver Alert System*

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/MediaPipe-FaceMesh-00C7B7?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Raspberry%20Pi-4B-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white" />
  <img src="https://img.shields.io/badge/Architecture-Mealy%20%2B%20Moore%20FSM-FF6F00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" />
</p>

<p align="center">
  <strong>An edge-optimized assistive communication workstation enabling motor-impaired and locked-in patients to control home appliances, communicate routine needs, and dispatch prioritized caregiver alerts through calibrated ocular blinks.</strong>
</p>

<p align="center">
  <strong>Author & Lead Developer:</strong> Dilkhush Raj (<a href="https://github.com/Dilkhush144">@Dilkhush144</a>)
</p>

---

## 📌 Problem Statement & Engineering Motivation

Patients suffering from severe neuro-motor disorders (such as **Amyotrophic Lateral Sclerosis [ALS]**, brainstem stroke, or quadriplegia) frequently experience complete loss of voluntary muscular control and speech, while ocular motor functions (eyelid blinks) remain fully intact.

Traditional hospital nurse-call buttons fail because paralyzed individuals cannot physically exert pressure. Meanwhile, existing assistive eye-trackers often require expensive infrared hardware, cumbersome electrodes, or continuous high-bandwidth internet connectivity.

This project delivers a **standalone, edge-computable, non-invasive assistive workstation**:
1. Tracks involuntary vs. intentional eye blinks in real time using edge computer vision.
2. Formulates a **hierarchical spoken menu** (Needs, Emergency, Entertainment, Room Control).
3. Provides **eyes-free auditory navigation** (each option is read aloud via speech synthesis, allowing bedridden patients to navigate without eye strain).
4. Automates IoT home appliances (room lighting & multi-speed fan control via relays) and provides multi-tone local alarms with network caregiver escalation.

---

## 🌟 Key Capabilities

- **🎯 Zero-Sensor Non-Invasive Vision**: Works entirely through standard camera optical input using Google MediaPipe (468 3D facial landmarks); requires no electrodes, glasses, or wearable hardware.
- **📐 Mathematical EAR Algorithm (Soukupová & Čech)**: Invariant to lighting variations, skin tones, and minor head movement.
- **🎛️ 3-Tier Blink Gesture Classifier (Mealy FSM)**:
  - **Short Blink (< 0.5s)**: Cycles to the **Next** menu item (announced via audio).
  - **Medium Blink (~1.0s)**: **Selects** the item / drills down into submenus.
  - **Long Blink (≥ 3.0s)**: **Cancels / Returns** to the previous menu level.
- **🗣️ Eyes-Free Auditory Prompts**: Spoken text-to-speech announces every option aloud dynamically, enabling complete eyes-free operation.
- **💡 Smart Room Appliance Control (Moore FSM)**: Direct control over room light (Relay ON/OFF) and multi-speed ceiling fan (Speeds 0 to 3).
- **🚨 Fail-Safe Caregiver Alerting**: Immediate priority emergency dispatch with multi-tone local buzzer alarm and network caregiver notification.
- **💻 Dual Deployment Modes**: Runs 100% in **Software Simulation Mode** on any PC/laptop (with virtual appliance dashboard & audio), as well as on physical **Raspberry Pi 4 hardware**.

---

## 🌳 Hierarchical Menu Architecture

```text
Main Menu
├── Needs
│   ├── Water       ──> Speaks "Need Water", notifies caregiver
│   ├── Food        ──> Speaks "Need Food", notifies caregiver
│   ├── Pain        ──> Speaks "Severe Pain assistance needed"
│   └── Washroom    ──> Speaks "Washroom assistance needed"
├── Emergency       ──> PRIORITY ALARM: Triggers local buzzer pattern + caregiver distress alert
├── Entertainment
│   ├── Music       ──> Plays soothing relaxation music
│   └── Movies      ──> Starts audio entertainment stream
└── Room Control
    ├── Light       ──> Toggles Room Light Relay (ON / OFF)
    └── Fan Speed   ──> Cycles Ceiling Fan Speed (OFF ➔ 1 ➔ 2 ➔ 3)
```

---

## 🧠 Engineering & System Design Deep-Dive (Interview Focus)

### 1. Why MediaPipe FaceMesh (468 landmarks) over Haar Cascades or Dlib 68?
- **Sub-millimeter palpebral fissure precision:** Haar Cascades only provide bounding boxes without eyelid distance geometry. Dlib’s 68-point model incurs high CPU latency on embedded processors. MediaPipe FaceMesh runs at **>30 FPS on standard edge CPUs** using 468 3D contour points, providing exact coordinates for both upper and lower eyelid boundaries.

### 2. Geometry-Invariant Blink Formulation (Soukupová & Čech EAR)
- Instead of brittle intensity thresholding or optical flow (which fail under ambient lighting shifts), the system computes the geometric Eye Aspect Ratio:
  $$\text{EAR} = \frac{\|p_2 - p_6\| + \|p_3 - p_5\|}{2 \cdot \|p_1 - p_4\|}$$
- **Thresholding Strategy:** When open, $\text{EAR} \approx 0.28 - 0.35$. Upon eye closure, $\text{EAR}$ drops below $0.22$. Temporal thresholding filters out natural involuntary blinks ($<100\text{ ms}$) while identifying deliberate communication commands.

### 3. Finite State Machine: Mealy & Moore Separation
- **Mealy FSM (`src/fsm.py`):** Operates on continuous EAR streams. State transitions depend on closure frame counts upon eye reopening, emitting discrete events (`SHORT_BLINK`, `MEDIUM_BLINK`, `LONG_BLINK`).
- **Moore FSM (`src/fsm.py`):** Governs system state (active menu level, breadcrumb trails, appliance states, and alert timeouts). Outputs depend strictly on the current state.

### 4. Multithreaded Non-Blocking I/O Architecture
- Text-to-speech (`pyttsx3`) audio synthesis and GPIO relay control are dispatched to dedicated worker threads via thread-safe queues. This ensures that video frame ingestion and landmark extraction never stutter or drop frames during audio announcements.

---

## 🛠️ System Architecture & Tech Stack

| Domain | Technology | Role |
|---|---|---|
| **Platform** | **Raspberry Pi 4 / PC / Laptop** | Core edge processor & runtime environment |
| **Vision AI** | **Google MediaPipe Face Mesh** | Real-time 468-point 3D facial landmark localization |
| **Vision Framework** | **OpenCV (Python)** | Video capture, frame preprocessing, and HUD overlay |
| **Blink Mathematics** | **NumPy & EAR Formulation** | Palpebral fissure vector distance calculation |
| **Speech Synthesizer** | **pyttsx3** | Real-time offline Text-to-Speech audio prompts |
| **Physical I/O** | **RPi.GPIO** | Direct 5V relay control for light/fan and buzzer |

---

## 🚀 Quickstart Guide (Running on Laptop / PC)

You can run the full system right now on your Windows/Linux/Mac laptop without any extra hardware:

### 1. Clone the Repository
```bash
git clone https://github.com/Dilkhush144/Single-Click-Assistant-for-Paralyzed-Patients.git
cd Single-Click-Assistant-for-Paralyzed-Patients
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Raspberry Pi:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Launch the Assistant
```bash
python src/main.py
```

### 4. Interactive Controls
- **Blink Normally**: Natural blinks are filtered out.
- **Short Blink (< 0.5s)**: Cycles to the next menu item with spoken audio prompt.
- **Medium Blink (~1.0s)**: Confirms and selects the current item.
- **Long Blink (≥ 3.0s)**: Returns to previous menu / Cancel.
- **Keyboard Simulation Fallbacks**:
  - `n` = Simulate Short Blink (Next)
  - `s` = Simulate Medium Blink (Select)
  - `b` = Simulate Long Blink (Back)
  - `q` or `ESC` = Exit Application

---

## 🔌 Hardware Deployment (Raspberry Pi 4)

When deploying to physical hardware:
- **Camera**: Raspberry Pi Camera Module v2 (CSI ribbon interface) or USB webcam.
- **Relay 1 (Room Light)**: GPIO Pin 23.
- **Relays 2 & 3 (Fan Speed Control)**: GPIO Pins 24 & 25.
- **Local Alarm Buzzer**: GPIO Pin 18.
- **Status Indicator LED**: GPIO Pin 27.
- **Caregiver Acknowledge Button**: GPIO Pin 17.

Detailed circuit schematics are documented in [`hardware/README.md`](hardware/README.md).

---

## 📚 References

1. S. Soukupová and J. Čech, *"Real-time eye blink detection using facial landmarks,"* in Proc. 21st Computer Vision Winter Workshop (CVWW), 2016.
2. Meghana S., Monica R., Nayana K., and Neha S. S., *"Eye Blink Detection Method for Disabled: Assisting System for Paralyzed,"* IJERT, vol. 8, no. 15, NCAIT, 2020.
3. C. Lugaresi et al., *"MediaPipe: A Framework for Building Perception Pipelines,"* in Proc. 3rd Workshop on Computer Vision for AR/VR at IEEE CVPR, 2019.
4. K. N. D. Malleswararao et al., *"Economic Autonomous Assistive Bot with Cloud Integrated Eye Tracking and Morse Code for Paralyzed Patients,"* IJERD, vol. 21, no. 4, pp. 154-157, Apr. 2025.

## 📄 License
Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

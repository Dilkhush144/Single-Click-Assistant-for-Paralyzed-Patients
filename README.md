# 👁️ Single-Click Assistant for Paralyzed Patients
### *An Eye-Blink Controlled Smart Assistance and Caregiver Alert System*

<p align="center">
  <strong>National Institute of Technology, Manipur</strong><br>
  Department of Electronics and Communication Engineering • B.Tech Project (2026–27)
</p>

<p align="center">
  <strong>Project Team:</strong><br>
  1. <strong>Gaurav Kumar Chaudhary</strong> (Roll: 23105026)<br>
  2. <strong>Rahul Deb</strong> (Roll: 23105031)<br>
  3. <strong>Dilkhush Raj</strong> (Roll: 23105008)<br><br>
  <strong>Under the Guidance of:</strong><br>
  <strong>Prof. L. Lolitkumar Singh</strong><br>
  Department of Electronics and Communication Engineering, NIT Manipur
</p>

---

## 📌 Problem Statement & Motivation

Severe paralysis (caused by Amyotrophic Lateral Sclerosis [ALS], brainstem stroke, or Locked-in Syndrome) robs patients of speech and limb movement while voluntary eye control remains functional. 

Conventional calling buzzers only signal *that* assistance is needed, but cannot specify *what* the patient needs. Existing solutions often suffer from high cost, intrusive electrode headsets, or dependency on uninterrupted internet connectivity.

This project delivers a **standalone, non-invasive eye-blink assistance workstation** that:
1. Detects intentional eye blinks in real time using high-speed vision pipelines.
2. Implements a **hierarchical spoken menu** (Needs, Emergency, Entertainment, Room Control).
3. Reads items aloud so **no screen is strictly required** for the patient (eyes-free operation).
4. Automates home appliances (room lighting & fan speed) and triggers offline local alarms alongside caregiver alerts.

---

## 🌟 Key Capabilities

- **🎯 100% Non-Invasive Optical Tracking**: Uses standard camera input with Google MediaPipe (468 3D landmarks); no heavy electrodes or goggles.
- **📐 Soukupová & Čech (2016) EAR Algorithm**: Invariant to lighting changes, skin tone, and minor head movement.
- **🎛️ 3-Tier Blink Gesture Classification (Mealy FSM)**:
  - **Short Blink (< 0.5s)**: Cycles to the **Next** menu item (read aloud).
  - **Medium Blink (~1.0s)**: **Selects** the item / drills down into submenus.
  - **Long Blink (≥ 3.0s)**: **Cancels / Returns** to the previous menu.
- **🗣️ Eyes-Free Auditory Prompts**: Spoken speech feedback announces every option aloud so bedridden patients can operate the system purely by sound.
- **💡 Smart Room Appliance Control (Moore FSM)**: Direct control over room light (Relay ON/OFF) and multi-speed ceiling fan (Speeds 0 to 3).
- **🚨 Fail-Safe Caregiver Alerting**: Immediate priority emergency dispatch with multi-tone local buzzer alarm and Wi-Fi caregiver notification.
- **💻 Dual Deployment Modes**: Runs 100% in **Software Simulation Mode** on any laptop/PC (with virtual appliance dashboard & audio), as well as on physical **Raspberry Pi 4 hardware**.

---

## 🌳 Hierarchical Menu Tree

```text
Main Menu
├── Needs
│   ├── Water       ──> Speaks "Need Water", notifies caregiver
│   ├── Food        ──> Speaks "Need Food", notifies caregiver
│   ├── Pain        ──> Speaks "Severe Pain assistance needed"
│   └── Washroom    ──> Speaks "Washroom assistance needed"
├── Emergency       ──> Immediate Priority Local Buzzer Alarm + Caregiver Distress Alert
├── Entertainment
│   ├── Music       ──> Plays soothing relaxation music
│   └── Movies      ──> Starts audio entertainment stream
└── Room Control
    ├── Light       ──> Toggles Room Light Relay (ON / OFF)
    └── Fan Speed   ──> Adjusts Ceiling Fan Speed (OFF ➔ 1 ➔ 2 ➔ 3)
```

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

When deploying to physical hardware in the laboratory:
- **Camera**: Raspberry Pi Camera Module v2 (connected via ribbon cable to CSI port).
- **Relay 1 (Room Light)**: GPIO Pin 23.
- **Relays 2 & 3 (Fan Speed)**: GPIO Pins 24 & 25.
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

---

<p align="center">
  Developed for B.Tech Capstone Project 2026–27 • Department of ECE, NIT Manipur
</p>

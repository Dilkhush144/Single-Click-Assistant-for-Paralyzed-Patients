# System Architecture & Finite State Machine Specification

**Project:** Single-Click Assistant for Paralyzed Patients: An Eye-Blink Controlled Smart Assistance and Caregiver Alert System  
**Institution:** Department of Electronics and Communication Engineering, National Institute of Technology, Manipur (2026-27)  
**Authors:** Gaurav Kumar Chaudhary (23105026), Rahul Deb (23105031), Dilkhush Raj (23105008)  
**Supervisor:** Prof. L. Lolitkumar Singh, NIT Manipur  

---

## 1. High-Level System Architecture

```text
       [ Video Capture ] (Pi Camera Module / Laptop Webcam)
                 │
                 ▼
   [ OpenCV Frame Ingestion & Mirroring ]
                 │
                 ▼
     [ MediaPipe FaceMesh Engine ]
                 │ (Extracts 468 3D landmarks in real time)
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
   ┌─────────────────────────────────────────────────────────────┐
   │                   MEALY FINITE STATE MACHINE                │
   │               (Blink Duration Classification)               │
   │                                                             │
   │  EAR < 0.22  ──> Increment closed frame counter             │
   │  EAR >= 0.22 ──> Evaluate closure duration on reopening:    │
   │       ├── Short Blink (3 - 13 frames / ~0.1 - 0.4s)        │
   │       │   └── Output Event: NEXT_ITEM                       │
   │       ├── Medium Blink (16 - 45 frames / ~0.5 - 1.3s)       │
   │       │   └── Output Event: SELECT_ITEM                     │
   │       └── Long Blink (>= 55 frames / ~2.0 - 3.0s)           │
   │           └── Output Event: BACK_CANCEL                     │
   └─────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                   MOORE FINITE STATE MACHINE                │
   │            (Hierarchical Menu & System State Manager)        │
   │                                                             │
   │  States:                                                    │
   │    ├── ROOT_MENU [Needs, Emergency, Entertainment, Room]    │
   │    ├── NEEDS_SUBMENU [Water, Food, Pain, Washroom]          │
   │    ├── ENTERTAINMENT_SUBMENU [Music, Movies]                │
   │    └── ROOM_SUBMENU [Light Toggle, Fan Speed Cycle]         │
   │                                                             │
   │  Appliance Variables:                                       │
   │    ├── Room Light: {OFF, ON}                                │
   │    └── Fan Speed:  {0 (Off), 1 (Low), 2 (Med), 3 (High)}    │
   └─────────────────────────────┬───────────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
     [ Assistive UI Overlay ]       [ Caretaker Notifier Engine ]
     - Landmark tracking contours    - Spoken Audio Prompts (pyttsx3)
     - Live EAR telemetry            - Local Offline Buzzer Alarm
     - Gesture Hold Progress Meter   - Appliance Relays (GPIO 23, 24, 25)
     - Virtual Appliance Dashboard   - Priority Emergency Escalation
```

---

## 2. Mathematical Foundation: Eye Aspect Ratio (EAR)

Following the landmark research by **Soukupová & Čech (2016)**, blink detection relies on the palpebral fissure geometry rather than luminance differences:

$$\text{EAR} = \frac{\|p_2 - p_6\| + \|p_3 - p_5\|}{2 \cdot \|p_1 - p_4\|}$$

Where:
- $p_1, p_4$ are the horizontal boundary landmarks of the eye.
- $p_2, p_6$ and $p_3, p_5$ are vertical landmark pairs across upper and lower eyelids.

Under normal conditions:
- **Open Eye:** $\text{EAR} \approx 0.28 - 0.35$
- **Closed Eye:** $\text{EAR} < 0.20$

---

## 3. Hierarchical Menu Tree & Eyes-Free Auditory Prompts

As specified in the NIT Manipur project design (Slide 8):
- **Eyes-Free Operation:** Each menu item is read aloud upon selection or navigation via text-to-speech. Patients do not need to strain their vision on a screen.

```text
Main Menu
├── Needs
│   ├── Water       ──> Alerts caregiver: "Need Water"
│   ├── Food        ──> Alerts caregiver: "Need Food"
│   ├── Pain        ──> Alerts caregiver: "Severe Pain assistance needed"
│   └── Washroom    ──> Alerts caregiver: "Washroom assistance needed"
├── Emergency       ──> PRIORITY ALARM: Triggers buzzer pattern + caregiver alert
├── Entertainment
│   ├── Music       ──> Plays soothing music stream
│   └── Movies      ──> Starts audio entertainment stream
└── Room Control
    ├── Light       ──> Toggles room light relay ON / OFF
    └── Fan Speed   ──> Cycles fan controller: OFF ➔ 1 ➔ 2 ➔ 3
```

---

## 4. Hardware Deployment vs. Software Simulation

| Component | Hardware Deployment (Raspberry Pi 4) | Software Simulation (PC / Laptop) |
|---|---|---|
| **Video Sensor** | Raspberry Pi Camera Module v2 (CSI) | Laptop Integrated / USB Webcam |
| **Buzzer** | Active 5V Buzzer on GPIO 18 | Audio chime & terminal telemetry |
| **Relay 1 (Light)**| SPDT 5V Relay on GPIO 23 | Virtual light bulb indicator (ON/OFF) |
| **Relay 2 & 3 (Fan)**| Dual Relay Module on GPIO 24 & 25 | Virtual 3-blade animated spinning fan |
| **Audio Output** | 3.5mm Jack / I2S Speaker Amplifier | Laptop Default Audio via pyttsx3 |
| **Ack Button** | Physical Pushbutton on GPIO 17 | Keyboard shortcuts (`n`, `s`, `b`, `q`) |

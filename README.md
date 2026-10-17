# 👁️ Single Click Assistant for Paralyzed Patients
### *Eye-Blink Controlled Smart Assistive System*

<p align="center">
  <strong>Non-Invasive Healthcare Interface • Real-Time Eye Blink Detection • Raspberry Pi & MediaPipe Integration</strong>
</p>

<p align="center">
  An assistive healthcare communication system enabling paralyzed and locked-in patients to communicate daily care requests through single-click calibrated eye blinks using <strong>Raspberry Pi</strong>, <strong>OpenCV</strong>, and <strong>Google MediaPipe</strong>.
</p>

---

## 📌 Problem Statement

Patients afflicted with advanced neurodegenerative diseases (ALS, Locked-in Syndrome) or quadriplegic paralysis cannot vocalize or physically trigger standard call buttons. However, voluntary oculomotor control (eye blinks) frequently remains intact.

This project delivers a **hands-free, non-invasive assistive communication workstation**:
1. Monitors the patient's eyes via high-speed computer vision.
2. Formulates Eye Aspect Ratio (EAR) metrics in real time.
3. Classifies **Normal Blinks** (to scroll through a customizable needs menu) and **Long Blinks** (to lock in and confirm selections).
4. Dispatches immediate multi-modal notifications: visual alerts, hardware buzzer alarms via Raspberry Pi GPIO, and automated text-to-speech synthesized caregiver voice alerts.

---

## 🌟 Key Features

- **🎯 Zero Calibration Headset Needed**: 100% optical and non-invasive; no heavy electrodes, eye-tracking goggles, or intrusive caps.
- **⚡ High-Precision 468-Point FaceMesh**: Powered by Google MediaPipe for millimeter-accurate eye contour detection even under variable head positions.
- **📐 Mathematical EAR Algorithm**: Implements the Soukupová & Čech Eye Aspect Ratio formula, preventing false positives from ambient lighting shifts.
- **🎛️ Dual-State Blink Detection Engine**:
  - **Quick Blink (3–17 frames)**: Increments the menu selection (Cycle: *Need Water* $\to$ *Need Food* $\to$ *Washroom* $\to$ *Emergency*).
  - **Long Sustained Blink (18+ frames)**: Confirms selection and triggers caretaker alerts.
- **🔊 Multi-Channel Dispatch**:
  - **Text-to-Speech (TTS)**: Voice output announces patient needs clearly.
  - **Physical GPIO Alarm**: Drives 5V active buzzer and LED indicator array on Raspberry Pi.
  - **Visual HUD**: On-screen dynamic overlay with EAR telemetry and status confirmation.

---

## 🛠️ System Architecture & Tech Stack

| Domain | Technology / Module | Purpose |
|---|---|---|
| **Edge Compute** | **Raspberry Pi 4 / 3B+ / PC** | On-device execution and hardware interfacing |
| **Vision AI** | **Google MediaPipe Face Mesh** | 468 3D facial landmark localization |
| **Image Processing** | **OpenCV (Python)** | Video streaming, geometric overlays, and UI rendering |
| **Math / Array Logic** | **NumPy** | Vectorized Euclidean distance & EAR computation |
| **Audio Synthesizer** | **pyttsx3** | Offline Text-to-Speech audio notification |
| **Hardware I/O** | **RPi.GPIO** | Direct physical control of buzzers and LED signals |

```text
[Camera Feed] ──> [OpenCV Preprocessing] ──> [MediaPipe Mesh] ──> [EAR Calculation]
                                                                        │
                   ┌────────────────────────────────────────────────────┘
                   ▼
       [Blink Duration Classifier]
       ├── Short Blink: Navigate Option [1 -> 2 -> 3 -> 4]
       └── Long Blink:  Confirm Request ──> [Audio Speech] + [GPIO Buzzer/LEDs]
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Dilkhush144/Single-Click-Assistant-for-Paralyzed-Patients.git
cd Single-Click-Assistant-for-Paralyzed-Patients
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
# On Linux / macOS / Raspberry Pi:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Communicator
```bash
python src/main.py
```
> Press `q` to safely exit the application and release camera resources.

---

## 🔌 Hardware Setup

For complete wiring schematics, resistor values, and pin-out diagrams for Raspberry Pi, review the dedicated guide:  
👉 **[Hardware Interfacing Guide](hardware/README.md)**

---

## 📁 Repository Structure

```text
AI-Assistive-Vision-Patient-Communicator/
├── config/
│   └── settings.py          # Thresholds, GPIO pinouts, and care options
├── docs/
│   └── architecture.md      # Mathematical formulations and dataflow
├── hardware/
│   └── README.md            # Raspberry Pi pinout & circuit wiring guide
├── src/
│   ├── ear_calculator.py    # Vectorized Eye Aspect Ratio math
│   ├── detector.py          # MediaPipe FaceMesh eye tracking module
│   ├── notifier.py          # Multithreaded TTS & GPIO buzzer alerts
│   ├── ui.py                # OpenCV HUD interface
│   └── main.py              # Main real-time execution loop
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## 👨‍💻 Project Developer

**Dilkhush Raj**  
B.Tech — Electronics and Communication Engineering  
National Institute of Technology (NIT) Manipur  

- **GitHub**: [@Dilkhush144](https://github.com/Dilkhush144)  
- **LinkedIn**: [Dilkhush Raj](https://www.linkedin.com/in/dilkhushraj)  
- **Email**: [kdilkhush844@gmail.com](mailto:kdilkhush844@gmail.com)  

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

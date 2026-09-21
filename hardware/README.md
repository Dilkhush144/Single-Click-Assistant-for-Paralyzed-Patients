# Hardware Interfacing Guide: Raspberry Pi & Peripheral Setup

This guide details the physical hardware integration between the **Raspberry Pi 4 / 3B+** and assistive feedback peripherals (Active Buzzer, Status LEDs, and Pi Camera v2).

---

## 1. Component Bill of Materials (BOM)

| Component | Specification | Pin / Interface |
|---|---|---|
| **SBC (Single Board Computer)** | Raspberry Pi 4 Model B (2GB/4GB) | Broadcom BCM2711 |
| **Camera Sensor** | Raspberry Pi Camera Module v2 (8MP Sony IMX219) or USB Web Camera | CSI Ribbon Cable or USB 3.0 |
| **Auditory Alarm** | 5V Active Buzzer Module | GPIO 18 (BCM Pin 12 Physical) |
| **Visual Indicators** | 4x Diffused 5mm LEDs (Blue, Yellow, Green, Red) | GPIO 23, 24, 25, 12 |
| **Current Limiting Resistors** | 4x 330 $\Omega$ Resistors (1/4 Watt) | In series with LED anodes |
| **Display Monitor** | 7" HDMI LCD Screen or external monitor | Micro-HDMI port |

---

## 2. Raspberry Pi GPIO Pinout Mapping

```text
Raspberry Pi 40-Pin Header:
              +3.3V [ 1] [ 2] +5V (Buzzer VCC)
     SDA1 / GPIO 2  [ 3] [ 4] +5V
     SCL1 / GPIO 3  [ 5] [ 6] GND (Common Ground)
            GPIO 4  [ 7] [ 8] GPIO 14 / TXD
               GND  [ 9] [10] GPIO 15 / RXD
           GPIO 17  [11] [12] GPIO 18 (Buzzer Signal OUT)
 (Water)   GPIO 27  [13] [14] GND
 (Food)    GPIO 22  [15] [16] GPIO 23 (LED Blue - Water)
              +3.3V [17] [18] GPIO 24 (LED Yellow - Food)
           GPIO 10  [19] [20] GND
            GPIO 9  [21] [22] GPIO 25 (LED Green - Washroom)
           GPIO 11  [23] [24] GPIO 8
               GND  [25] [26] GPIO 7
                    ...
            GPIO 12 [32] ... (LED Red - Emergency)
```

---

## 3. Circuit Schematic Overview

1. **Buzzer Circuit**:
   - VCC $\to$ Pin 2 (+5V)
   - GND $\to$ Pin 6 (Ground)
   - I/O $\to$ Pin 12 (GPIO 18)
2. **LED Visual Notifications**:
   - Each LED Anode (+) connects through a $330\ \Omega$ resistor to designated GPIO pin.
   - Cathodes (-) tied to Pi Ground bus.

---

## 4. Raspberry Pi OS Setup Commands

Enable the camera interface via raspi-config:
```bash
sudo raspi-config
# Interface Options -> Legacy Camera / Camera -> Enable -> Reboot
```

Test camera feed:
```bash
libcamera-hello --timeout 3000
```

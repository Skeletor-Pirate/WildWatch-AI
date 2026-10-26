# WildWatch Edge Node: Hardware Wiring & Pinout Guide

This guide documents the physical actuator interface for WildWatch edge sensor nodes (Raspberry Pi 4 / NVIDIA Jetson Orin Nano).

---

## 1. GPIO Pinout Mapping

| Component | Function | BCM Pin (Pi / Jetson) | Physical Header Pin | Electrical Stage |
| :--- | :--- | :---: | :---: | :--- |
| **High-Intensity Strobe** | Visual Deterrent | `GPIO 17` | Pin 11 | Optocoupler + 12V MOSFET / Relay |
| **Acoustic Buzzer / Siren**| Directional Sound | `GPIO 27` | Pin 13 | NPN Transistor (2N2222) + 5V Buzzer |
| **Status LED (Network/Sync)**| Heartbeat & Health | `GPIO 22` | Pin 15 | 330Ω Resistor + Green LED |
| **PIR / Motion Trigger** | Optional Wakeup | `GPIO 23` | Pin 16 | 3.3V Digital Input |
| **Ground (GND)** | Common Ground | `GND` | Pin 6 / Pin 9 | System Ground |

---

## 2. Electrical Schematic

```
[ Raspberry Pi / Jetson ]
  GPIO 17 (Pin 11) ----[ 1kΩ ]----> Gate of IRLZ44N MOSFET
                                      |
                                      +----> 12V Ultra-Bright LED Strobe Matrix
                                      |
                                    [ GND ]

  GPIO 27 (Pin 13) ----[ 1kΩ ]----> Base of 2N2222 Transistor
                                      |
                                      +----> 5V Piezoelectric Buzzer (90 dB)
                                      |
                                    [ GND ]

  GPIO 22 (Pin 15) ----[ 330Ω ]---> Green LED ---> [ GND ] (Heartbeat indicator)
```

---

## 3. Power Supply & Solar Resilience
- **Input**: 12V 20W Solar Panel with 12V 7Ah LiFePO4 battery pack.
- **Buck Converter**: High-efficiency 12V to 5.1V 3.5A converter powering the Raspberry Pi / Jetson.
- **Fail-Safe Offline Mode**: If LTE/Wi-Fi connection drops, the local SQLite database (`events_queue.db`) buffers sightings, executes local strobe deterrents autonomously via `fallback.py`, and transmits sync bursts once uplink is restored.

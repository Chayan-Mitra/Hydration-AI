# 💧 Hydration AI

> An intelligent desktop assistant that makes sure you actually drink water — powered by Computer Vision, AI, and a clean real-time dashboard.

---

## 🧠 What is this?

Hydration AI is a smart system that:

- 👁️ Uses **YOLO + MediaPipe** to detect when you're drinking water  
- 🔔 Reminds you to hydrate at regular intervals  
- 📊 Tracks your hydration behavior with a **live graph**  
- 💻 Runs silently in the background like a real desktop app  

This isn’t just a reminder — it’s a **behavior-aware hydration system**.

---

## ⚙️ Features

### 🤖 AI Detection
- Real-time sip detection using:
  - YOLOv8 (object detection)
  - MediaPipe (face + hand tracking)
- Smart logic (not overly strict, not dumb)

### 🔔 Smart Reminders
- Toast notifications using `win10toast`
- Voice alerts using `pyttsx3`

### 📊 Live Hydration Graph
- Real-time sip tracking
- Visual progress over time
- Clean UI powered by `pyqtgraph`

### 🖥️ Desktop App Behavior
- Runs in system tray
- Close → minimize to background
- 🛑 STOP button for full shutdown

---

## 🧱 Tech Stack

- Python 3.10
- OpenCV
- MediaPipe
- Ultralytics YOLOv8
- PyQt5
- PyQtGraph
- Win10Toast
- pyttsx3

---

## 📦 Installation

```bash
git clone https://github.com/your-username/Hydration-AI.git
cd Hydration-AI
python main.py
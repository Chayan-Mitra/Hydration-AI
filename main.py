import sys
import time
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QProgressBar
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject
import threading
import pyttsx3

from logic import HydrationLogic
from vision import VisionSystem

logic = HydrationLogic(interval=10)
vision = VisionSystem()

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

class Communicator(QObject):
    sip_detected = pyqtSignal()

comm = Communicator()

class HydrationApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hydration AI 💧")
        self.setGeometry(300, 200, 420, 350)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: white;
                font-size: 16px;
            }
            QPushButton {
                background-color: #00c8ff;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout()

        self.status_label = QLabel("Status: WAITING ⏳")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.timer_label = QLabel("Next Reminder: --")
        self.timer_label.setAlignment(Qt.AlignCenter)

        self.sip_label = QLabel("Sips: 0")
        self.sip_label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setMaximum(3)

        self.button = QPushButton("Manual Sip 💧")
        self.button.clicked.connect(self.manual_sip)

        layout.addWidget(self.status_label)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.sip_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system)
        self.timer.start(1000)

        comm.sip_detected.connect(self.handle_sip)

        threading.Thread(target=self.vision_loop, daemon=True).start()

    def manual_sip(self):
        logic.register_sip()

    def handle_sip(self):
        logic.register_sip()

    def vision_loop(self):
        import cv2

        while True:
            if logic.active:
                vision.start_camera()
                detected, frame = vision.detect_drink()

                if frame is not None:
                    cv2.imshow("Vision", frame)
                    cv2.waitKey(1)

                if detected:
                    comm.sip_detected.emit()

            else:
                vision.stop_camera()
                time.sleep(1)

    def update_system(self):
        event = logic.update()

        if event == "WAKE":
            speak("Time to drink water")

        self.status_label.setText(f"Status: {logic.status}")
        self.timer_label.setText(f"Next Reminder: {logic.get_remaining_time()}s")
        self.sip_label.setText(f"Sips: {logic.sip_count}")
        self.progress.setValue(logic.sip_count)

    def closeEvent(self, event):
        vision.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HydrationApp()
    window.show()
    sys.exit(app.exec_())
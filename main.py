import sys
import time
import threading
import cv2
import pyqtgraph as pg

from PyQt5.QtWidgets import (
    QApplication, QLabel, QPushButton, QVBoxLayout,
    QWidget, QProgressBar, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon

import pyttsx3
from win10toast import ToastNotifier

from logic import HydrationLogic
from vision import VisionSystem


# -------- SYSTEM INIT --------
logic = HydrationLogic(interval=10)
vision = VisionSystem()

engine = pyttsx3.init()
toaster = ToastNotifier()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def show_toast(title, message):
    threading.Thread(
        target=lambda: toaster.show_toast(title, message, duration=3),
        daemon=True
    ).start()


class Communicator(QObject):
    sip_detected = pyqtSignal()


comm = Communicator()


# -------- MAIN APP --------
class HydrationApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hydration AI 💧")
        self.setGeometry(300, 200, 420, 420)

        # -------- TRAY --------
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon())

        menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.exit_app)

        menu.addAction(show_action)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

        # -------- STYLE --------
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: #e2e8f0;
                font-family: Segoe UI;
            }

            QLabel {
                font-size: 18px;
            }

            QProgressBar {
                border: none;
                height: 20px;
                border-radius: 10px;
                background: #1e293b;
            }

            QProgressBar::chunk {
                border-radius: 10px;
                background-color: #38bdf8;
            }

            QPushButton {
                background-color: #38bdf8;
                border-radius: 12px;
                padding: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #0ea5e9;
            }
        """)

        # -------- UI --------
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

        # -------- GRAPH --------
        self.graph = pg.PlotWidget()
        self.graph.setBackground('#0f172a')
        self.graph.setTitle("Hydration Progress", color="w", size="12pt")

        self.graph.showGrid(x=True, y=True)
        self.graph.setLabel('left', 'Sips')
        self.graph.setLabel('bottom', 'Time (s)')

        self.graph_curve = self.graph.plot(
            pen=pg.mkPen(color=(56, 189, 248), width=3),
            symbol='o',
            symbolSize=6,
            symbolBrush=(56, 189, 248)
        )

        # -------- ADD TO LAYOUT --------
        layout.addWidget(self.status_label)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.sip_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.graph)
        layout.addWidget(self.button)

        self.setLayout(layout)

        # -------- TIMER --------
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system)
        self.timer.start(10000)

        # -------- SIGNAL --------
        comm.sip_detected.connect(self.handle_sip)

        # -------- VISION THREAD --------
        threading.Thread(target=self.vision_loop, daemon=True).start()

    # -------- EXIT --------
    def exit_app(self):
        vision.release()
        self.tray.hide()
        QApplication.quit()

    # -------- SIP --------
    def manual_sip(self):
        logic.register_sip()

    def handle_sip(self):
        logic.register_sip()

    # -------- VISION --------
    def vision_loop(self):
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

    # -------- UPDATE --------
    def update_system(self):
        event = logic.update()

        if logic.active:
            self.progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #22c55e; }"
            )
        else:
            self.progress.setStyleSheet(
                "QProgressBar::chunk { background-color: #64748b; }"
            )

        if event == "WAKE":
            speak("Time to drink water")
            show_toast("Hydration Reminder 💧", "Time to drink water!")

        self.status_label.setText(f"Status: {logic.status}")
        self.timer_label.setText(f"Next Reminder: {logic.get_remaining_time()}s")
        self.sip_label.setText(f"Sips: {logic.sip_count}")
        self.progress.setValue(logic.sip_count)

        # -------- GRAPH UPDATE --------
        if logic.history:
            t0 = logic.history[0][0]
            times = [t - t0 for t, _ in logic.history]
            sips = [s for _, s in logic.history]

            self.graph_curve.setData(times, sips)
            self.graph.enableAutoRange()

    # -------- CLOSE --------
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        show_toast("Hydration AI", "Running in background 💧")


# -------- RUN --------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HydrationApp()
    window.show()
    sys.exit(app.exec_())
# gui.py
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                           QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import sys
from spotlight_core import Spotlight

class SpotlightApp(QWidget):
    def __init__(self):
        super().__init__()
        self.spotlight = None
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def initUI(self):
        self.setWindowTitle("Spotlight - Virtual Camera")
        self.setStyleSheet("""
            QWidget {
                background-color: #1c1c1e;
                color: white;
                font-family: Arial;
            }
        """)

        # Create preview label
        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #2c2c2e;
                border-radius: 10px;
                padding: 5px;
                background-color: #2c2c2e;
            }
        """)
        self.preview_label.setMinimumSize(640, 480)

        # Create control buttons
        self.toggle_button = QPushButton("Start Camera", self)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #0a84ff;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
                padding: 10px 20px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #0060df;
            }
            QPushButton:pressed {
                background-color: #004db2;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_spotlight)

        # Layout setup
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.toggle_button)
        button_layout.addStretch(1)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.preview_label)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(20)

        self.setLayout(main_layout)
        self.resize(800, 600)

    def toggle_spotlight(self):
        if self.timer.isActive():
            self.stop_spotlight()
        else:
            self.start_spotlight()

    def start_spotlight(self):
        try:
            self.spotlight = Spotlight()
            self.spotlight.start_camera()
            self.timer.start(30)  # 30ms refresh rate (~33 fps)
            self.toggle_button.setText("Stop Camera")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not start camera: {str(e)}")
            self.spotlight = None

    def stop_spotlight(self):
        self.timer.stop()
        if self.spotlight:
            self.spotlight.release()
            self.spotlight = None
        self.toggle_button.setText("Start Camera")
        self.preview_label.clear()

    def update_frame(self):
        if not self.spotlight:
            return

        frame = self.spotlight.get_frame()
        if frame is not None:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_pixmap = QPixmap.fromImage(image).scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        self.stop_spotlight()
        event.accept()
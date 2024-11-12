# windows/gui.py
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import sys
from spotlight import Spotlight


class SpotlightApp(QWidget):
    def __init__(self):
        super().__init__()
        self.spotlight = Spotlight()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def initUI(self):
        self.setWindowTitle("Spotlight - Virtual Camera")
        self.setStyleSheet("background-color: #1c1c1e; color: white;")

        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px solid #2c2c2e; border-radius: 10px;")

        self.toggle_button = QPushButton("Start Spotlight", self)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #0a84ff;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0060df;
            }
            QPushButton:pressed {
                background-color: #004db2;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_spotlight)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.toggle_button)
        button_layout.addStretch(1)

        layout = QVBoxLayout()
        layout.addWidget(self.preview_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.resize(800, 600)

    def toggle_spotlight(self):
        if self.timer.isActive():
            self.timer.stop()
            self.spotlight.release()
            self.toggle_button.setText("Start Spotlight")
            self.preview_label.clear()
        else:
            self.spotlight.start_camera()
            self.timer.start(30)
            self.toggle_button.setText("Stop Spotlight")

    def update_frame(self):
        frame = self.spotlight.get_frame()
        if frame is not None:
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.preview_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.spotlight.release()

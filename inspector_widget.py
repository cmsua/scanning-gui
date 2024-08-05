from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QPalette, QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QTextEdit
from inspector import CaptureThread

from config import config

import os
import shutil

import cv2
import numpy


class InspectorWidget(QWidget):
    def __init__(self, name, device) -> None:
        super().__init__()
        self.name = name
        self.device = device

        layout = QVBoxLayout()

        # Title
        label = QLabel(f"{self.name} - {self.device}")
        font = label.font()
        font.setPointSize(font.pointSize() * 2)
        label.setFont(font)
        layout.addWidget(label)

        # Main Area
        main_layout = QHBoxLayout()

        # Text Output
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        pallete = self.log.palette()
        pallete.setColor(QPalette.ColorRole.Base, 0)
        self.log.setPalette(pallete)
        self.log.setFixedWidth(786)
        self.log.setFixedHeight(512)
        main_layout.addWidget(self.log)

        # Image Output
        self.image = QLabel("Not Yet Captured")
        self.image.setFixedWidth(786)
        self.image.setFixedHeight(512)
        main_layout.addWidget(self.image)

        # Add Main Layout
        widget = QWidget()
        widget.setLayout(main_layout)
        layout.addWidget(widget)

        # Start button
        self.start_button = QPushButton("Start Inspection")
        self.start_button.pressed.connect(self.start_inspection)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def start_inspection(self) -> None:
        # Disable interface
        self.start_button.setEnabled(False)
        self.start_button.setText("Inspection In Progress...")

        out_dir = f"{ config.getOutputDir() }/_{ self.name }"

        # Make out dir
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)

        # Clear Log + Image
        self.log.setText("")
        self.image.setText("Not Yet Captured")

        # On line recieve
        def insert_line(line: str) -> None:
            self.log.moveCursor(QTextCursor.MoveOperation.End)
            self.log.insertHtml(line)
            self.log.moveCursor(QTextCursor.MoveOperation.End)

        # On image recieve
        def set_image(image: numpy.ndarray) -> None:
            height, width = image.shape[:2]
            aspect_ratio = width / height
            
            # Load new dimensions
            #height = self.image.maximumHeight()
            #width = int(aspect_ratio * height)
            width = self.image.width()
            height = int(aspect_ratio * width)

            image = cv2.resize(image, (width, height))
            # image = image.scaled(self.image.maximumWidth(), self.image.maximumHeight(), Qt.AspectRatioMode.KeepAspectRatio)
            image = QImage(image.data, width, height, width * 3, QImage.Format.Format_BGR888)
            self.image.setPixmap(QPixmap.fromImage(image))

        # Start scan
        self.scan_thread = CaptureThread(self.device, out_dir)
        self.scan_thread.finished.connect(self.finish_inspection)
        self.scan_thread.line.connect(insert_line)
        self.scan_thread.image.connect(set_image)
        self.scan_thread.start()

    def finish_inspection(self) -> None:
        self.start_button.setText("Start Inspection")
        self.start_button.setEnabled(True)
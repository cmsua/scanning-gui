from PyQt6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QThread, Qt

from config import config
import os

import cv2
from visual_inspection import inspection

class ScanWidget(QWidget):
    def __init__(self, name, device) -> None:
        super().__init__()
        self.name = name
        self.device = device

        layout = QHBoxLayout()

        # Options
        optionsLayout = QFormLayout()
        label = QLabel(self.name)
        font = label.font()
        font.setPointSize(font.pointSize() * 2)
        label.setFont(font)
        optionsLayout.addRow(label)

        label = QLabel(self.device)
        font = label.font()
        font.setPointSize(font.pointSize() * 1.5)
        label.setFont(font)
        optionsLayout.addRow(label)

        self.barcode = QLineEdit()
        self.barcode.setMaxLength(15)
        optionsLayout.addRow(QLabel("Barcode"), self.barcode)

        self.scan_button = QPushButton("Scan")
        self.scan_button.pressed.connect(self.start_scan)

        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)
        self.save_button.pressed.connect(self.save_scan)
        optionsLayout.addRow(self.save_button, self.scan_button)

        optionsWidget = QWidget()
        optionsWidget.setLayout(optionsLayout)
        layout.addWidget(optionsWidget)

        # Scan Out
        self.result_raw = QLabel("Scan result will show here")
        self.result_raw.setMaximumWidth(512)
        self.result_raw.setMaximumHeight(786)
        self.result_raw.setMinimumWidth(512)
        layout.addWidget(self.result_raw)

        # Inspection Out
        self.result = QLabel("Inspection result will show here")
        self.result.setMaximumWidth(512)
        self.result.setMaximumHeight(786)
        self.result.setMinimumWidth(512)
        layout.addWidget(self.result)
        
        layout.addStretch()

        self.setLayout(layout)

    def start_scan(self) -> None:
        # Disable interface
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning In Progress...")
        self.result_raw.setText("Scanning In Progress...")
        self.result.setText("Scanning In Progress...")

        # Make out dir
        if not os.path.exists(config.getOutputDir()):
            os.makedirs(config.getOutputDir())
            
        # Start scan
        self.scan_thread = ScanThread(self.device, f"{ config.getOutputDir() }/_{ self.name }.pnm")
        self.scan_thread.finished.connect(self.finish_scan)
        self.scan_thread.start()

    def finish_scan(self) -> None:
        image_path = f"{ config.getOutputDir() }/_{ self.name }.pnm"
        self.image = cv2.imread(image_path)

        # Set raw image
        height, width, channel = self.image.shape
        image = QImage(self.image.data, width, height, width * 3, QImage.Format.Format_RGB888)
        map = QPixmap(image)
        height = min(self.result_raw.maximumHeight(), map.height())
        width = min(self.result_raw.maximumWidth(), map.width())
        map = map.scaled(height, width, Qt.AspectRatioMode.KeepAspectRatio)
        self.result_raw.setPixmap(map)

        # Run Inspection
        self.inspection_result = inspection.run_inspection(self.image)

        # Set Result image
        height, width, channel = self.inspection_result.annotated.shape
        image = QImage(self.inspection_result.annotated.data, width, height, width * 3, QImage.Format.Format_RGB888)
        map = QPixmap(image)
        height = min(self.result_raw.maximumHeight(), map.height())
        width = min(self.result_raw.maximumWidth(), map.width())
        map = map.scaled(height, width, Qt.AspectRatioMode.KeepAspectRatio)
        self.result.setPixmap(map)

        # Enable interface
        self.scan_button.setEnabled(True)
        self.scan_button.setText("Rescan")
        self.save_button.setEnabled(True)

    # 'Save' the image
    def save_scan(self) -> None:
        out_raw = f"{ config.getOutputDir() }/{ self.barcode.text() }-raw.png"
        out_annotated = f"{ config.getOutputDir() }/{ self.barcode.text() }-annotated.png"

        cv2.imwrite(out_raw, self.image)
        cv2.imwrite(out_annotated, self.inspection_result.annotated)

        self.save_button.setEnabled(False)
        self.scan_button.setText("Scan")
        self.result_raw.setText("Scan result will show here")
        self.result.setText("Inspection result will show here")
        self.barcode.clear()

# Self-explanatory
class ScanThread(QThread):
    def __init__(self, device, out) -> None:
        super().__init__()
        self.device = device
        self.out = out

    def run(self) -> None:
        # Delete if exists
        if os.path.exists(self.out):
            os.remove(self.out)

        # Scan new
        os.system(f"scanimage -d \"{ self.device }\" -o \"{ self.out }\"")
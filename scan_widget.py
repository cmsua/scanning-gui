from PyQt6.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QThread, Qt

from config import config
import os

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
        self.label = QLabel("Scan result will show here")
        label.setMaximumWidth(512)
        label.setMaximumHeight(786)
        label.setMinimumWidth(512)
        layout.addWidget(self.label)
        
        layout.addStretch()

        self.setLayout(layout)

    def start_scan(self) -> None:
        # Disable interface
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning In Progress...")
        self.label.setText("Scanning In Progress...")

        # Make out dir
        if not os.path.exists(config.getOutputDir()):
            os.makedirs(config.getOutputDir())
            
        # Start scan
        self.scan_thread = ScanThread(self.device, f"{ config.getOutputDir() }/_{ self.name }.pnm")
        self.scan_thread.finished.connect(self.finish_scan)
        self.scan_thread.start()

    def finish_scan(self) -> None:
        # Load iamge
        map = QPixmap(f"{ config.getOutputDir() }/_{ self.name }.pnm")
        height = min(self.label.maximumHeight(), map.height())
        width = min(self.label.maximumWidth(), map.width())
        map = map.scaled(height, width, Qt.AspectRatioMode.KeepAspectRatio)
        self.label.setPixmap(map)

        # Enable interface
        self.scan_button.setEnabled(True)
        self.scan_button.setText("Rescan")
        self.save_button.setEnabled(True)

    # 'Save' the image
    def save_scan(self) -> None:
        os.rename(f"{ config.getOutputDir() }/_{ self.name }.pnm", f"{ config.getOutputDir() }/{ self.barcode.text() }.pnm")
        self.save_button.setEnabled(False)
        self.scan_button.setText("Scan")
        self.label.setText("Scan result will show here")
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
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from inspector_widget import InspectorWidget

import sys

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Visual Inspection")
        layout = QVBoxLayout()

        # Add Header
        header = QLabel("Visual Inspection GUI")
        font = header.font()
        font.setPointSize(font.pointSize() * 2)
        header.setFont(font)

        layout.addWidget(header)

        # Scanners
        scanner_layout = QHBoxLayout()
        scanner_layout.addWidget(InspectorWidget("Machine 1", "/dev/ttyACM0"))

        scanner_widget = QWidget()
        scanner_widget.setLayout(scanner_layout)
        layout.addWidget(scanner_widget)
        layout.addStretch()

        widget = QWidget()
        widget.setLayout(layout)

        self.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(widget)
        self.showFullScreen()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('dark')

    window = MainWindow()
    app.exec()
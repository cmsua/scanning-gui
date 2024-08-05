from PyQt6.QtCore import QThread, pyqtSignal

import config

import serial
import logging
import time

import numpy
import cv2

from ansi2html import Ansi2HTMLConverter
converter = Ansi2HTMLConverter()

# Write GCode line and wait for resposne
def write(machine: serial.Serial, line: str, logger: logging.Logger):
    logger.debug(f"Sending: {line}")
    machine.write(f"{line}\n".encode("utf-8"))
    
    # Wait for ok
    while True:
        line = machine.readline().decode("utf-8")
        logger.debug(f"Machine Response: {line}")
        if line == "ok\n":
            break


# Self-explanatory
class CaptureThread(QThread):
    line = pyqtSignal(str)
    image = pyqtSignal(numpy.ndarray)

    def __init__(self, device, out) -> None:
        super().__init__()
        self.device = device
        self.out = out

    def run(self) -> None:
        start_time = time.time()

        # Prepare Logger
        logger = logging.getLogger(self.device)
        log_handlers = [
            logging.FileHandler(f"{self.out}/result.log"),
            SignalHandler(self.line)
        ]
        for handler in log_handlers:
            logger.addHandler(handler)

        # Prepare machine
        logger.info(f"Starting scan to {self.out}")

        logger.info("Opening machine via USB")
        machine = serial.Serial(self.device, 250_000)

        # Prepare Webcam
        logger.info("Opening Webcam")
        webcam = cv2.VideoCapture(0)
        webcam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 4096)
        webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        webcam.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        logger.info("Homing machine")
        # write(machine, "G28 X Y", logger.debug)
        # write(machine, "M400", logger.debug)

        # Capture images
        logger.info("Capturing Images")
        for position in config.config.getTargets():
            # Move to target and then wait
            logger.info(f"Moving to {position}")
            write(machine, f"G0 X{position['x']} Y{position['y']}", logger)
            write(machine, "M400", logger)

            # Waiting to capture image
            logger.info(f"Waiting to capture image.")
            time.sleep(config.config.getPauseTime())

            # Capture Image
            filename = f"{self.out}/X{position['x']}Y{position['y']}.png"
            logger.info(f"Capturing photo to {filename}")

            _, _ = webcam.read() # Flush buffer
            result, image = webcam.read()
            if not result:
                raise RuntimeError("No result loaded from webcam!")
            
            # Pass Image
            self.image.emit(image)

            # Save Image
            cv2.imwrite(filename, image)

        # Return to zero
        logger.info("Moving out of the way")
        write(machine, "G0 X0 Y0", logger)
        write(machine, "M400", logger)
        
        # Finish Capture
        webcam.release()
        machine.close()
        logger.info(f"Image capture completed in {int(time.time() - start_time)}s")

        # Run Visual Inspection
        start_time_2 = time.time()
        
        # TODO Visual Inspection
        # TODO Rename Files

        logger.info(f"Inspection completed in {int(time.time() - start_time_2)}s")
        logger.info(f"Full inspection took {int(time.time() - start_time)}s")

        # Remove Logger Handlers
        for handler in log_handlers:
            logger.removeHandler(handler)
            

class SignalHandler(logging.StreamHandler):
    def __init__(self, signal: pyqtSignal):
        super().__init__()
        self.signal = signal
        self.setFormatter(config.Formatter())

    def emit(self, record: logging.LogRecord):
        self.signal.emit(converter.convert(self.formatter.format(record) + "\n"))
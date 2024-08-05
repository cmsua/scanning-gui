import configparser
import logging
from os import path

# Code from https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
# This formatter is for pretty logs
class Formatter(logging.Formatter):
    grey = "\x1b[37m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[1;31m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)-14s - %(levelname)-7s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: logging.Formatter(grey + format + reset),
        logging.INFO: logging.Formatter(format),
        logging.WARNING: logging.Formatter(yellow + format + reset),
        logging.ERROR: logging.Formatter(red + format + reset),
        logging.CRITICAL: logging.Formatter(bold_red + format + reset)
    }

    def format(self, record):
        return self.FORMATS.get(record.levelno).format(record)
    
# Config Class
class Config:
    def __init__(self, configFile: str) -> None:
        self.config = configparser.ConfigParser()

        # Defaults
        self.config["General"] = {
            "OutputDir": "./data",
            "Points": "0, 0; 0, 100; 200, 0; 200, 200; 0, 0",
            "PauseTime": 0.1,
            "LogLevel": "DEBUG",
        }

        # Read Config, Save
        self.config.read(configFile)
        with open(configFile, 'w') as file:
            self.config.write(file)

        # Setup color logging, log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.getLevelName(self.config["General"].get("LogLevel")))
        ch.setFormatter(Formatter())
        logging.basicConfig(
            level=self.config["General"].get("LogLevel").upper(),
            handlers=[ch]
        )

    def getTargets(self) -> list:
        points = self.config["General"].get("Points").split(";")
        points = [ point.strip().split(",") for point in points ]
        return [ {"x": int(point[0].strip()), "y": int(point[1].strip())} for point in points ]

    def getOutputDir(self) -> str:
        return path.abspath(self.config["General"].get("OutputDir"))
    
    def getPauseTime(self) -> float:
        return self.config["General"].getfloat("PauseTime")

config = Config("config.ini")
import configparser
import logging
from os import path

# Config Class
class Config:
    def __init__(self, configFile: str) -> None:
        self.config = configparser.ConfigParser()

        # Defaults
        self.config["General"] = {
            "OutputDir": "./data",
        }

        # Read Config, Save
        self.config.read(configFile)
        with open(configFile, 'w') as file:
            self.config.write(file)

    def getOutputDir(self) -> str:
        return path.abspath(self.config["General"].get("OutputDir"))

config = Config("config.ini")
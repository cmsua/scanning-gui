# Hexaboard Visual Inspection GUI
## University of Alabama

## Installation

This repository is designed to install from source.

This GUI was built on AlmaLinux 9 and uses command-line tools to scan files.

```bash
# Clone the Repository
git clone --recursive https://github.com/cmsua/scanning-gui.git
cd scanning-gui

# Setup a Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
# **LASERS**

## Installing

# LASERS

[Proposal for Undergraduate Research Opportunity Program](https://docs.google.com/document/d/1Zs-3Oz4RHg5y4TUKqVspDdzgsVqdx_FvKxMJN8ncZs8/edit?usp=sharing)

[Design Review Poster](https://docs.google.com/presentation/d/1s7Md1SMyu5eshy5V6Pu0rfp4BjMkpyDq/edit?usp=sharing&ouid=111285953818455480942&rtpof=true&sd=true)

## Description

Software to support an environment sensitive laser show device

[Hardware Schematic](https://docs.google.com/document/d/1tKLXK8S47ILp-UKqPA8MeWQIL5mXLm_fEFIxwtPoTZU/edit?usp=sharing)

[Software Systems Diagram](https://drive.google.com/file/d/1JRHrKc23knE8jHwocKXcX61SSdG1veRA/view?usp=sharing)

[Audio Processing Pipeline Diagram](https://drive.google.com/file/d/1XEXewiZxPbybltlxubsjz2IEPeYOthq3/view?usp=sharing)

## Getting Started

### Dependencies

Device Microcontroller

- Ubuntu for Raspberry Pi 3B (or similar microcontroller)
- Python 3.10
- See required Python packages in laser_device/requirements.txt

Personal Computer

- Python 3.10
- See required Python packages in laser_gui/requirements.txt

### Installing

Installing on device microcontroller (Laser device)

- SSH into Raspberry Pi (or similar microcontroller)
- Install repo
- Create Python virtual environments and install dependencies

```
git clone https://github.com/awtsui/lasers.git
cd lasers
cd laser_device
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Installing on personal computer (GUI device)

- Install repo
- Create Python virtual environments and install dependencies

```
git clone https://github.com/awtsui/lasers.git
cd lasers
cd laser_gui
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Executing program

Executing laser device program

- Verify integrity of hardware system
- Power device and verify that the microcontroller is connected to WiFi
- Navigate to /laser_device and run main.py
- Take note of device's IP address

```
cd laser_device
source env/bin/activate
python main.py
```

Executing GUI program

- Verity personal computer is connected to same network as laser device
- Navigate to /laser_gui and run main.py
- Using GUI, navigate to ip address drop down menu and select laser device's ip address
- Enter 5000 for Port
- Connect to device and notice GUI change to device settings control screen

```
cd laser_gui
source env/bin/activate
python main.py
```

## Authors

- Alvin T.
- Sakeena F.
- Adam S.

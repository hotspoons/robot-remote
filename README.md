# Robot Remote 

A simple python-based remote control for a Freenove 3-wheel "smart car" 
that can control the car locally (e.g. wireless gamepad connected to the 
onboard Raspberry Pi) or remotely (e.g. using a web browser on another PC 
with a connected gamepad).

If using the Freenove mjpeg streamer bundled with their Bitbucket 
repository [HERE](https://github.com/Freenove/Freenove_Three-wheeled_Smart_Car_Kit_for_Raspberry_Pi),
the stream be embedded in the web UI for this application if it is available

## Requirements

This has only been tested on a Raspberry Pi 4 with Raspberry Pi OS, but 
there is nothing preventing it from running on other OSes or hardware. The 
following libraries and runtimes are required for this to function on Pi OS:

 - Python 3 and pip for Python 3
 - The following python libraries: flask, flask-classful, flask-socketio, pygame, smbus
 - I2C interface enabled on the Raspberry Pi (see ~page 38 in Freenove's instructions)
 - For video streaming, see MJPEG streaming section below
 
## Getting started

To clone this repository and all necessary libraries, perform the following

```bash
# - Follow instructions for enabling I2C bus on the Raspberry Pi
sudo apt-get install -y python3 python3-pip i2c-tools
pip3 install flask flask-classful flask-socketio pygame smbus
sudo mkdir /opt/robot-remote
sudo chown -R pi:pi /opt/robot-remote
cd /opt
git clone https://github.com/hotspoons/robot-remote.git robot-remote
```

## Configuration

Currently, configuration is set by modifying values in control/config.py.
I will add the option to create an external configuration file soon.

If you only want to hook up a gamepad (hopefully wireless) to your robot
and drive it around, change the value of Config.mode from "Mode.SERVER"
to "Mode.LOCAL". 

You may need to update AXIS_MAP and ACTIONS_MAP to correspond to the correct
axes and actions on your controller.

## Installing as a startup service

To install this as systemd service, perform the following:

```bash
sudo su
echo "" > /lib/systemd/system/robot-remote.service
echo "[Unit]" >> /lib/systemd/system/robot-remote.service
echo "Description=Robot Remote" >> /lib/systemd/system/robot-remote.service
echo "After=network-online.target" >> /lib/systemd/system/robot-remote.service
echo ""  >> /lib/systemd/system/robot-remote.service
echo "[Service]" >> /lib/systemd/system/robot-remote.service
echo "ExecStart=/usr/bin/python3 /opt/robot-remote/main.py" >> /lib/systemd/system/robot-remote.service
echo "WorkingDirectory=/opt/robot-remote/" >> /lib/systemd/system/robot-remote.service
echo "StandardOutput=inherit" >> /lib/systemd/system/robot-remote.service
echo "StandardError=inherit" >> /lib/systemd/system/robot-remote.service
echo "Restart=always" >> /lib/systemd/system/robot-remote.service
echo "User=pi" >> /lib/systemd/system/robot-remote.service
echo ""  >> /lib/systemd/system/robot-remote.service
echo "[Install]" >> /lib/systemd/system/robot-remote.service
echo "WantedBy=multi-user.target" >> /lib/systemd/system/robot-remote.service

sudo systemctl enable robot-remote.service
sudo systemctl start robot-remote.service
```

## MJPEG streaming

If you wish to use the mjpeg streaming service from Freenove's repository, 
you can install it as a systemd service by doing the following:

```bash
sudo apt-get install -y libv4l-dev libjpeg8-dev imagemagick python3-pyqt5 python3-pyqt5.qtwebkit python3-dev subversion
sudo su
cd /opt
git clone https://github.com/Freenove/Freenove_Three-wheeled_Smart_Car_Kit_for_Raspberry_Pi.git robot

touch /opt/robot/robot-server.sh
chmod +x touch /opt/robot/robot-server.sh
chown -R pi:pi robot
echo "#!/bin/bash" >> /opt/robot/robot-server.sh
echo "cd /opt/robot/Server" >> /opt/robot/robot-server.sh
echo "DISPLAY=:0 python3 Main.py -mnt" >> /opt/robot/robot-server.sh

echo "" > /lib/systemd/system/robot-server.service
echo "[Unit]" >> /lib/systemd/system/robot-server.service
echo "Description=Robot Service" >> /lib/systemd/system/robot-server.service
echo "After=network-online.target" >> /lib/systemd/system/robot-server.service
echo ""  >> /lib/systemd/system/robot-server.service
echo "[Service]" >> /lib/systemd/system/robot-server.service
echo "ExecStart=/bin/bash /opt/robot/robot-server.sh" >> /lib/systemd/system/robot-server.service
echo "WorkingDirectory=/opt/robot/" >> /lib/systemd/system/robot-server.service
echo "StandardOutput=inherit" >> /lib/systemd/system/robot-server.service
echo "StandardError=inherit" >> /lib/systemd/system/robot-server.service
echo "Restart=always" >> /lib/systemd/system/robot-server.service
echo "User=pi" >> /lib/systemd/system/robot-server.service
echo ""  >> /lib/systemd/system/robot-server.service
echo "[Install]" >> /lib/systemd/system/robot-server.service
echo "WantedBy=multi-user.target" >> /lib/systemd/system/robot-server.service

sudo systemctl enable robot-server.service
sudo systemctl start robot-server.service

```

## TODOs
 - Externalize configuration
 - Possibly integrated h264 streaming if I can figure out hardware acceleration
 - Configurable input on the web client
 - Finish writing python client 

inputs# Robot Remote 

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
 - GStreamer and GStreamer python 3 bindings
 - The following python libraries: flask, flask-classful, flask-socketio, pygame, smbus
 - I2C interface enabled on the Raspberry Pi (see ~page 38 in Freenove's instructions)
 - For video streaming, see MJPEG streaming section below
 
## Getting started

To clone this repository and all necessary libraries, perform the following

```bash
# - Follow instructions for enabling I2C bus on the Raspberry Pi
sudo apt-get install -y python3 python3-pip i2c-tools python3-gst-1.0 gstreamer1.0-omx-rpi-config libgstrtspserver-1.0-dev python3-sdl2
pip3 install flask flask-classful flask-socketio approxeng.input smbus websockets
sudo mkdir /opt/robot-remote
sudo chown -R pi:pi /opt/robot-remote
cd /opt
git clone https://github.com/hotspoons/robot-remote.git robot-remote
```

## Configuration

Configuration is set by providing a valid JSON file with the following 
structure, and running the application with the argument " --conf=</path/to/configfile.json>":

```JavaScript

{
	 // The MJPEG URL to embed from your robot, null if none. Hostname 
	 // auto-resolves to the name of the server
	 
    "mjpeg_url": "http://{hostname}:8090/?action=stream",
    
    // Future use :)
    
    "h264_url": null,
    
    // SERVER or LOCAL. Server exposes a web UI that can remote control 
    // your robot through a web browser by accessing it's IP address
    // and the port listed below, using the gamepad API in the browser. 
    // Local allows you to remote control the robot with any gamepad SDL 
    // can read, wireless hopefully :)
    
    "mode": "SERVER",
    
    // Binding address for server, or "0.0.0.0" for all 
    
    "address": "0.0.0.0",
    
    // The port that the server runs on for HTTP service, REST, and WebSockets
    
    "port": 9090,
    
    // How often in seconds that the controller state, either over 
    // WebSockets/REST or locally, is polled for its state.
    
    "sampling_frequency": 0.06,
    
    // How long since the last update from an HTTP client to consider
    // the connection lost, so the robot stops in place instead of heading
    // on its current trajectory
    
    "server_state_update_timeout": 1.0,
    
    // SDL or web gamepad axis mapping to tuples that represent 
    // vectors for the robot to move or look
    
    "AXIS_MAP": {
        "0": ["LEFT", "RIGHT"],
        "1": ["FORWARD", "REVERSE"],
        "2": ["LOOK_LEFT", "LOOK_RIGHT"],
        "3": ["LOOK_UP", "LOOK_DOWN"]
    },
    
    // SDL or web gamepad button mapping to the various 
    // logic outputs the Freenove robot has
    
    "ACTIONS_MAP":{
        "0":"G_TOGGLE",
        "1":"R_TOGGLE",
        "3":"B_TOGGLE",
        "4":"BEEP"
    }
}

```

## Running

If you just want to run the program, run the following, adjusting the
path of the configuration file and program folder as necessary

```bash
python3 /path/to/robot-remote/main.py --conf=/path/to/robot-remote/config.json
# OR
cd /path/to/robot-remote
cd ..
python -m robot-remote --conf=/path/to/robot-remote/config.json
```

## Installing as a startup service

To install this as systemd service, perform the following, adjusting
paths as necessary. Also note the location of the config file; change this
if you want to use another location:

```bash
sudo su
echo "" > /lib/systemd/system/robot-remote.service
echo "[Unit]" >> /lib/systemd/system/robot-remote.service
echo "Description=Robot Remote" >> /lib/systemd/system/robot-remote.service
echo "After=network-online.target" >> /lib/systemd/system/robot-remote.service
echo ""  >> /lib/systemd/system/robot-remote.service
echo "[Service]" >> /lib/systemd/system/robot-remote.service
echo "ExecStart=/usr/bin/python3 /opt/robot-remote/main.py --conf=/opt/robot-remote/config.json" >> /lib/systemd/system/robot-remote.service
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
 - ~~Externalize configuration~~
   - Done, see config.json for an example
 - Possibly integrated h264 streaming if I can figure out hardware acceleration
   - Researching using WebRTC for transport, it involves a lot of setup and requires SSL either being correctly setup with a local CA installed on your LAN's workstation and correctly signed certificates, or adding exceptions. It is definitely possible though, I will continue to research
 - Configurable input on the web client
 - ~~Finish writing python client~~
   - I think I am going to abandon this since the Web UI works just fine, and I don't see much of a use case for this
 - Better packaging of application (this was my first time writing more than a couple of lines of Python in 10 years, so I am a little rusty and behind the times)

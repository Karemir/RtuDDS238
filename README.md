# RtuDDS238
Python code to read Hiking DDS238-2 ZN/S energy meter via RS485 RTU

This also contains code for rtu device simulator on arduino.

# Instructions
This is mostly a reminder for myself.
1. Setup port and baud rate for the device in ddsReader.py file
1. Setup /etc/rc.local to autostart ddsReader and server (remember to put & and each command)
1. Start the ddsReader.py
1. Start webserver in proper directory, ex. 'cd xx; python -m SimpleHTTPServer 8000'

# Notice
This is a project for fun. Don't take it seriously.
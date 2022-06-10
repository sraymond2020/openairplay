#!/usr/bin/env python3

#  Copyright (C) 2015-2016 Ben Klein. All rights reserved.
#
#  This application is licensed under the GNU GPLv3 License, included with
#  this application source.

import sys
from dataclasses import dataclass

# from PyQt6 import QtWidgets

global DEBUG
DEBUG = True

if __name__ == '__main__':
    print("Use main.py instead.")
    sys.exit();

# Qt GUI stuff
# try:
#     from PyQt6 import QtCore, QtGui
#     from PyQt6.QtCore import QSettings
# except ImportError:
#     print("There was an error importing the Qt python3 libraries,")
#     print("These are required by to operate this program.")
#     print("If you are on Ubuntu/Debian, they should be available via APT.")
#     sys.exit("Could not import Python3 Qt Libraries.")


class Device(object):
    def __init__(self, info) -> None:
        self.type = info.type
        self.name = info.name
        self.addresses = info.addresses
        self.port = info.port
        self.weight = info.weight
        self.priority = info.priority
        self.server = info.server
        self.interface_index = info.interface_index


class AirplayDevice(Device):
    def __init__(self, info):
        print("Airplay")
        super().__init__(info)
        self.id = info.properties[b'deviceid']
        self.features = info.properties[b'features']
        self.flags = info.properties[b'flags']
        self.model = info.properties[b'model']
        self.pk = info.properties[b'pk']
        self.pi = info.properties[b'pi']
        self.srcvers = info.properties[b'srcvers']
        self.osvers = info.properties[b'osvers']
        self.properName = str(self.name).replace("._airplay._tcp.local.", "")
        self.vv = info.properties[b'vv']
        self.properType = "Airplay"


class ChromecastDevice(Device):
    def __init__(self, info):
        print("Chromecast")
        super().__init__(info)
        self.id = info.properties[b'id']
        self.cd = info.properties[b'cd']
        self.rm = info.properties[b'rm']
        self.ve = info.properties[b've']
        self.md = info.properties[b'md']
        self.ic = info.properties[b'ic']
        self.fn = info.properties[b'fn']
        self.ca = info.properties[b'ca']
        self.st = info.properties[b'st']
        self.bs = info.properties[b'bs']
        self.nf = info.properties[b'nf']
        self.properName = bytes(self.fn).decode("utf-8")
        self.rs = info.properties[b'rs']
        self.properType = "Chromecast"


#!/usr/bin/env python3

#  Copyright (C) 2015-2016 Ben Klein. All rights reserved.
#
#  This application is licensed under the GNU GPLv3 License, included with
#  this application source.

import re
import sys
import playAirplay
import asyncio

global DEBUG
DEBUG = True

if DEBUG:
    print("Debugging enabled.")
    print("Called with system args: " + str(sys.argv))
    print("Python version: " + sys.version)

# Qt GUI stuff
try:
    from PyQt6 import QtCore, QtGui
    import PyQt6.QtWidgets as QW
    from PyQt6.QtCore import QSettings, Qt
except ImportError:
    print("There was an error importing the Qt python3 libraries,")
    print("These are required by to operate this program.")
    print("If you are on Ubuntu/Debian, they should be available via APT.")
    sys.exit("Could not import Python3 Qt Libraries.")

# Airplay Things:
try:
    import discovery
except:
    sys.exit("Could not import own classes.")

# class Window(QtGui.QDialog):


class Window(QW.QDialog):
    def __init__(self):
        super(Window, self).__init__()

        self.settings = QSettings('open-airplay')
        # Establishes a hook on our system settings.
        # http://pyqt.sourceforge.net/Docs/PyQt6/pyqt_qsettings.html

        # Place items in our window.
        self.createIconGroupBox()  # Tray Icon Settings
        self.createMessageGroupBox()  # Test notification group
        self.createMediaButtonsGroupBox() # Media Buttons for Casting Media
        self.createDeviceListGroupBox()  # Airplay server selection

        # Set the iconlabel to it's minimum width without scollbaring.
        self.iconLabel.setMinimumWidth(self.durationLabel.sizeHint().width())

        # Create action groups to put actionable items into.
        self.createActions()
        self.createTrayIcon()

        # Attach clicks on things to actual functions
        self.showMessageButton.clicked.connect(self.showMessage)
        self.showIconCheckBox.toggled.connect(self.trayIconVisible)
        self.systrayClosePromptCheckBox.toggled.connect(
            self.setSystrayClosePrompt)
        self.iconComboBox.currentIndexChanged.connect(self.setIcon)
        self.trayIcon.messageClicked.connect(self.messageClicked)
        self.trayIcon.activated.connect(self.iconActivated)

        # Finally add the GUI item groupings we made to the layout and init it.
        mainLayout = QW.QVBoxLayout()
        mainLayout.addWidget(self.iconGroupBox)
        mainLayout.addWidget(self.deviceListGroupBox)
        mainLayout.addWidget(self.mediaGroupBox)
        mainLayout.addWidget(self.messageGroupBox)
        self.setLayout(mainLayout)

        # Set our System Tray Presence
        self.iconComboBox.setCurrentIndex(1)
        self.trayIcon.show()
        self.trayIcon.setToolTip("OpenAirplay")

        # Set our basic window things.
        self.setWindowTitle("OpenAirplay Settings")
        self.resize(400, 300)

        # If the user chose not to show the system tray icon:
        if self.settings.value('systrayicon', type=bool) is False:
            print("The user chose not to show the system tray icon.")
            self.trayIconVisible(False)

        # Setup stuff to poll available receivers every 3 seconds.
        self.oldReceiverList = []
        self.timer = QtCore.QTimer()
        self.timer.start(3000)
        self.timer.timeout.connect(self.updateReceivers)

        # Start discovery of airplay receivers:
        if DEBUG:
            print("Starting discovery service...")
        discovery.start()

    def setVisible(self, visible):
        # When we want to 'disappear' into the system tray.
        self.minimizeAction.setEnabled(visible)
        #self.maximizeAction.setEnabled(not self.isMaximized())
        self.restoreAction.setEnabled(self.isMaximized() or not visible)
        super(Window, self).setVisible(visible)

    def closeEvent(self, event):
        # When someone clicks to close the window, not the tray icon.
        if self.trayIcon.isVisible():
            if self.settings.value('promptOnClose_systray', type=bool):
                print("The program is returning to the system tray, user notified.")
                QW.QMessageBox.information(self, "Systray",
                                              "The program will keep running in the system tray. \
                    To terminate the program, choose <b>Quit</b> in \
                    the menu of the system tray airplay icon.")
            else:
                print("Program returned to system tray, user chose not to be notified.")
            self.hide()
            event.ignore()
            print("Closing to System Tray")
        else:
            print("Tray Icon not visible, quitting.")
            self.quit("Exit: No system tray instance to close to.")

    def setIcon(self, index):
        # Sets the selected icon in the tray and taskbar.
        icon = self.iconComboBox.itemIcon(index)
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)

    def setSystrayClosePrompt(self, preference):
        print("Prompt on close is now " + str(preference))
        self.settings.setValue('promptOnClose_systray', preference)

    def trayIconVisible(self, preference):
        self.trayIcon.setVisible(preference)
        self.settings.setValue('systrayicon', preference)

    def iconActivated(self, reason):
        if reason in (
            QW.QSystemTrayIcon.ActivationReason.Trigger, 
            QW.QSystemTrayIcon.ActivationReason.DoubleClick):
            self.iconComboBox.setCurrentIndex(
                (self.iconComboBox.currentIndex() + 1)
                % self.iconComboBox.count())
        elif reason == QW.QSystemTrayIcon.ActivationReason.MiddleClick:
            self.showMessage()

    def showMessage(self):
        # Show the message that was typed in the boxes
        icon = QW.QSystemTrayIcon.MessageIcon(
            self.typeComboBox.itemData(self.typeComboBox.currentIndex()))
        self.trayIcon.showMessage(
            self.titleEdit.text(),
            self.bodyEdit.toPlainText(),
            icon,
            self.durationSpinBox.value() * 1000)

    def selectionChanged(self):
        # Eumerates Selected Device
        r = self.deviceSelectList.currentIndex().row()
        if r > 0:
            name, device = str(self.deviceSelectList.selectedItems()[0].text()).split(": (")
            device = device.replace(")", "")
            if DEBUG:
                # print(device)
                # print(name)
                pass
            deviceCheck = {
                "Airplay": "._airplay._tcp.local.",
                "Chromecast": "._googlecast._tcp.local."
            }
            for k, v in discovery.deviceList.items():
                if str(v.name).find(deviceCheck[device]) > 0:
                    if name == v.properName:
                        print("KEY is: ", k) 
                        print("VALUE is: ", v)
                        print()
                        self.activeDevice = v
                        return
        else:
            self.activeDevice = None
    

    def playMedia(self):
        if self.activeDevice is not None:
            if self.activeDevice.properType == 'Airplay':
                playAirplay.playMedia(bytes(
                    self.activeDevice.id).decode("utf-8"), url="F:\Videos\VueJSCrashCourse2021.mp4")
                # asyncio.run(playAirplay.playMedia(bytes(
                #     self.activeDevice.id).decode("utf-8"), url="F:\Videos\VueJSCrashCourse2021.mp4"))

    def messageClicked(self):
        # In the case that someone clicks on the notification popup (impossible on Ubuntu Unity)
        QW.QMessageBox.information(None, "OpenAirplay Help", "If you need help with OpenAirplay, " 
            "see the Github page to file bug reports or see further documentation and help.")

    def updateReceivers(self):
        # print(discovery.deviceList)
        # print(type(discovery.deviceList))
        if list(set(discovery.airplayReceivers) - set(self.oldReceiverList)) != []:
            # The new list has items oldReceiverList doesn't!
            for item in list(set(discovery.airplayReceivers) - set(self.oldReceiverList)):
                self.oldReceiverList.append(item)
                print("Adding device: " + item)
                # Convert item to string to remove the excess info
                # item = QW.QListWidgetItem(str(item).replace("._airplay._tcp.local.", ""))
                item = QW.QListWidgetItem(
                    # re.sub(r"(-\w*)?._(airplay|googlecast)._tcp.local.", "", str(item))
                    discovery.deviceList[item].properName +
                    ": (" +
                    discovery.deviceList[item].properType +
                    ")"
                    )
                self.deviceSelectList.addItem(item)
        if list(set(self.oldReceiverList) - set(discovery.airplayReceivers)) != []:
            # Items have been removed from the list!
            for item in list(set(self.oldReceiverList) - set(discovery.airplayReceivers)):
                self.oldReceiverList.remove(item)
                print("Removed device: " + item)
                items = self.deviceSelectList.findItems(
                    item, QtCore.Qt.MatchExactly)
                for x in items:
                    self.deviceSelectList.takeItem(
                        self.deviceSelectList.row(x))

    def createIconGroupBox(self):  # Add the SysTray preferences window grouping
        self.iconGroupBox = QW.QGroupBox("Tray Icon")

        self.iconLabel = QW.QLabel("Icon:")

        self.iconComboBox = QW.QComboBox()
        self.iconComboBox.addItem(QtGui.QIcon(
            'images/Airplay-Light'), "Black Icon")
        self.iconComboBox.addItem(QtGui.QIcon(
            'images/Airplay-Dark'), "White Icon")

        self.showIconCheckBox = QW.QCheckBox("Show tray icon")
        self.showIconCheckBox.setChecked(
            self.settings.value('systrayicon', type=bool))
        print("Got systrayicon from settings:" +
              str(self.settings.value('systrayicon', type=bool)))

        self.systrayClosePromptCheckBox = QW.QCheckBox("Systray Close warning")
        self.systrayClosePromptCheckBox.setChecked(
            self.settings.value('promptOnClose_systray', type=bool))
        print("Got promptOnClose_systray from settings:" +
              str(self.settings.value('promptOnClose_systray', type=bool)))

        iconLayout = QW.QHBoxLayout()
        iconLayout.addWidget(self.iconLabel)
        iconLayout.addWidget(self.iconComboBox)
        iconLayout.addStretch()
        iconLayout.addWidget(self.showIconCheckBox)
        iconLayout.addWidget(self.systrayClosePromptCheckBox)
        self.iconGroupBox.setLayout(iconLayout)

    # Creates the device selection list.
    def createDeviceListGroupBox(self):
        self.deviceListGroupBox = QW.QGroupBox("Airplay to")

        self.deviceSelectList = QW.QListWidget()
        deviceSelectListNoDisplayItem = QW.QListWidgetItem("No display.")
        self.deviceSelectList.addItem(deviceSelectListNoDisplayItem)
        self.deviceSelectList.itemSelectionChanged.connect(self.selectionChanged)

        # layout
        deviceListLayout = QW.QHBoxLayout()
        deviceListLayout.addWidget(self.deviceSelectList)
        self.deviceListGroupBox.setLayout(deviceListLayout)

    # Add the Media Buttons GUI window grouping.
    def createMediaButtonsGroupBox(self):
        self.mediaGroupBox = QW.QGroupBox("Media Controller")
    
        self.playButton = QW.QPushButton("Play")
        self.playButton.clicked.connect(self.playMedia)
        self.pauseButton = QW.QPushButton("Pause")
        self.stopButton = QW.QPushButton("Stop")
        self.backButton = QW.QPushButton("Back")
        self.fwdButton = QW.QPushButton("Forward")
        # self.showMessageButton.setDefault(True)

        #layout
        mediaLayout = QW.QHBoxLayout()
        mediaLayout.addWidget(self.backButton)
        mediaLayout.addWidget(self.playButton)
        mediaLayout.addWidget(self.pauseButton)
        mediaLayout.addWidget(self.stopButton)
        mediaLayout.addWidget(self.fwdButton)
        # mediaLayout.addWidget(self.playButton, 1, 1, 1, 1)
        # mediaLayout.addWidget(self.pauseButton, 1, 2, 1, 1)
        # mediaLayout.addWidget(self.stopButton, 1, 3, 1, 1)
        # mediaLayout.setColumnStretch(1, 3)
        # mediaLayout.setRowStretch(1, 1)
        # mediaLayout.setStretch(2, 2)
        self.mediaGroupBox.setLayout(mediaLayout)

    
    # Add the message test GUI window grouping.
    def createMessageGroupBox(self):
        self.messageGroupBox = QW.QGroupBox("Balloon Message Test:")

        typeLabel = QW.QLabel("Type:")

        self.typeComboBox = QW.QComboBox()
        self.typeComboBox.addItem(
            "None", QW.QSystemTrayIcon.MessageIcon.NoIcon)
        self.typeComboBox.addItem(self.style().standardIcon(
            QW.QStyle.StandardPixmap.SP_MessageBoxInformation), "Information", QW.QSystemTrayIcon.MessageIcon.Information)
        self.typeComboBox.addItem(self.style().standardIcon(
            QW.QStyle.StandardPixmap.SP_MessageBoxWarning), "Warning", QW.QSystemTrayIcon.MessageIcon.Warning)
        self.typeComboBox.addItem(self.style().standardIcon(
            QW.QStyle.StandardPixmap.SP_MessageBoxCritical), "Critical", QW.QSystemTrayIcon.MessageIcon.Critical)
        self.typeComboBox.setCurrentIndex(1)

        self.durationLabel = QW.QLabel("Duration:")

        self.durationSpinBox = QW.QSpinBox()
        self.durationSpinBox.setRange(2, 15)
        self.durationSpinBox.setSuffix("s")
        self.durationSpinBox.setValue(5)

        durationWarningLabel = QW.QLabel(
            "(some systems might ignore this hint)")
        durationWarningLabel.setIndent(10)

        titleLabel = QW.QLabel("Title:")

        self.titleEdit = QW.QLineEdit("Cannot connect to network")

        bodyLabel = QW.QLabel("Body:")

        self.bodyEdit = QW.QTextEdit()
        self.bodyEdit.setPlainText(
            "Don't believe me. Honestly, I don't have a clue.")

        self.showMessageButton = QW.QPushButton("Show Message")
        self.showMessageButton.setDefault(True)

        messageLayout = QW.QGridLayout()
        messageLayout.addWidget(typeLabel, 0, 0)
        messageLayout.addWidget(self.typeComboBox, 0, 1, 1, 2)
        messageLayout.addWidget(self.durationLabel, 1, 0)
        messageLayout.addWidget(self.durationSpinBox, 1, 1)
        messageLayout.addWidget(durationWarningLabel, 1, 2, 1, 3)
        messageLayout.addWidget(titleLabel, 2, 0)
        messageLayout.addWidget(self.titleEdit, 2, 1, 1, 4)
        messageLayout.addWidget(bodyLabel, 3, 0)
        messageLayout.addWidget(self.bodyEdit, 3, 1, 2, 4)
        messageLayout.addWidget(self.showMessageButton, 5, 4)
        messageLayout.setColumnStretch(3, 1)
        messageLayout.setRowStretch(4, 1)
        self.messageGroupBox.setLayout(messageLayout)

    def createActions(self):  # Create Actions that can be taken from the System Tray Icon
        self.minimizeAction = QtGui.QAction(
            "Mi&nimize", self, triggered=self.hide)

        # Application is not the kind to be maximized
        # self.maximizeAction = QtGui.QAction("Ma&ximize", self, triggered=self.showMaximized)

        self.restoreAction = QtGui.QAction(
            "&Restore", self, triggered=self.showNormal)

        self.quitAction = QtGui.QAction(
            "&Quit", self, triggered=QW.QApplication.quit)

    def createTrayIcon(self):
        self.trayIconMenu = QW.QMenu(self)
        self.trayIconMenu.addAction(self.minimizeAction)
        # self.trayIconMenu.addAction(self.maximizeAction)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QW.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)

    def quit(self, reason):
        del self.settings
        # discovery.stop()
        sys.exit(reason)


if __name__ == '__main__':

    app = QW.QApplication(['Open Airplay'])
    # app = QtGui.QApplication(['Open Airplay'])

    if not QW.QSystemTrayIcon.isSystemTrayAvailable():
        QW.QMessageBox.critical(
            None, "Systray", "I couldn't detect any system tray on this system.")
        sys.exit(1)

    QW.QApplication.setQuitOnLastWindowClosed(False)

    window = Window()
    window.show()

    # After teh progreem endz:
    sys.exit(app.exec())  # Goodbye World

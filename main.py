#! /usr/bin/env python
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
from espeak import espeak
import random
import time, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class FlashParser():
    def __init__(self, ffile):
        self.f = open(ffile, 'r')
        self.f = self.f.read()
    def parseFlash(self):
        return [i.split('---') for i in self.f.splitlines()]
    def getChoice(self):
        return random.choice(self.parseFlash())

class Speaker(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.delay = 5
        self.fp = FlashParser("trivia.txt")
    def speakTrivia(self):
        trivia = self.fp.getChoice()
        espeak.set_voice("mb-us2")
        espeak.set_parameter(espeak.Parameter.Rate, 2)
        espeak.synth(trivia[0])
        time.sleep(self.delay)
        espeak.synth(trivia[1])
        time.sleep(self.delay*2)
    def run(self):
        while True:
            self.speakTrivia()

class Waiter(QThread):
    def __init__(self, time):
        QThread.__init__(self)
        self.time = time 
    def run(self):
        aw = AlarmWindow(self.time)
        aw.sleepyTime()
        

class AlarmWindow(QDialog):
    def __init__(self):
        super(AlarmWindow, self).__init__()
        layout = QVBoxLayout()
        self.alarmText = QLabel("<font size=800>Wake Up</font>")
        self.stopButton = QPushButton("stop")
        layout.addWidget(self.alarmText)
        layout.addWidget(self.stopButton)
        self.setLayout(layout)
        self.setWindowFlags(Qt.SplashScreen)
        self.stopButton.clicked.connect(self.closeAll)
        self.s = Speaker()

    def closeAll(self):
        self.s.terminate()
        self.hide()

    def sleepyTime(self, alarmTime):
        self.alarmTime = alarmTime
        print "Got alarmtime", self.alarmTime.toString()
        while QTime.currentTime() < self.alarmTime:
            print "sleeping %r", QTime.currentTime()
            time.sleep(20)
        self.show()
        self.s.start()


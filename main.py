#! /usr/bin/env python
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
from espeak import espeak
from FlashCards import *
import time, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *



class Speaker(QThread):
    def __init__(self, flashset):
        QThread.__init__(self)
        self.delay = 5
        self.fp = FlashParser(flashset)
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

    def closeAll(self):
        self.emit(SIGNAL('AlarmClosed'))
        self.s.terminate()
        self.hide()

    def sleepyTime(self, alarmTime,flashset):
        self.alarmTime = alarmTime
        print "Got alarmtime", self.alarmTime.toString()
        while QTime.currentTime() < self.alarmTime:
            print "sleeping %r", QTime.currentTime()
            time.sleep(20)
        self.s = Speaker(flashset)
        self.show()
        self.s.start()


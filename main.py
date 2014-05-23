
#! /usr/bin/env python
import json, os
from alarmwindow import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class AlarmHandler():
    def __init__(self):
        try:
            with open('alarms.json') as f:
                self.alarmsDict = json.load(f)
        except IOError:
            print "no alarms json file found"
            emptyjson = {"active":{}, "nonactive":{}}
            self.alarmsDict= emptyjson
    def addNonActiveAlarm(self, name, time,fset):
        self.alarmsDict["nonactive"][str(name)] = {"time":time, "flashset":fset}
        self.writeAlarmsToJson()
    def addActiveAlarm(self, name, time, fset):
        self.alarmsDict["active"][str(name)] = {"time":time, "flashset":fset}
        self.writeAlarmsToJson()
    def activateAlarm(self, name):
        self.alarmsDict["active"][str(name)] = self.alarmsDict["nonactive"][str(name)]
        del self.alarmsDict["nonactive"][str(name)]
        self.writeAlarmsToJson()
    def deactivateAlarm(self, name):
        self.alarmsDict["nonactive"][str(name)] = self.alarmsDict["active"][str(name)]
        del self.alarmsDict["active"][str(name)]
        self.writeAlarmsToJson()
    def removeActiveAlarm(self, name):
        del self.alarmsDict["active"][str(name)]
        self.writeAlarmsToJson()
    def removeNonActiveAlarm(self, name):
        del self.alarmsDict["nonactive"][str(name)]
        self.writeAlarmsToJson()

    def writeAlarmsToJson(self):
        print "dumping", self.alarmsDict
        with open('alarms.json', 'w') as f:
            json.dump(self.alarmsDict, f)
    def strtoIntTime(self, tobj):
        return int(tobj.replace(':',''))
    def getClosestAlarm(self):
        cur = self.strtoIntTime(str(QTime.currentTime().toString()))
        print "current time:", cur
        nlist = [self.strtoIntTime(k["time"])-cur for i, k in self.alarmsDict["active"].iteritems()]
        sortednlist = [[i for i in nlist if i>0], [abs(i) for i in nlist if i<0]]
        print "list with difference", nlist
        if sortednlist[0]:
            closestAlarm = list(self.alarmsDict["active"].iteritems())[nlist.index(min([e for e in sortednlist[0]]))] 
        else:
            closestAlarm = list(self.alarmsDict["active"].iteritems())[nlist.index(min([-e for e in sortednlist[1]]))] 
        return closestAlarm

class AlarmEditorWindow(QDialog):
    def __init__(self):
        super(AlarmEditorWindow, self).__init__()
        tablelayout = QGridLayout()
        vlayout = QVBoxLayout()
        addalarmlayout = QGridLayout()
        self.alarms = AlarmHandler()
        self.active = QTableWidget()
        self.active.setSelectionBehavior(self.active.SelectRows)  
        self.active.setSelectionMode(self.active.SingleSelection) 
        self.nonactive = QTableWidget()
        self.nonactive.setSelectionBehavior(self.nonactive.SelectRows)
        self.nonactive.setSelectionMode(self.nonactive.SingleSelection) 
        self.removeActiveAlarmButton = QPushButton("Remove")
        self.removeNonActiveAlarmButton = QPushButton("Remove")
        self.active.itemClicked.connect(self.tableClicked)
        self.nonactive.itemClicked.connect(self.tableClicked)
        self.populateTables()
        self.addAlarmName = QLineEdit()
        self.addAlarmName.setPlaceholderText("Alarm Name")

        self.addAlarmTime = QTimeEdit()
        self.addAlarmTime.setTime(QTime.currentTime())
        self.addAlarmButton = QPushButton("Add Alarm")
        self.addAlarmCheck = QCheckBox("Activate?")
        self.addAlarmButton.clicked.connect(self.addAlarm)
        self.removeActiveAlarmButton.clicked.connect(self.removeAlarm)
        self.removeNonActiveAlarmButton.clicked.connect(self.removeAlarm)
        self.startAlarmsButton = QPushButton("Start Alarms")
        self.startAlarmsButton.clicked.connect(self.startAlarms)
        self.fcDropDown = QComboBox()
        self.populateDropDown()
        tablelayout.addWidget(self.active, 0,0)
        tablelayout.addWidget(self.nonactive, 0, 1)
        addalarmlayout.addWidget(self.addAlarmName, 0, 1)
        addalarmlayout.addWidget(self.addAlarmTime, 0, 2)
        addalarmlayout.addWidget(self.addAlarmCheck, 0, 3)
        addalarmlayout.addWidget(self.fcDropDown, 0, 4)
        addalarmlayout.addWidget(self.addAlarmButton, 0, 5)
        vlayout.addLayout(tablelayout)
        vlayout.addWidget(self.removeActiveAlarmButton)
        vlayout.addWidget(self.removeNonActiveAlarmButton)
        self.removeActiveAlarmButton.hide()
        self.removeNonActiveAlarmButton.hide()
        vlayout.addLayout(addalarmlayout)
        vlayout.addWidget(self.startAlarmsButton)
        self.setLayout(vlayout)
        self.setWindowTitle("Smart Alarm")
        aw.closeWindow.connect(self.alarmWindowClosed)
    def alarmWindowClosed(self):
        print "aw closed"
        self.startAlarms()
    def getSelectedName(self, buttonname):
        if(buttonname == self.removeNonActiveAlarmButton):
            row =self.nonactive.selectedIndexes()[0].row()
            return self.nonactive.item(row, 0).text()
        else:
            row =self.active.selectedIndexes()[0].row()
            return self.active.item(row, 0).text()
    def populateTables(self):
        self.populateTable(self.nonactive, self.alarms.alarmsDict["nonactive"])
        self.populateTable(self.active, self.alarms.alarmsDict["active"])

    def populateTable(self,tableobj,alarmobj):
        tableobj.setColumnCount(3)
        tableobj.setRowCount(len(alarmobj))
        tableobj.setHorizontalHeaderLabels(["name", "time", "set"])
        for i, k in enumerate(alarmobj.iteritems()):
            print k
            tableobj.setItem(i, 0, QTableWidgetItem(k[0]))
            tableobj.setItem(i, 1, QTableWidgetItem(k[1]["time"]))
            tableobj.setItem(i, 2, QTableWidgetItem(k[1]["flashset"]))
    def populateDropDown(self):
        files = os.listdir('./sets/')
        self.fcDropDown.clear()
        for i in files:
            self.fcDropDown.addItem(i)
            


    def addAlarm(self):
        if self.addAlarmCheck.isChecked() is True:
            self.alarms.addActiveAlarm(self.addAlarmName.text(), str(self.addAlarmTime.time().toString()), str(self.fcDropDown.currentText()))
        else:
            self.alarms.addNonActiveAlarm(self.addAlarmName.text(), str(self.addAlarmTime.time().toString()), str(self.fcDropDown.currentText()))
        self.populateTables()

    def removeAlarm(self):
        buttonname = self.sender()
        print "Nonactname", self.removeNonActiveAlarmButton
        if(buttonname == self.removeNonActiveAlarmButton):
            self.alarms.removeNonActiveAlarm(self.getSelectedName(buttonname))
        else:
            self.alarms.removeActiveAlarm(self.getSelectedName(buttonname))
        self.populateTables()

    def tableClicked(self, tablename):
        print tablename.tableWidget()
        print self.nonactive
        if(tablename.tableWidget() is self.nonactive):
            self.removeNonActiveAlarmButton.show()
            self.removeActiveAlarmButton.hide()
            self.active.clearSelection()
        else:
            self.removeActiveAlarmButton.show()
            self.removeNonActiveAlarmButton.hide()
            self.nonactive.clearSelection()


    def startAlarms(self):
        try: 
            closestAlarm = self.alarms.getClosestAlarm()
            print "CA", closestAlarm
            closestTime = closestAlarm[1]["time"].split(":")
            self.hide()
            aw.sleepyTime(QTime(int(closestTime[0]), int(closestTime[1])),closestAlarm[1]["flashset"])
        except:
            print "no closest"



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    aw = AlarmWindow()
    t = AlarmEditorWindow()
    t.show()
    sys.exit(app.exec_())







# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Start_Window(object):
    def setupUi(self, Start_Window):
        Start_Window.setObjectName("Start_Window")
        Start_Window.resize(437, 359)
        self.centralwidget = QtWidgets.QWidget(Start_Window)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(30, 20, 181, 261))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.rtbm = QtWidgets.QRadioButton(self.groupBox)
        self.rtbm.setGeometry(QtCore.QRect(40, 50, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.rtbm.setFont(font)
        self.rtbm.setObjectName("rtbm")
        self.aosp = QtWidgets.QRadioButton(self.groupBox)
        self.aosp.setGeometry(QtCore.QRect(40, 120, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.aosp.setFont(font)
        self.aosp.setObjectName("aosp")
        self.vera = QtWidgets.QRadioButton(self.groupBox)
        self.vera.setGeometry(QtCore.QRect(40, 190, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.vera.setFont(font)
        self.vera.setObjectName("vera")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(240, 20, 171, 261))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.online = QtWidgets.QRadioButton(self.groupBox_2)
        self.online.setGeometry(QtCore.QRect(30, 50, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.online.setFont(font)
        self.online.setObjectName("online")
        self.offline = QtWidgets.QRadioButton(self.groupBox_2)
        self.offline.setGeometry(QtCore.QRect(30, 190, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.offline.setFont(font)
        self.offline.setObjectName("offline")
        self.open_btn = QtWidgets.QPushButton(self.centralwidget)
        self.open_btn.setGeometry(QtCore.QRect(30, 290, 381, 41))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.open_btn.setFont(font)
        self.open_btn.setObjectName("open_btn")
        Start_Window.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(Start_Window)
        self.statusbar.setObjectName("statusbar")
        Start_Window.setStatusBar(self.statusbar)

        self.retranslateUi(Start_Window)
        QtCore.QMetaObject.connectSlotsByName(Start_Window)

    def retranslateUi(self, Start_Window):
        _translate = QtCore.QCoreApplication.translate
        Start_Window.setWindowTitle(_translate("Start_Window", "Choose Option - Procee Monitor Tool"))
        self.groupBox.setTitle(_translate("Start_Window", "Please choose device"))
        self.rtbm.setText(_translate("Start_Window", "RTBM"))
        self.aosp.setText(_translate("Start_Window", "AOSP"))
        self.vera.setText(_translate("Start_Window", "Vera"))
        self.groupBox_2.setTitle(_translate("Start_Window", "Please choose Version"))
        self.online.setText(_translate("Start_Window", "Online"))
        self.offline.setText(_translate("Start_Window", "Offline"))
        self.open_btn.setText(_translate("Start_Window", "OPEN"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Start_Window = QtWidgets.QMainWindow()
    ui = Ui_Start_Window()
    ui.setupUi(Start_Window)
    Start_Window.show()
    sys.exit(app.exec_())

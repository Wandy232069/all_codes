# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'command_sub_monitor_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_COMMAND_Dialog(object):
    def setupUi(self, COMMAND_Dialog):
        COMMAND_Dialog.setObjectName("COMMAND_Dialog")
        COMMAND_Dialog.resize(1121, 633)
        self.tableWidget_2 = QtWidgets.QTableWidget(COMMAND_Dialog)
        self.tableWidget_2.setGeometry(QtCore.QRect(10, 110, 601, 511))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.tableWidget_2.setFont(font)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(6)
        self.tableWidget_2.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(5, item)
        self.label_2 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 10, 331, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.plot_view = QChartView(COMMAND_Dialog)
        self.plot_view.setGeometry(QtCore.QRect(619, 110, 491, 250))
        self.plot_view.setObjectName("plot_view")
        self.plot_view1 = QChartView(COMMAND_Dialog)
        self.plot_view1.setGeometry(QtCore.QRect(620, 370, 491, 250))
        self.plot_view1.setObjectName("plot_view1")
        self.label_6 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_6.setGeometry(QtCore.QRect(290, 40, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.label_6.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.label_9 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_9.setGeometry(QtCore.QRect(120, 70, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.label_9.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.mem_high = QtWidgets.QLabel(COMMAND_Dialog)
        self.mem_high.setGeometry(QtCore.QRect(180, 70, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.mem_high.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.mem_high.setFont(font)
        self.mem_high.setAlignment(QtCore.Qt.AlignCenter)
        self.mem_high.setObjectName("mem_high")
        self.cpu_high = QtWidgets.QLabel(COMMAND_Dialog)
        self.cpu_high.setGeometry(QtCore.QRect(180, 40, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.cpu_high.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.cpu_high.setFont(font)
        self.cpu_high.setAlignment(QtCore.Qt.AlignCenter)
        self.cpu_high.setObjectName("cpu_high")
        self.label_4 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_4.setGeometry(QtCore.QRect(20, 70, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_5.setGeometry(QtCore.QRect(120, 40, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.label_5.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.label_3 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_3.setGeometry(QtCore.QRect(20, 40, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.label_8 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_8.setGeometry(QtCore.QRect(290, 70, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.label_8.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.label_10 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_10.setGeometry(QtCore.QRect(470, 70, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.label_10.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.label_10.setFont(font)
        self.label_10.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName("label_10")
        self.mem_low = QtWidgets.QLabel(COMMAND_Dialog)
        self.mem_low.setGeometry(QtCore.QRect(350, 70, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.mem_low.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.mem_low.setFont(font)
        self.mem_low.setAlignment(QtCore.Qt.AlignCenter)
        self.mem_low.setObjectName("mem_low")
        self.mem_avg = QtWidgets.QLabel(COMMAND_Dialog)
        self.mem_avg.setGeometry(QtCore.QRect(530, 70, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.mem_avg.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.mem_avg.setFont(font)
        self.mem_avg.setAlignment(QtCore.Qt.AlignCenter)
        self.mem_avg.setObjectName("mem_avg")
        self.cpu_low = QtWidgets.QLabel(COMMAND_Dialog)
        self.cpu_low.setGeometry(QtCore.QRect(350, 40, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.cpu_low.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.cpu_low.setFont(font)
        self.cpu_low.setAlignment(QtCore.Qt.AlignCenter)
        self.cpu_low.setObjectName("cpu_low")
        self.label_7 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_7.setGeometry(QtCore.QRect(470, 40, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.label_7.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.cpu_avg = QtWidgets.QLabel(COMMAND_Dialog)
        self.cpu_avg.setGeometry(QtCore.QRect(530, 40, 61, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.cpu_avg.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.cpu_avg.setFont(font)
        self.cpu_avg.setAlignment(QtCore.Qt.AlignCenter)
        self.cpu_avg.setObjectName("cpu_avg")
        self.label_15 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_15.setGeometry(QtCore.QRect(590, 40, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_15.setFont(font)
        self.label_15.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_15.setObjectName("label_15")
        self.label_16 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_16.setGeometry(QtCore.QRect(590, 70, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_16.setFont(font)
        self.label_16.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_16.setObjectName("label_16")
        self.label_17 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_17.setGeometry(QtCore.QRect(410, 40, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_17.setFont(font)
        self.label_17.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_17.setObjectName("label_17")
        self.label_18 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_18.setGeometry(QtCore.QRect(410, 70, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_18.setFont(font)
        self.label_18.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_18.setObjectName("label_18")
        self.label_19 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_19.setGeometry(QtCore.QRect(240, 40, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_19.setFont(font)
        self.label_19.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_19.setObjectName("label_19")
        self.label_20 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_20.setGeometry(QtCore.QRect(240, 70, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_20.setFont(font)
        self.label_20.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_20.setObjectName("label_20")
        self.pid_group = QtWidgets.QTextEdit(COMMAND_Dialog)
        self.pid_group.setGeometry(QtCore.QRect(690, 70, 251, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.pid_group.setFont(font)
        self.pid_group.setObjectName("pid_group")
        self.label_11 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_11.setGeometry(QtCore.QRect(630, 70, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_11.setFont(font)
        self.label_11.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName("label_11")
        self.analyze_btn = QtWidgets.QPushButton(COMMAND_Dialog)
        self.analyze_btn.setGeometry(QtCore.QRect(950, 70, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.analyze_btn.setFont(font)
        self.analyze_btn.setObjectName("analyze_btn")
        self.reset_btn = QtWidgets.QPushButton(COMMAND_Dialog)
        self.reset_btn.setGeometry(QtCore.QRect(1030, 70, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.reset_btn.setFont(font)
        self.reset_btn.setObjectName("reset_btn")
        self.label_23 = QtWidgets.QLabel(COMMAND_Dialog)
        self.label_23.setGeometry(QtCore.QRect(630, 40, 431, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.label_23.setFont(font)
        self.label_23.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_23.setObjectName("label_23")

        self.retranslateUi(COMMAND_Dialog)
        QtCore.QMetaObject.connectSlotsByName(COMMAND_Dialog)

    def retranslateUi(self, COMMAND_Dialog):
        _translate = QtCore.QCoreApplication.translate
        COMMAND_Dialog.setWindowTitle(_translate("COMMAND_Dialog", "Command Subprocess Monitor"))
        item = self.tableWidget_2.horizontalHeaderItem(0)
        item.setText(_translate("COMMAND_Dialog", "PID"))
        item = self.tableWidget_2.horizontalHeaderItem(1)
        item.setText(_translate("COMMAND_Dialog", "USER"))
        item = self.tableWidget_2.horizontalHeaderItem(2)
        item.setText(_translate("COMMAND_Dialog", "COMMAND"))
        item = self.tableWidget_2.horizontalHeaderItem(3)
        item.setText(_translate("COMMAND_Dialog", "CPU(%)"))
        item = self.tableWidget_2.horizontalHeaderItem(4)
        item.setText(_translate("COMMAND_Dialog", "MEM(%)"))
        item = self.tableWidget_2.horizontalHeaderItem(5)
        item.setText(_translate("COMMAND_Dialog", "TIME+"))
        self.label_2.setText(_translate("COMMAND_Dialog", "時間："))
        self.label_6.setText(_translate("COMMAND_Dialog", "Low："))
        self.label_9.setText(_translate("COMMAND_Dialog", "High："))
        self.mem_high.setText(_translate("COMMAND_Dialog", "0.0"))
        self.cpu_high.setText(_translate("COMMAND_Dialog", "0.0"))
        self.label_4.setText(_translate("COMMAND_Dialog", "MEM"))
        self.label_5.setText(_translate("COMMAND_Dialog", "High："))
        self.label_3.setText(_translate("COMMAND_Dialog", "CPU"))
        self.label_8.setText(_translate("COMMAND_Dialog", "Low："))
        self.label_10.setText(_translate("COMMAND_Dialog", "Average："))
        self.mem_low.setText(_translate("COMMAND_Dialog", "0.0"))
        self.mem_avg.setText(_translate("COMMAND_Dialog", "0.0"))
        self.cpu_low.setText(_translate("COMMAND_Dialog", "0.0"))
        self.label_7.setText(_translate("COMMAND_Dialog", "Average："))
        self.cpu_avg.setText(_translate("COMMAND_Dialog", "0.0"))
        self.label_15.setText(_translate("COMMAND_Dialog", "%"))
        self.label_16.setText(_translate("COMMAND_Dialog", "%"))
        self.label_17.setText(_translate("COMMAND_Dialog", "%"))
        self.label_18.setText(_translate("COMMAND_Dialog", "%"))
        self.label_19.setText(_translate("COMMAND_Dialog", "%"))
        self.label_20.setText(_translate("COMMAND_Dialog", "%"))
        self.pid_group.setPlaceholderText(_translate("COMMAND_Dialog", "PID,PID,PID....limit five."))
        self.label_11.setText(_translate("COMMAND_Dialog", "Select："))
        self.analyze_btn.setText(_translate("COMMAND_Dialog", "Analyze"))
        self.reset_btn.setText(_translate("COMMAND_Dialog", "Reset"))
        self.label_23.setText(_translate("COMMAND_Dialog", "You can click the PID that you want to draw line chart."))
from PyQt5.QtChart import QChartView


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    COMMAND_Dialog = QtWidgets.QDialog()
    ui = Ui_COMMAND_Dialog()
    ui.setupUi(COMMAND_Dialog)
    COMMAND_Dialog.show()
    sys.exit(app.exec_())

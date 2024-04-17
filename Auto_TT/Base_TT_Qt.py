# -*- coding: utf-8 -*-
import json
import subprocess
import sys
import time

# Form implementation generated from reading ui file 'saw_test_tool.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QTextCursor


class BaseUI(object):
    def __init__(self):
        super().__init__()
        self.adb_command = ["adb"]
        self.base_form = QtWidgets.QWidget()
        self.setup_ui(self.base_form)

    def setup_ui(self, base_form):

        base_form.setObjectName("base_form")
        base_form.resize(750, 800)
        self.gridLayout_2 = QtWidgets.QGridLayout(base_form)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.tabWidget = QtWidgets.QTabWidget(base_form)
        self.tabWidget.setEnabled(True)

        self.tabWidget.setObjectName("tabWidget")
        self.tab_system = QtWidgets.QWidget()
        self.tab_system.setObjectName("tab_system")
        self.gridLayout_config = QtWidgets.QGridLayout(self.tab_system)
        self.gridLayout_config.setObjectName("gridLayout_13")
        self.groupBox_options = QtWidgets.QGroupBox(self.tab_system)
        self.groupBox_options.setObjectName(
            "groupBox_option"
        )
        self.gridLayout_14 = QtWidgets.QGridLayout(self.groupBox_options)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.pushButton_upload_log = QtWidgets.QPushButton(
            self.groupBox_options
        )
        self.pushButton_upload_log.setObjectName("pushButton_upload_log")
        self.gridLayout_14.addWidget(self.pushButton_upload_log, 4, 0, 1, 2)
        self.comboBox_ftp_server = QtWidgets.QComboBox(
            self.groupBox_options
        )
        self.comboBox_ftp_server.setObjectName("comboBox_ftp_server")
        self.comboBox_ftp_server.addItems(["TW_FTP", "CN_FTP"])
        self.gridLayout_14.addWidget(self.comboBox_ftp_server, 3, 1, 1, 1)
        self.checkBox_file_issue_to_jira = QtWidgets.QCheckBox(
            self.groupBox_options
        )

        self.checkBox_file_issue_to_jira.setObjectName("checkBox_file_issue_to_jira")
        self.gridLayout_14.addWidget(self.checkBox_file_issue_to_jira, 0, 0, 1, 2)
        self.checkBox_monkey_test = QtWidgets.QCheckBox(
            self.groupBox_options
        )
        self.checkBox_monkey_test.setObjectName("checkBox_monkey_test")
        self.gridLayout_14.addWidget(self.checkBox_monkey_test, 1, 0, 1, 2)
        self.pushButton_reboot = QtWidgets.QPushButton(
            self.groupBox_options
        )
        self.pushButton_reboot.setObjectName("pushButton_reboot")
        self.pushButton_reboot.clicked.connect(self.reboot_device)
        self.gridLayout_14.addWidget(self.pushButton_reboot, 2, 0, 1, 2)
        self.label_ftp_server = QtWidgets.QLabel(self.groupBox_options)
        self.label_ftp_server.setObjectName("label_ftp_server")
        self.gridLayout_14.addWidget(self.label_ftp_server, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout_14.addItem(spacerItem, 5, 0, 1, 2)
        self.gridLayout_config.addWidget(self.groupBox_options, 0, 1, 1, 1)
        self.groupBox_log_config = QtWidgets.QGroupBox(self.tab_system)
        self.groupBox_log_config.setObjectName("groupBox_log_config")
        self.gridLayout_log_config = QtWidgets.QGridLayout(self.groupBox_log_config)
        self.gridLayout_log_config.setObjectName("gridLayout_option")
        self.label_app_name = QtWidgets.QLabel(self.groupBox_log_config)
        self.label_app_name.setObjectName("label_app_name")
        self.gridLayout_log_config.addWidget(self.label_app_name, 1, 0, 1, 1)
        self.label_project_name = QtWidgets.QLabel(self.groupBox_log_config)
        self.label_project_name.setObjectName("label_project_name")
        self.gridLayout_log_config.addWidget(self.label_project_name, 0, 0, 1, 1)
        self.label_project_name_data = QtWidgets.QLabel(self.groupBox_log_config)
        self.label_project_name_data.setObjectName("label_project_name_data")
        self.gridLayout_log_config.addWidget(self.label_project_name_data, 0, 1, 1, 1)
        self.comboBox_app_name = QtWidgets.QComboBox(self.groupBox_log_config)
        self.comboBox_app_name.setObjectName("comboBox_app_name")
        self.gridLayout_log_config.addWidget(self.comboBox_app_name, 1, 1, 1, 1)
        self.label_tester_name = QtWidgets.QLabel(self.groupBox_log_config)
        self.label_tester_name.setObjectName("label_tester_name")
        self.gridLayout_log_config.addWidget(self.label_tester_name, 2, 0, 1, 1)
        self.label_current_tester = QtWidgets.QLabel(self.groupBox_log_config)
        self.label_current_tester.setText("")
        self.label_current_tester.setObjectName("label_currenct_tester")
        self.gridLayout_log_config.addWidget(self.label_current_tester, 2, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout_log_config.addItem(spacerItem1, 3, 0, 1, 2)
        self.gridLayout_config.addWidget(self.groupBox_log_config, 1, 1, 1, 1)
        self.groupBox_cpu_memory_storage_logcat = QtWidgets.QGroupBox(self.tab_system)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(197, 196, 200))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(197, 196, 200))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(197, 196, 200))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(197, 196, 200))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.groupBox_cpu_memory_storage_logcat.setPalette(palette)
        self.groupBox_cpu_memory_storage_logcat.setObjectName(
            "groupBox_cpu_memory_storage_logcat"
        )
        self.gridLayout_16 = QtWidgets.QGridLayout(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.gridLayout_16.setObjectName("gridLayout_16")
        self.lineEdit_disk_loop = QtWidgets.QLineEdit(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.lineEdit_disk_loop.setObjectName("lineEdit_disk_loop")
        self.gridLayout_16.addWidget(self.lineEdit_disk_loop, 5, 1, 1, 1)
        self.label_memory_interval = QtWidgets.QLabel(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.label_memory_interval.setObjectName("label_memory_interval")
        self.gridLayout_16.addWidget(self.label_memory_interval, 2, 0, 1, 1)
        self.label_cpu_interval = QtWidgets.QLabel(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.label_cpu_interval.setObjectName("label_cpu_interval")
        self.gridLayout_16.addWidget(self.label_cpu_interval, 0, 0, 1, 1)
        self.label_cpu_loop = QtWidgets.QLabel(self.groupBox_cpu_memory_storage_logcat)
        self.label_cpu_loop.setObjectName("label_cpu_loop")
        self.gridLayout_16.addWidget(self.label_cpu_loop, 1, 0, 1, 1)
        self.lineEdit_memory_interval = QtWidgets.QLineEdit(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.lineEdit_memory_interval.setObjectName("lineEdit_memory_interval")
        self.gridLayout_16.addWidget(self.lineEdit_memory_interval, 2, 1, 1, 1)
        self.label_memory_loop = QtWidgets.QLabel(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.label_memory_loop.setObjectName("label_memory_loop")
        self.gridLayout_16.addWidget(self.label_memory_loop, 3, 0, 1, 1)
        self.lineEdit_memory_loop = QtWidgets.QLineEdit(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.lineEdit_memory_loop.setObjectName("lineEdit_memory_loop")
        self.gridLayout_16.addWidget(self.lineEdit_memory_loop, 3, 1, 1, 1)
        self.lineEdit_cpu_loop = QtWidgets.QLineEdit(
            self.groupBox_cpu_memory_storage_logcat
        )

        self.lineEdit_cpu_loop.setInputMask("")
        self.lineEdit_cpu_loop.setText("")
        self.lineEdit_cpu_loop.setObjectName("lineEdit_cpu_loop")
        self.gridLayout_16.addWidget(self.lineEdit_cpu_loop, 1, 1, 1, 1)
        self.lineEdit_cpu_interval = QtWidgets.QLineEdit(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.lineEdit_cpu_interval.setAutoFillBackground(False)
        self.lineEdit_cpu_interval.setInputMask("")
        self.lineEdit_cpu_interval.setText("")
        self.lineEdit_cpu_interval.setObjectName("lineEdit_cpu_interval")
        self.gridLayout_16.addWidget(self.lineEdit_cpu_interval, 0, 1, 1, 1)
        self.label_disk_interval = QtWidgets.QLabel(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.label_disk_interval.setObjectName("label_disk_interval")
        self.gridLayout_16.addWidget(self.label_disk_interval, 4, 0, 1, 1)
        self.lineEdit_disk_interval = QtWidgets.QLineEdit(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.lineEdit_disk_interval.setObjectName("lineEdit_disk_interval")
        self.gridLayout_16.addWidget(self.lineEdit_disk_interval, 4, 1, 1, 1)
        self.label_disk_loop = QtWidgets.QLabel(self.groupBox_cpu_memory_storage_logcat)
        self.label_disk_loop.setObjectName("label_disk_loop")
        self.gridLayout_16.addWidget(self.label_disk_loop, 5, 0, 1, 1)
        self.pushButton_start = QtWidgets.QPushButton(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.pushButton_start.setObjectName("pushButton_start")
        self.pushButton_start.clicked.connect(self.start_log)
        self.gridLayout_16.addWidget(self.pushButton_start, 6, 0, 1, 2)
        self.pushButton_end = QtWidgets.QPushButton(
            self.groupBox_cpu_memory_storage_logcat
        )
        self.pushButton_end.setObjectName("pushButton_end")
        self.pushButton_end.clicked.connect(self.stop_log)
        self.gridLayout_16.addWidget(self.pushButton_end, 8, 0, 1, 2)
        self.gridLayout_config.addWidget(
            self.groupBox_cpu_memory_storage_logcat, 0, 0, 2, 1
        )
        self.gridLayout_config.setColumnStretch(0, 1)
        self.gridLayout_config.setColumnStretch(1, 1)
        self.gridLayout_config.setRowStretch(0, 1)
        self.gridLayout_config.setRowStretch(1, 1)
        self.tabWidget.addTab(self.tab_system, "")
        self.tab_packages = QtWidgets.QWidget()
        self.tab_packages.setObjectName("tab_packages")
        self.gridLayout_17 = QtWidgets.QGridLayout(self.tab_packages)
        self.gridLayout_17.setObjectName("gridLayout_17")
        self.pushButton_uncheck_all = QtWidgets.QPushButton(self.tab_packages)
        self.pushButton_uncheck_all.setObjectName("pushButton_uncheck_all")
        self.pushButton_uncheck_all.clicked.connect(self.uncheck_all)
        self.gridLayout_17.addWidget(self.pushButton_uncheck_all, 3, 3, 1, 2)
        self.groupBox_package2 = QtWidgets.QGroupBox(self.tab_packages)
        self.groupBox_package2.setObjectName("groupBox_package2")
        self.verticalLayout_package2 = QtWidgets.QVBoxLayout(self.groupBox_package2)
        self.verticalLayout_package2.setObjectName("verticalLayout_package2")

        self.gridLayout_17.addWidget(self.groupBox_package2, 0, 3, 3, 2)
        self.pushButton_check_all = QtWidgets.QPushButton(self.tab_packages)
        self.pushButton_check_all.setObjectName("pushButton_check_all")
        self.pushButton_check_all.clicked.connect(self.check_all)
        self.gridLayout_17.addWidget(self.pushButton_check_all, 3, 0, 1, 2)
        self.groupBox_package1 = QtWidgets.QGroupBox(self.tab_packages)
        self.groupBox_package1.setObjectName("groupBox_package1")
        self.verticalLayout_package1 = QtWidgets.QVBoxLayout(self.groupBox_package1)
        self.verticalLayout_package1.setObjectName("verticalLayout_6")

        self.gridLayout_17.addWidget(self.groupBox_package1, 0, 0, 3, 2)
        self.tabWidget.addTab(self.tab_packages, "")
        self.gridLayout_2.addWidget(self.tabWidget, 5, 1, 1, 1)
        self.scrollArea_log = QtWidgets.QScrollArea(base_form)
        self.scrollArea_log.setFrameShadow(QtWidgets.QFrame.Raised)
        self.scrollArea_log.setWidgetResizable(True)
        self.scrollArea_log.setObjectName("scrollArea_log")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 730, 294))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.textEdit_log = QtWidgets.QTextEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.textEdit_log.setFont(font)
        self.textEdit_log.setReadOnly(True)
        self.textEdit_log.setObjectName("textEdit_log")
        self.gridLayout.addWidget(self.textEdit_log, 0, 0, 1, 1)
        self.scrollArea_log.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollArea_log, 6, 1, 1, 1)
        self.label_contributed = QtWidgets.QLabel(base_form)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(71, 71, 71))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(71, 71, 71))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        self.label_contributed.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.label_contributed.setFont(font)
        self.label_contributed.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.label_contributed.setObjectName("label_contributed")
        self.gridLayout_2.addWidget(self.label_contributed, 7, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_device = QtWidgets.QLabel(base_form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.label_device.setFont(font)
        self.label_device.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.label_device.setObjectName("label_device")
        self.horizontalLayout.addWidget(self.label_device)
        self.comboBox_device = QtWidgets.QComboBox(base_form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.comboBox_device.setFont(font)

        self.comboBox_device.setObjectName("comboBox_device")
        self.comboBox_device.currentTextChanged.connect(self.dev_changed)
        self.horizontalLayout.addWidget(self.comboBox_device)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 2)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 1, 1, 1)

        self.translate_ui(base_form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(base_form)

    def translate_ui(self, form):
        _translate = QtCore.QCoreApplication.translate
        form.setWindowTitle(_translate("base_form", "Test Tool Template"))
        self.groupBox_options.setTitle(
            _translate("base_form", "Options")
        )
        self.pushButton_upload_log.setText(_translate("base_form", "Upload log"))
        self.checkBox_file_issue_to_jira.setText(
            _translate("base_form", "File issue to Jira")
        )

        self.checkBox_monkey_test.setText(_translate("base_form", "Monkey test"))
        self.pushButton_reboot.setText(_translate("base_form", "Reboot"))
        self.label_ftp_server.setText(_translate("base_form", "FTP Server"))
        self.groupBox_log_config.setTitle(_translate("base_form", "Log Directory Config"))
        self.label_app_name.setText(_translate("base_form", "App Name"))
        self.label_project_name.setText(_translate("base_form", "Project Name"))
        self.label_tester_name.setText(_translate("base_form", "Tester Name"))
        self.groupBox_cpu_memory_storage_logcat.setTitle(
            _translate("base_form", "CPU / Memory / Storage / logcat")
        )
        self.label_memory_interval.setText(_translate("base_form", "Memory Interval"))
        self.label_cpu_interval.setText(_translate("base_form", "CPU Interval"))
        self.label_cpu_loop.setText(_translate("base_form", "CPU Loop"))
        self.label_memory_loop.setText(_translate("base_form", "Memory Loop"))
        self.label_disk_interval.setText(_translate("base_form", "Disk Interval"))
        self.label_disk_loop.setText(_translate("base_form", "Disk Loop"))
        self.pushButton_start.setText(_translate("base_form", "Start"))
        self.pushButton_end.setText(_translate("base_form", "End"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_system), _translate("base_form", "System")
        )
        self.pushButton_uncheck_all.setText(_translate("base_form", "Uncheck all"))
        self.groupBox_package2.setTitle(_translate("base_form", "Package 2"))

        self.pushButton_check_all.setText(_translate("base_form", "Check all"))
        self.groupBox_package1.setTitle(_translate("base_form", "Package 1"))

        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_packages),
            _translate("base_form", "Packages"),
        )
        self.textEdit_log.setHtml(
            _translate(
                "base_form",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'Arial'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>',
            )
        )
        self.label_contributed.setText(
            _translate("base_form", "Contributed by Auto team")
        )
        self.label_device.setText(_translate("base_form", "Device"))

    def init_packages_tab(self, packages_list: list, test_packages_list: list):
        _translate = QtCore.QCoreApplication.translate
        for i in range(0, int(len(packages_list))):
            if i > int(len(packages_list) / 2):
                group_box = self.groupBox_package2
                vertical_layout = self.verticalLayout_package2
            else:
                group_box = self.groupBox_package1
                vertical_layout = self.verticalLayout_package1
            self.checkbox_package = QtWidgets.QCheckBox(group_box)
            self.checkbox_package.setObjectName("checkbox" + packages_list[i])
            vertical_layout.addWidget(self.checkbox_package)
            self.checkbox_package.setText(_translate("base_form", packages_list[i]))
            if packages_list[i] in test_packages_list:
                self.checkbox_package.click()

    def modify_tester_name(self, text):
        _translate = QtCore.QCoreApplication.translate
        self.label_current_tester.setText(text)

    def change_device(self, device_sn):
        if device_sn != "":
            self.adb_command = ["adb", "-s", device_sn]
        else:
            self.adb_command = ["adb"]

    def start_log(self):
        self.create_log_folder_at_local()
        self.create_log_folder_on_device()
        print("start monitoring")
        pass

    def stop_log(self):
        self.create_log_folder_at_local()
        print("stop monitoring")
        pass

    def create_log_folder_at_local(self):
        pass

    def create_log_folder_on_device(self):
        pass

    def wait_device(self):
        subprocess.call(self.adb_command + ["wait-for-device"])

    def reboot_device(self):
        subprocess.call(self.adb_command + ["reboot"])

    def dev_changed(self, event):
        device_id = self.comboBox_device.currentText()
        self.change_device(device_id)

    def push_file(self, file, location):
        subprocess.call(self.adb_command + ["push", file, location])

    def pull_file(self, file, location):
        subprocess.call(self.adb_command + ["pull", file, location])

    def remove_file(self, file):
        subprocess.call(self.adb_command + ["shell", "rm", "-rf", file])

    def check_all(self):
        for item in self.groupBox_package1.children() + self.groupBox_package2.children():
            if type(item) is QtWidgets.QCheckBox:
                item.setChecked(True)

    def uncheck_all(self):
        for item in self.groupBox_package1.children() + self.groupBox_package2.children():
            if type(item) is QtWidgets.QCheckBox:
                item.setChecked(False)

    def update_test_packages(self, file):
        package_list = []
        for item in self.groupBox_package1.children() + self.groupBox_package2.children():
            if type(item) is QtWidgets.QCheckBox and item.isChecked():
                package_list.append(item.text())

        json_data = json.dumps(package_list, separators=(',', ':'), indent=2)

        # Write JSON data to a file
        with open(file, 'w') as file:
            file.write(json_data)


def modify_eol_to_linux(filename):
    windows_line_end = b'\r\n'
    unix_line_end = b'\n'

    # relative or absolute file path, e.g.:
    with open(filename, 'rb') as open_file:
        content = open_file.read()
    # Windows ➡ Unix
    content = content.replace(windows_line_end, unix_line_end)

    with open(filename, 'wb') as open_file:
        open_file.write(content)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = BaseUI()
    ui.init_packages_tab(["1", "2", "3"], [1, 2, 3])
    ui.base_form.show()
    sys.exit(app.exec_())
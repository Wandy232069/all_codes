import datetime
import io
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

from PyQt5 import QtCore, QtWidgets


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from . import Base_TT_Qt
except (ModuleNotFoundError, ImportError):
    import Base_TT_Qt

try:
    from Auto_TT.modules import log_combiner, DrawLineChart, logcatParserV3, parser_and_create_issue, \
        ftp_tool, QNX_logger
except (ModuleNotFoundError, ImportError):
    from modules import log_combiner, DrawLineChart, logcatParserV3, parser_and_create_issue, \
        ftp_tool, QNX_logger

DUT_LOG_DIRECTORY = "/data/local/tmp/qa/"  # it's android base, have to use /


def resource_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS + os.sep + "PDU_TT"
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path)


ABS_DIR_PATH = resource_path() + os.sep

# Test log directory naming variables
LOG_PDU = ABS_DIR_PATH + "Log_PDU" + os.sep
LOG_DATE = LOG_PDU + time.strftime("%Y_%m_%d", time.localtime()) + os.sep
LOG_PDU_LOGCAT = LOG_DATE + "logcat" + os.sep
LOG_PDU_BUGREPORT = LOG_DATE + "bugreport" + os.sep
LOG_PDU_QA_LOG = LOG_DATE + "qalog" + os.sep
LOG_TIME = time.strftime(
    "%Y_%m_%d-%H_%M_%S", time.localtime()
)
LOG_TIME_DIR = LOG_DATE + os.sep + "outputFolder" + os.sep + LOG_TIME + os.sep

# For device choice

MONITOR_SYSTEM_LIST = ["CPU", "MEM", "DISK"]

config_common = ABS_DIR_PATH + "common.json"
config_package_list = ABS_DIR_PATH + "package_list.json"
config_test_package_list = ABS_DIR_PATH + "test_package_list.json"

SERVER_DIRECTION = r"\\MD-TEST\Projects\PDU\Monkey_log"
LOCAL_DIRECTION = r"D:\Projects\PDU\Monkey_log"


def parsing_bugreport(path, log_time):
    parser_and_create_issue.fetch_data(path, log_time)


def update_config_data(key, value):
    with open(config_common, "r+") as jsonFile:
        data = json.load(jsonFile)
        data[key] = value
        jsonFile.seek(0)  # rewind
        json.dump(data, jsonFile, indent=4)
        jsonFile.truncate()
    get_config_data()


def copy_log_data_to(dir_path, target_path):
    """

    Args:
        dir_path: str, the source directory path, will copy those dirs under the dir_path
        target_path: the destination route to place dirs

    Returns: boolean, True if copy success, False for copy fail

    """
    dir_path = os.path.abspath(dir_path)
    try:
        shutil.copytree(dir_path, target_path, dirs_exist_ok=True)
    except Exception:
        print(sys.exc_info())


def get_config_data():
    """
    get variables in common.json and append initial as global variables
    """
    with open(config_common) as j:
        data = json.load(j)
        for key, values in data.items():
            globals()[key] = values
        j.close()


def get_package_data(filename):
    """
        Get test package list from json file
        :param filename: the json file filename
        :return: the dict of json file's data
        """
    with open(filename) as j:
        variable = json.load(j)
        variable.sort()
    return variable


def get_devices():
    devices_output = os.popen('adb devices').readlines()
    devices = []
    if len(devices_output) != 1:
        for device in devices_output:
            print(device)
            if "\tdevice\n" in device:
                devices.append(re.sub("\tdevice\n", "", device))
    return devices


def create_log_folder_at_local():
    os.makedirs(LOG_DATE, exist_ok=True)
    os.makedirs(LOG_PDU_LOGCAT, exist_ok=True)
    os.makedirs(LOG_PDU_BUGREPORT, exist_ok=True)
    os.makedirs(LOG_PDU_QA_LOG, exist_ok=True)
    os.makedirs(LOG_TIME_DIR, exist_ok=True)


class PDUui(Base_TT_Qt.BaseUI):
    def __init__(self):
        super().__init__()
        self.qnx_log_data = None
        self.qnx_logger = None
        _translate = QtCore.QCoreApplication.translate
        self.base_form.setWindowTitle(_translate("base_form", "PDU Test Tool"))
        self.init_packages_tab(get_package_data(config_package_list), get_package_data(config_test_package_list))
        self.comboBox_device.addItems(get_devices())
        self.checkBox_monkey_test.clicked.connect(self.switch_frame)
        self.pushButton_upload_log.clicked.connect(self.upload_files)
        # Monkey test group box
        self.groupBox_monkey = QtWidgets.QGroupBox(self.tab_system)
        self.groupBox_monkey.setObjectName("groupBox_monkey")
        self.gridLayout_monkey = QtWidgets.QGridLayout(self.groupBox_monkey)
        self.gridLayout_monkey.setObjectName("gridLayout_monkey")
        self.label_throttle = QtWidgets.QLabel(self.groupBox_monkey)
        self.label_throttle.setObjectName("label_throttle")
        self.gridLayout_monkey.addWidget(self.label_throttle, 0, 0, 1, 1)
        self.label_event_count = QtWidgets.QLabel(self.groupBox_monkey)
        self.label_event_count.setObjectName("label_event_count")
        self.gridLayout_monkey.addWidget(self.label_event_count, 1, 0, 1, 1)
        self.label_timeout = QtWidgets.QLabel(self.groupBox_monkey)
        self.label_timeout.setObjectName("label_timeout")
        self.gridLayout_monkey.addWidget(self.label_timeout, 2, 0, 1, 1)
        self.lineEdit_throttle = QtWidgets.QLineEdit(
            self.groupBox_monkey
        )
        self.gridLayout_monkey.addWidget(self.lineEdit_throttle, 0, 1, 1, 1)

        self.lineEdit_event_count = QtWidgets.QLineEdit(
            self.groupBox_monkey
        )
        self.gridLayout_monkey.addWidget(self.lineEdit_event_count, 1, 1, 1, 1)
        self.lineEdit_timeout = QtWidgets.QLineEdit(
            self.groupBox_monkey
        )
        self.gridLayout_monkey.addWidget(self.lineEdit_timeout, 2, 1, 1, 1)

        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout_monkey.addItem(spacerItem1, 3, 0, 1, 2)
        self.gridLayout_config.addWidget(self.groupBox_monkey, 1, 1, 1, 1)
        self.groupBox_monkey.setTitle(_translate("base_form", "Monkey Config"))
        self.label_throttle.setText(_translate("base_form", "Throttle"))
        self.label_event_count.setText(_translate("base_form", "Event Count"))
        self.label_timeout.setText(_translate("base_form", "Timeout"))
        self.groupBox_monkey.hide()
        # fill up all data from common.json
        get_config_data()
        self.lineEdit_cpu_interval.setText(_translate("base_form", CPU_MONITOR_INTERVAL_MINUTE))
        self.lineEdit_memory_interval.setText(_translate("base_form", MEM_MONITOR_INTERVAL_MINUTE))
        self.lineEdit_disk_interval.setText(_translate("base_form", DISK_MONITOR_INTERVAL_MINUTE))
        self.lineEdit_cpu_loop.setText(_translate("base_form", CPU_MONITOR_LOOP_TIMES))
        self.lineEdit_memory_loop.setText(_translate("base_form", MEM_MONITOR_LOOP_TIMES))
        self.lineEdit_disk_loop.setText(_translate("base_form", DISK_MONITOR_LOOP_TIMES))
        print(PROJECTS)
        self.label_project_name_data.setText(_translate("base_form", PROJECTS))
        self.comboBox_app_name.addItems(APPLICATIONS)
        self.lineEdit_throttle.setText(_translate("base_form", MONKEY_ACTION_INTERVAL))
        self.lineEdit_timeout.setText(_translate("base_form", MONKEY_TEST_TIMEOUT_MINUTE))
        self.lineEdit_event_count.setText(_translate("base_form", MONKEY_ACTION_COUNT))
        # redirect the stdout / std error to textEdit_log
        sys.stdout = TextRedirector(self.textEdit_log, "stdout")
        sys.stderr = TextRedirector(self.textEdit_log, "stderr")

        # update the background color
        self.base_form.setStyleSheet('#base_form{background-color: #FFF8D7;}')

    def upload_dirs_to_ftp(self, ftp_ip, ftp_account, ftp_password, dir_path, target_path):
        """
        Args:
            ftp_ip: ip for the ftp server
            ftp_account: the account to log in to ftp server
            ftp_password: the password for the log in account
            dir_path: the path of local directory's path
            target_path: the path to place directories
        """
        try:
            ftp_tool.upload_dirs(ftp_ip, ftp_account, ftp_password, dir_path, target_path)
        except Exception:
            self.popup_notify(traceback.format_exc())

    def popup_notify(self, message):
        if self.base_form.isVisible():
            message_box = QtWidgets.QMessageBox(self.base_form)
            message_box.warning(self.base_form, "Warning", message)
        else:
            print(message)

    def delete_monitor_log(self):
        """
        Delete log files in device
        """
        print('Delete exist log files')
        for item in get_package_data(config_test_package_list):
            subprocess.run(
                self.adb_command + ['shell', 'rm', DUT_LOG_DIRECTORY + 'qa_{}.csv'.format(item)])
        subprocess.Popen(self.adb_command + ['shell', 'rm', DUT_LOG_DIRECTORY + '*.csv']).wait()
        subprocess.Popen(self.adb_command + ['shell', 'rm', DUT_LOG_DIRECTORY + '*.log']).wait()

    def run_monkey_command(self):
        """
            trigger a monkey test with the command by generate_monkey_command()
        """
        cmd = self.generate_monkey_command()
        monkey_timeout_sec = int(MONKEY_TEST_TIMEOUT_MINUTE) * 60
        monkey_thread = subprocess.Popen(cmd)
        try:
            monkey_thread.communicate(timeout=monkey_timeout_sec)
        except subprocess.TimeoutExpired:
            print(f"Reach timeout, {MONKEY_TEST_TIMEOUT_MINUTE} minutes")
            monkey_thread.kill()

    def start_log(self):
        super().start_log()
        # presetting
        subprocess.call(self.adb_command + ["root"])
        subprocess.call(self.adb_command + ["remount"])
        self.wait_device()
        subprocess.call(self.adb_command + ["shell", "pkill", "logcat"])
        try:
            self.qnx_logger = QNX_logger.QNXlogger()
            self.qnx_logger.start_log()
        except Exception:
            print("Failed to trigger QNX logging")
            print(traceback.format_exc())
        # modify system time to current time
        subprocess.call(self.adb_command + ["shell", "date", datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")])
        self.update_test_packages(config_test_package_list)
        self.delete_monitor_log()
        self.trigger_monitor()

        if self.checkBox_monkey_test.isChecked():
            try:
                print("Start monkey testing")
                self.run_monkey_command()
            except KeyboardInterrupt:
                print("interrupt by ctrl+c")
            self.stop_log()
        print("All Done for Start process")

    def stop_log(self):
        """
            stop log recording and pull data
        """
        print("Start collecting log")
        super().stop_log()
        self.wait_device()
        subprocess.call(self.adb_command + ["shell", "pkill", "logcat"])
        self.wait_device()
        subprocess.call(self.adb_command + ["shell", "pkill", "monkey"])
        self.wait_device()
        try:
            self.qnx_logger.flag = False
            self.qnx_log_data = self.qnx_logger.test_data
            with open(LOG_TIME_DIR+os.sep+"qnx_log.log", mode="w", encoding="utf-8") as qnx_file:
                qnx_file.writelines(self.qnx_log_data)
        except Exception:
            print("Failed to get qnx log")
            print(traceback.format_exc())
        self.get_test_log(self.checkBox_monkey_test.isChecked())
        self.wait_device()
        self.pull_and_delete_bugreport(self.checkBox_file_issue_to_jira.isChecked())

        bugreport_thread = threading.Thread(target=self.generate_bugreport)
        bugreport_thread.start()
        while bugreport_thread.is_alive():
            self.textEdit_log.update()

        with open(LOG_TIME_DIR + "Build_info.txt", 'w') as file:
            build_info = re.findall("SMP PREEMPT (.+)", self.get_device_build_info())[0]
            file.write(build_info + "\n")
        logcat_file = LOG_PDU_LOGCAT + f"{LOG_TIME}-logcat.txt"
        subprocess.call(
            self.adb_command + ["pull", DUT_LOG_DIRECTORY + "logcat.log", logcat_file])
        subprocess.call(self.adb_command + ["shell", "rm",
                                            DUT_LOG_DIRECTORY + "logcat.log"])
        log_combiner.combine_log(LOG_DATE + "outputFolder" + os.sep + LOG_TIME + os.sep)

        if not self.checkBox_monkey_test.isChecked():
            if self.label_current_tester.text() != "":
                tester = self.label_current_tester.text()
            else:
                tester = "None"
            monitor_dir = self.label_project_name_data.text() + os.sep \
                          + self.comboBox_app_name.currentText() + os.sep \
                          + tester + os.sep
            print(monitor_dir)
            os.makedirs(monitor_dir, exist_ok=True)
            log_date_only = LOG_DATE.replace(LOG_PDU, "")
            copy_log_data_to(LOG_DATE, monitor_dir + os.sep + log_date_only)
            shutil.rmtree(LOG_DATE)
            if not os.listdir(LOG_PDU):
                os.rmdir(LOG_PDU)
        upload_thread = threading.Thread(target=self.upload_files)
        upload_thread.start()
        if upload_thread.is_alive():
            self.textEdit_log.update()
        print("All Done for END process")

    def generate_bugreport(self):
        """
            Generate bugreport file
            """
        print("Generate Bugreport, it will take few minutes.")
        subprocess.run(self.adb_command + ["bugreport", LOG_PDU_BUGREPORT])

    def pull_and_delete_bugreport(self, file_issue):
        """
            Pull bugreport file and
        """
        print("Pull bugreport data and remove it on device")
        bugreport_dir = LOG_PDU_BUGREPORT + f"BR_{LOG_TIME}"
        os.makedirs(bugreport_dir, exist_ok=True)
        self.pull_remove_file("/data/system/dropbox", bugreport_dir)
        self.pull_remove_file("/data/anr", bugreport_dir)
        self.pull_remove_file("/data/tombstones", bugreport_dir)
        print("Start parsing bugreport data")

        try:
            logcatParserV3.parse_br_files(os.path.abspath(bugreport_dir), LOG_TIME)
        except FileNotFoundError:
            print("File / dir not found")
            print(sys.exc_info())
        if file_issue:
            parsing_bugreport(bugreport_dir, LOG_TIME)

    def upload_files(self):
        print("Uploading log \n")
        get_config_data()
        if self.comboBox_ftp_server.currentText() == "TW_FTP":
            print("FTP node: TW \n")
            ftp_ip = AUTO_QA_FTP_IP
            ftp_account = AUTO_QA_ACCOUNT
            ftp_password = AUTO_QA_PASSWORD
            remote_path_add = "/PDU/"
        else:
            print("FTP node: CN \n")
            ftp_ip = CN_FTP_IP
            ftp_account = CN_FTP_ACCOUNT
            ftp_password = CN_FTP_PASSWORD
            remote_path_add = "/mobiledrivetech/PROJECT/PDU/Auto_team/"
        if getattr(sys, 'frozen', False):
            execute_folder = os.path.dirname(sys.executable)
            for directory in os.listdir(ABS_DIR_PATH):
                if directory in ["Log_PDU"] + PROJECTS:
                    shutil.copytree(os.path.abspath(ABS_DIR_PATH + os.sep + directory),
                                    execute_folder + os.sep + directory)
            for directory in os.listdir(execute_folder):
                if directory == "Log_PDU":
                    self.upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password, os.path.abspath(directory),
                                            remote_path_add + "Monkey_log")
                elif directory in PROJECTS:
                    for log_dir in os.listdir(directory):
                        self.upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password,
                                                os.path.abspath(directory + os.sep + log_dir),
                                                remote_path_add + "AOSP_Monitor_log" + os.sep + log_dir)

        for directory in os.listdir(ABS_DIR_PATH):
            if directory == "Log_PDU":
                self.upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password, os.path.abspath(LOG_PDU),
                                        remote_path_add + "Monkey_log")
            elif directory in PROJECTS:
                for log_dir in os.listdir(directory):
                    self.upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password,
                                            os.path.abspath(directory + os.sep + log_dir),
                                            remote_path_add + "AOSP_Monitor_log" + os.sep + log_dir)
        print("Upload process is done, please check the data in server.\n")

    def get_test_log(self, is_monkey_test=True):
        """
        Pull all log data in device and draw line chart by log data
        """
        print("Pulling test log")
        log_PDU_qalog_time_ = LOG_PDU_QA_LOG + LOG_TIME + os.sep
        os.makedirs(log_PDU_qalog_time_, exist_ok=True)
        for system in MONITOR_SYSTEM_LIST:
            if system != "DISK":
                for item in get_package_data(config_test_package_list):
                    self.pull_remove_file(
                        f"/data/local/tmp/qa/qa_{item}_{system}.csv", log_PDU_qalog_time_
                    )
                    # print(Path(log_PDU_qalog_time_ + f"qa_{item}_{system}.csv"))
                    DrawLineChart.draw_line_chart(
                        str(Path(log_PDU_qalog_time_ + f"qa_{item}_{system}.csv")), system, 2)

            self.pull_remove_file(f"/data/local/tmp/qa/qa_{system}_monitor.csv",
                                  log_PDU_qalog_time_)

            DrawLineChart.draw_line_chart(
                str(Path(f"{log_PDU_qalog_time_}qa_{system}_monitor.csv")), system)
        if is_monkey_test:
            self.pull_remove_file("/data/local/tmp/qa/monkey_test_log.log", LOG_TIME_DIR)

    def pull_remove_file(self, file, location):
        self.pull_file(file, location)
        self.remove_file(file)

    def switch_frame(self):
        if self.checkBox_monkey_test.isChecked():
            self.groupBox_log_config.hide()
            self.groupBox_monkey.show()
        else:
            self.groupBox_monkey.hide()
            self.groupBox_log_config.show()

    def trigger_logcat(self):
        """
        trigger logcat in background process and put logcat log in logcat.log
        """
        print("Triggering logcat service")
        logcat_command = "logcat -b main -b system -b radio -b events -v time 2>&1 >  /data/local/tmp/qa/logcat.log"

        subprocess.call(self.adb_command + ["shell", "logcat", "-b", "all", "-c"])
        subprocess.call(self.adb_command + ["shell", "nohup", "sh", "-c", f"\"{logcat_command}\"", "&"])

    def monitor_thread(self, system):
        """
            To put monitor script in DUT and trigger it
            :param system: str: system name, e.g. "CPU"
            """
        # copy qa_{system}_monitor.sh2 to DUT and rename to qa_{system}_monitor.sh
        subprocess.call(
            self.adb_command + ["push", Path(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2"),
                                f"{DUT_LOG_DIRECTORY}qa_{system}_monitor.sh"]
        )
        # remove qa_{system}_monitor.sh2
        os.remove(Path(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2"))
        # grant execute permission
        subprocess.call(self.adb_command + ["shell", "chmod", "+x",
                                            f"{DUT_LOG_DIRECTORY}qa_{system}_monitor.sh"])
        # put the qa_restart{system}.sh to DUT
        subprocess.call(
            self.adb_command + ["push", Path(f"{ABS_DIR_PATH}/shell/qa_restart{system}.PDU.sh"),
                                f"{DUT_LOG_DIRECTORY}qa_restart{system}.PDU.sh"]
        )
        # grant execute permission
        subprocess.call(
            self.adb_command + ["shell", "chmod", "+x",
                                f"{DUT_LOG_DIRECTORY}qa_restart{system}.PDU.sh"]
        )
        # trigger qa_restart{system}.PDU.sh in another process
        subprocess.call(self.adb_command + ["shell",
                                            f"cd /data/local/tmp/qa && nohup ./qa_restart{system}.PDU.sh &"],
                        timeout=10)

    def trigger_monitor(self):
        threading.Thread(target=self.trigger_logcat).start()
        for shell_script in os.listdir(f"{ABS_DIR_PATH}" + os.sep + "shell"):
            Base_TT_Qt.modify_eol_to_linux(f"{ABS_DIR_PATH}" + os.sep + "shell" + os.sep + shell_script)
        # get monitor config from common.json
        for system in MONITOR_SYSTEM_LIST:
            print(f"Push {system} monitor scripts, raise permission and start monitoring")
            system_monitor = globals()["{}_MONITOR".format(system)]
            system_monitor_interval_minute = int(globals()["{}_MONITOR_INTERVAL_MINUTE".format(
                system)]) * 60
            system_monitor_loop = globals()["{}_MONITOR_LOOP_TIMES".format(system)]

            if system_monitor:
                fin = open(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh",
                           "rt", encoding="utf-8")
                contents = fin.read()
                fin.close()
                # put interval , loops & packages list in qa_{system}_monitor.sh into qa_{system}_monitor.sh2
                fout = open(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2",
                            "w", newline="\n")
                fout.write(f"interval={system_monitor_interval_minute}\n")
                fout.write(f"loops={system_monitor_loop}\n")
                fout.writelines("processArray=(")
                for package in get_package_data(config_test_package_list):
                    fout.writelines("\"" + package + "\"\n")
                fout.writelines(")")
                fout.write(contents)
                fout.close()
                # trigger monitor threads
                system_thread = threading.Thread(target=self.monitor_thread,
                                                 args=(system,))
                system_thread.start()

        print("Thread started")

    def generate_monkey_command(self):
        monitor_loop_list = [
            self.lineEdit_cpu_loop.text(),
            self.lineEdit_memory_loop.text(),
            self.lineEdit_disk_loop.text()
        ]
        monitor_interval_list = [
            self.lineEdit_cpu_interval.text(),
            self.lineEdit_cpu_interval.text(),
            self.lineEdit_cpu_interval.text()
        ]
        update_config_data("MONKEY_ACTION_COUNT", self.lineEdit_event_count.text())
        update_config_data("MONKEY_ACTION_INTERVAL", self.lineEdit_throttle.text())
        update_config_data("MONKEY_TEST_TIMEOUT_MINUTE", self.lineEdit_timeout.text())
        for i in range(len(MONITOR_SYSTEM_LIST)):
            system = MONITOR_SYSTEM_LIST[i]
            update_config_data(f"{system}_MONITOR_INTERVAL_MINUTE", monitor_interval_list[i])
            update_config_data(f"{system}_MONITOR_LOOP_TIMES", monitor_loop_list[i])
        get_config_data()
        test_process_list = get_package_data(config_test_package_list)
        monkey_test_command = self.adb_command + [
            "shell",
            "monkey",
            " -p ",
            " -p ".join(test_process_list),
            " ".join(MONKEY_TEST_ARG),
            "--throttle " + " ".join([MONKEY_ACTION_INTERVAL, MONKEY_ACTION_COUNT]), "|", "tee",
            DUT_LOG_DIRECTORY + "monkey_test_log.log"]
        print(monkey_test_command)
        return monkey_test_command

    def get_device_build_info(self):
        return subprocess.check_output(self.adb_command + ["shell", "uname", "-a"]).decode("utf-8")

    def create_log_folder_on_device(self):
        subprocess.call(self.adb_command + ["shell", "mkdir", DUT_LOG_DIRECTORY])


class TextRedirector(object):
    def __init__(self, widget: QtWidgets.QTextEdit, tag="stdout"):
        self.widget = widget
        self.tag = tag
        if tag == "stdout":
            self.terminal = sys.__stdout__
        elif tag == "stderr":
            self.terminal = sys.__stderr__

    def write(self, text):
        self.terminal.write(text)
        self.terminal.flush()
        self.widget.append(str(text))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = PDUui()
    ui.base_form.show()
    sys.exit(app.exec_())

import datetime
import json
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path
from PIL import Image
from PyQt5 import QtCore, QtWidgets

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from . import Base_TT_Qt
except (ModuleNotFoundError, ImportError):
    import Base_TT_Qt

try:
    from Auto_TT.modules import log_combiner, DrawLineChart, logcatParserV3, parser_and_create_issue, \
        ftp_tool
except (ModuleNotFoundError, ImportError):
    from modules import log_combiner, DrawLineChart, logcatParserV3, parser_and_create_issue, \
        ftp_tool

DUT_LOG_DIRECTORY = "/data/local/tmp/qa/"  # it's android base, have to use /


def resource_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS + os.sep + "Vera_TT"
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path)


ABS_DIR_PATH = resource_path() + os.sep

# Test log directory naming variables
LOG_VERA = ABS_DIR_PATH + "LOG_VERA" + os.sep
LOG_DATE = LOG_VERA + time.strftime("%Y_%m_%d", time.localtime()) + os.sep
LOG_VERA_LOGCAT = LOG_DATE + "logcat" + os.sep
LOG_VERA_BUGREPORT = LOG_DATE + "bugreport" + os.sep
LOG_VERA_QA_LOG = LOG_DATE + "qalog" + os.sep
LOG_TIME = time.strftime(
    "%Y_%m_%d-%H_%M_%S", time.localtime()
)
LOG_TIME_DIR = LOG_DATE + os.sep + "outputFolder" + os.sep + LOG_TIME + os.sep

# For device choice

MONITOR_SYSTEM_LIST = ["CPU", "MEM", "DISK"]

config_common = ABS_DIR_PATH + "common.json"
config_package_list = ABS_DIR_PATH + "package_list.json"
config_test_package_list = ABS_DIR_PATH + "test_package_list.json"

SERVER_DIRECTION = r"\\MD-TEST\Projects\SAW\Vera_Monitor_log"
LOCAL_DIRECTION = r"D:\Projects\SAW\Vera_Monitor_log"


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
    os.makedirs(LOG_VERA_LOGCAT, exist_ok=True)
    os.makedirs(LOG_VERA_BUGREPORT, exist_ok=True)
    os.makedirs(LOG_VERA_QA_LOG, exist_ok=True)
    os.makedirs(LOG_TIME_DIR, exist_ok=True)


class VeraUI(Base_TT_Qt.BaseUI):
    def __init__(self):
        super().__init__()
        self.running = None
        self.monkey_thread = None
        self.monkey_y = None
        self.monkey_x = None
        self.qnx_log_data = None
        self.qnx_logger = None
        _translate = QtCore.QCoreApplication.translate
        self.base_form.setWindowTitle(_translate("base_form", "Vera Test Tool"))
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
        self.lineEdit_throttle = QtWidgets.QLineEdit(
            self.groupBox_monkey
        )
        self.gridLayout_monkey.addWidget(self.lineEdit_throttle, 0, 1, 1, 1)

        self.lineEdit_event_count = QtWidgets.QLineEdit(
            self.groupBox_monkey
        )
        self.gridLayout_monkey.addWidget(self.lineEdit_event_count, 1, 1, 1, 1)

        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout_monkey.addItem(spacerItem1, 3, 0, 1, 2)
        self.gridLayout_config.addWidget(self.groupBox_monkey, 1, 1, 1, 1)
        self.groupBox_monkey.setTitle(_translate("base_form", "Monkey Config"))
        self.label_throttle.setText(_translate("base_form", "Throttle"))
        self.label_event_count.setText(_translate("base_form", "Event Count"))
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
        self.lineEdit_event_count.setText(_translate("base_form", MONKEY_ACTION_COUNT))
        # redirect the stdout / std error to textEdit_log
        sys.stdout = TextRedirector(self.textEdit_log, "stdout")
        sys.stderr = TextRedirector(self.textEdit_log, "stderr")

        # update the background color
        self.base_form.setStyleSheet('#base_form{background-color: #FFECF5;}')

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

    def start_log(self):
        set_vera_time()
        self.push_file_to_vera()
        super().start_log()
        # presetting
        subprocess.call(self.adb_command + ["root"])
        subprocess.call(self.adb_command + ["remount"])
        self.wait_device()
        subprocess.Popen(self.adb_command + ["shell", "bash", f"{DUT_LOG_DIRECTORY}start_journalctl.sh"])

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
        self.running = False
        self.wait_device()
        super().stop_log()
        self.wait_device()
        print("Stop monkey test")
        print("Start collecting log")
        self.wait_device()
        subprocess.call(self.adb_command + ["shell", "bash", f"{DUT_LOG_DIRECTORY}stop_script.sh"])
        subprocess.call(self.adb_command + ["shell", "bash", f"{DUT_LOG_DIRECTORY}get_log.sh"])
        subprocess.call(self.adb_command + ["shell", "pkill", "journalctl"])
        self.wait_device()
        with open(LOG_TIME_DIR + "Build_info.txt", 'w') as file:
            build_info = re.findall("SMP PREEMPT (.+)", self.get_device_build_info())[0]
            file.write(build_info + "\n")
        print("Pulling log")
        get_monitor_log_thread = threading.Thread(target=self.get_monitor_log)
        get_monitor_log_thread.start()
        while get_monitor_log_thread.is_alive():
            self.main_page.update()
        log_combiner.combine_log(LOG_DATE + "outputFolder" + os.sep + LOG_TIME + os.sep)
        print("Uploading log")
        upload_thread = threading.Thread(target=self.upload_files)
        upload_thread.start()
        while upload_thread.is_alive():
            self.main_page.update()
        print("All Done for END process")
        self.remove_file(DUT_LOG_DIRECTORY + "*")

    def upload_files(self):
        print("Uploading log \n")
        get_config_data()
        if self.comboBox_ftp_server.currentText() == "TW_FTP":
            print("FTP node: TW \n")
            ftp_ip = AUTO_QA_FTP_IP
            ftp_account = AUTO_QA_ACCOUNT
            ftp_password = AUTO_QA_PASSWORD
            remote_path_add = "/SAW/"
        else:
            print("FTP node: CN \n")
            ftp_ip = CN_FTP_IP
            ftp_account = CN_FTP_ACCOUNT
            ftp_password = CN_FTP_PASSWORD
            remote_path_add = "/mobiledrivetech/PROJECT/SAW/Auto_team/"
        if getattr(sys, 'frozen', False):
            execute_folder = os.path.dirname(sys.executable)
            for directory in os.listdir(ABS_DIR_PATH):
                if directory in ["LOG_VERA"] + PROJECTS:
                    shutil.copytree(os.path.abspath(ABS_DIR_PATH + os.sep + directory),
                                    execute_folder + os.sep + directory)
            for directory in os.listdir(execute_folder):
                if directory == "LOG_VERA":
                    self.upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password, os.path.abspath(directory),
                                            remote_path_add + "Monkey_log")
                elif directory in PROJECTS:
                    for log_dir in os.listdir(directory):
                        self.upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password,
                                                os.path.abspath(directory + os.sep + log_dir),
                                                remote_path_add + "AOSP_Monitor_log" + os.sep + log_dir)

        for directory in os.listdir(ABS_DIR_PATH):
            if directory == "LOG_VERA":
                self.upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password, os.path.abspath(LOG_VERA),
                                        remote_path_add + "Monkey_log")
            elif directory in PROJECTS:
                for log_dir in os.listdir(directory):
                    self.upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password,
                                            os.path.abspath(directory + os.sep + log_dir),
                                            remote_path_add + "AOSP_Monitor_log" + os.sep + log_dir)
        print("Upload process is done, please check the data in server.\n")

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

    def monitor_thread(self, system):
        self.push_file(ABS_DIR_PATH + "/shell/qa_" + system + "_monitor.sh2",
                       DUT_LOG_DIRECTORY + "qa_" + system + "_monitor.sh")
        self.push_file(ABS_DIR_PATH + "/shell/qa_restart" + system + ".sh",
                       DUT_LOG_DIRECTORY + "qa_restart" + system + ".sh")
        os.remove(Path(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2"))
        subprocess.call(self.adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}qa_{system}_monitor.sh"])
        subprocess.call(self.adb_command + ["push", Path(f"{ABS_DIR_PATH}/shell/qa_restart{system}.sh"),
                                            f"{DUT_LOG_DIRECTORY}qa_restart{system}.sh"])
        subprocess.call(self.adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}qa_restart{system}.sh"])
        subprocess.call(self.adb_command + ["shell", f"cd /data/local/tmp/qa && nohup ./qa_restart{system}.sh &"])

    def trigger_monitor(self):
        for shell_script in os.listdir(f"{ABS_DIR_PATH}/shell"):
            Base_TT_Qt.modify_eol_to_linux(f"{ABS_DIR_PATH}" + os.sep + "shell" + os.sep + shell_script)
        for system in MONITOR_SYSTEM_LIST:
            system_monitor = globals()["{}_MONITOR".format(system)]
            system_monitor_interval_minute = int(globals()["{}_MONITOR_INTERVAL_MINUTE".format(system)]) * 60
            system_monitor_loop = globals()["{}_MONITOR_LOOP_TIMES".format(system)]

            if system_monitor:
                fin = open(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh", "rt", encoding="utf-8")
                contents = fin.read()
                fin.close()
                fout = open(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2", "w", newline="\n")
                fout.write(f"interval={system_monitor_interval_minute}\n")
                fout.write(f"loops={system_monitor_loop}\n")
                fout.writelines("processArray=(")
                for package in get_package_data(config_test_package_list):
                    fout.writelines("\"" + package + "\"\n")
                fout.writelines(")\n")
                fout.write(contents)
                fout.close()
                system_thread = threading.Thread(target=self.monitor_thread, args=(system,))
                system_thread.start()
        print("Thread started")

    def get_device_build_info(self):
        return subprocess.check_output(self.adb_command + ["shell", "uname", "-a"]).decode("utf-8")

    def create_log_folder_on_device(self):
        subprocess.call(self.adb_command + ["shell", "mkdir", DUT_LOG_DIRECTORY])

    def get_device_size(self):
        screenshot_path = os.path.join(os.getcwd(), "screenshot.png")
        # Check if the screenshot file already exists
        if not os.path.exists(screenshot_path):
            try:
                subprocess.run(["adb", "shell", "screenshooter", "screenshot.png"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error capturing screenshot: {e}")
                return

            try:
                subprocess.run(["adb", "pull", "/home/root/screenshot.png", screenshot_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error pulling screenshot: {e}")
                return

        img = Image.open(screenshot_path)
        self.monkey_x, self.monkey_y = img.size

    def push_file_to_vera(self):
        self.push_file(ABS_DIR_PATH + "/shell/get_log.sh", DUT_LOG_DIRECTORY)
        self.push_file(ABS_DIR_PATH + "/shell/stop_script.sh", DUT_LOG_DIRECTORY)
        self.push_file(ABS_DIR_PATH + "/shell/start_journalctl.sh", DUT_LOG_DIRECTORY)
        subprocess.call(self.adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}get_log.sh"])
        subprocess.call(self.adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}stop_script.sh"])
        subprocess.call(self.adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}start_journalctl.sh"])

    def random_click_position(self):
        self.get_device_size()
        random_x = random.randint(0, self.monkey_x / 2)
        random_y = random.randint(0, self.monkey_y)
        self.monkey_thread = subprocess.Popen(
            ["adb", "shell", "inputd-cli", "touch", str(random_x), str(random_y)])
        self.monkey_thread.communicate()
        print(f"Click:({random_x}, {random_y})")

    def random_swipe_position(self):
        self.get_device_size()
        random_x = random.randint(0, self.monkey_x / 2)
        random_y = random.randint(0, self.monkey_y)
        random_x1 = random.randint(0, self.monkey_x / 2)
        random_y1 = random.randint(0, self.monkey_y)
        self.monkey_thread = subprocess.Popen(
            ["adb", "shell", "inputd-cli", "swipe", str(random_x), str(random_y), str(random_x1), str(random_y1)])
        self.monkey_thread.communicate()

        print(f"Swipe:({random_x}, {random_y}) to ({random_x1}, {random_y1})")

    def run_monkey_command(self):
        update_config_data("MONKEY_ACTION_COUNT", self.click_count.get())
        update_config_data("MONKEY_ACTION_INTERVAL", self.interval_time.get())

        setting_count = int(MONKEY_ACTION_COUNT)
        setting_interval = float(MONKEY_ACTION_INTERVAL)
        self.monkey_thread = threading.Thread(target=self.run_monkey_actions, args=(setting_count, setting_interval))
        self.monkey_thread.start()

    def run_monkey_actions(self, setting_count, setting_interval):
        self.running = True
        count = 0
        while count < setting_count and self.running:
            funcs = [self.random_click_position, self.random_swipe_position]
            proportion = [9, 1]
            func = random.choices(funcs, weights=proportion, k=1)[0]
            func()
            count += 1
            time.sleep(setting_interval)
        print("Monkey Test Finish")


def set_vera_time():
    print('Set Vera Time')
    now = datetime.datetime.now()
    vera_time = now.strftime("%Y-%m-%d\ %H:%M:%S")
    os.popen('adb shell date -s "' + vera_time + '"')
    print('Set Time Finished')


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
    ui = VeraUI()
    ui.base_form.show()
    sys.exit(app.exec_())

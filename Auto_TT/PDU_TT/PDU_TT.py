import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from tkinter import scrolledtext
from pathlib import Path
from tkinter import *
import tkinter as tk
from tkinter import ttk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from . import Base_TT
except (ModuleNotFoundError, ImportError):
    import Base_TT

try:
    from Auto_TT.modules import log_combiner, DrawLineChart, logcatParserV3, parser_and_create_issue, \
        ftp_tool
except (ModuleNotFoundError, ImportError):
    from modules import log_combiner, DrawLineChart, logcatParserV3, parser_and_create_issue, \
        ftp_tool

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
parser_and_create_issue.jira_issue_create_tool.JIRA_PROJECT = "PDU"


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


def upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password, dir_path, target_path):
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
        popup_notify(sys.exc_info())


def copy_log_data_to(dir_path, target_path):
    """

    Args:
        dir_path: str, the source directory path, will copy those dirs under the dir_path
        target_path: the destination route to place dirs

    Returns: boolean, True if copy success, False for copy fail

    """
    dir_path = os.path.abspath(dir_path)
    # print(dir_path)
    try:
        shutil.copytree(Path(dir_path), Path(target_path), dirs_exist_ok=True)
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


def popup_notify(message):
    message_box = tk.Toplevel()
    message_box.wm_title("Warning!")
    label_text = tk.Label(message_box, text="Upload failed, error message:")
    label_text.pack()

    label_error_msg = scrolledtext.ScrolledText(message_box, height=2)
    label_error_msg.insert(END, message)
    label_error_msg.pack()

    noted_button = tk.Button(message_box, text="Noted", command=message_box.destroy, bg="#FFCC66")
    noted_button.pack()


class PDUui(Base_TT.UIPage):
    def __init__(self):
        super().__init__()
        main_page = super().main_page
        super().main_page.title(
            "  PDU_TestTool                                         Contributed by AutoTeam")
        main_page.configure()
        ttk_style = ttk.Style()
        font_style = ('Arial', 10, 'bold')
        ttk_style.theme_use('default')
        ttk_style.configure("TNotebook", background="#05F2DB", borderwidth=2)
        ttk_style.configure("TNotebook.Tab", background="#0583F2", borderwidth=2, font=font_style)
        ttk_style.configure("TFrame", background="#05F2DB", borderwidth=2, font=font_style)
        ttk_style.configure("TCombobox", background="#FFCC66", borderwidth=2, font=font_style)
        ttk_style.map("TNotebook.Tab", background=[("selected", "#05F2DB")])
        self.start_log_btn.configure(bg="#FFCC66")
        self.stop_log_btn.configure(bg="#FFCC66")
        process_array = get_package_data(config_package_list)
        self.text_output.grid_remove()
        text_output = scrolledtext.ScrolledText(main_page, height=10)
        self.text_output = text_output
        text_output.grid(column=0, row=2, padx=5,
                         pady=5, columnspan=5, sticky=S + E + W + N)
        sys.stdout = TextRedirector(self.text_output, "stdout")
        sys.stderr = TextRedirector(self.text_output, "stderr")
        tab_control = super().tab_control
        tab_control.grid_configure(rowspan=2)
        self.monitor_frame.configure(bg="#05F2DB", font=font_style)
        self.start_log_btn.configure(font=font_style)
        self.stop_log_btn.configure(font=font_style)

        tab_control.grid(row=0, column=0, sticky=W)

        super().value_cpu_interval_minute.set(f"{CPU_MONITOR_INTERVAL_MINUTE}")
        super().value_cpu_loop_count.set(f"{CPU_MONITOR_LOOP_TIMES}")
        super().value_mem_interval_minute.set(f"{MEM_MONITOR_INTERVAL_MINUTE}")
        super().value_mem_loop_count.set(f"{MEM_MONITOR_LOOP_TIMES}")
        super().value_disk_interval_minute.set(f"{DISK_MONITOR_INTERVAL_MINUTE}")
        super().value_disk_loop_count.set(f"{DISK_MONITOR_LOOP_TIMES}")
        sub_label_frame = tk.LabelFrame(super().tab_system, text='Options',
                                        padx=5, pady=5, bg="#05F2DB", font=font_style)
        sub_label_frame.grid(column=4, row=0, ipadx=5, ipady=5, sticky=N + S)

        is_create_issue = tk.BooleanVar()
        self.is_create_issue = is_create_issue
        create_issue_checkbox = tk.Checkbutton(sub_label_frame, text="File issue to JIRA ", width=17,
                                               variable=is_create_issue, onvalue=True, offvalue=False,
                                               font=font_style, anchor=W
                                               )
        create_issue_checkbox.grid(column=0, row=0, padx=5, pady=5, ipadx=5, columnspan=2)
        create_issue_checkbox.deselect()

        is_monkey_test = tk.BooleanVar()
        self.is_monkey_test = is_monkey_test
        monkey_test_checkbox = tk.Checkbutton(sub_label_frame, text="Monkey test", width=17,
                                              variable=is_monkey_test, onvalue=True, offvalue=False,
                                              command=self.switch_mode, font=font_style, anchor=W)
        monkey_test_checkbox.grid(column=0, row=1, padx=5, pady=5, ipadx=5, columnspan=2)
        monkey_test_checkbox.deselect()
        reboot_btn = Button(sub_label_frame, text='Reboot', command=self.reboot, font=font_style, bg="#FFCC66")

        reboot_btn.grid(column=0, row=2,
                        padx=5, pady=5, sticky=tk.E + tk.W, columnspan=2)
        Label(sub_label_frame, text="FTP server:", font=font_style).grid(
            column=0, row=3, padx=5, pady=5, sticky=tk.E)
        ftp_selector = ttk.Combobox(sub_label_frame, width=17)
        ftp_selector.grid(column=1, row=3, padx=5, pady=5, sticky=W + E)
        ftp_selector['values'] = ["TW_FTP", "CN_FTP"]
        self.ftp_selector = ftp_selector
        self.ftp_selector.current(0)
        upload_btn = Button(sub_label_frame, text='Upload log',
                            command=self.upload_files, font=font_style, bg="#FFCC66")
        upload_btn.grid(column=0, row=4,
                        padx=5, pady=5, sticky=tk.E + tk.W, columnspan=2)

        monkey_frame = tk.LabelFrame(super().tab_system, text='Monkey config', background="#05F2DB",
                                     padx=5, pady=5, font=font_style)
        self.monkey_frame = monkey_frame
        # monkey_frame.grid(column=6, row=0, ipadx=5, ipady=5, sticky=N)
        throttle_count = tk.StringVar()
        self.throttle_count = throttle_count
        throttle_count.set(f"{MONKEY_ACTION_INTERVAL}")
        entry_throttle_count = ttk.Entry(
            monkey_frame, textvariable=throttle_count)
        entry_throttle_count.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E + tk.S)
        Label(monkey_frame, text="Throttle:").grid(
            row=0, column=0, padx=5, pady=5, sticky=W + E)

        event_count = tk.StringVar()
        self.event_count = event_count
        event_count.set(f"{MONKEY_ACTION_COUNT}")
        entry_event_count = ttk.Entry(
            monkey_frame, textvariable=event_count)
        entry_event_count.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E + tk.S)
        Label(monkey_frame, text="Event-Count:").grid(row=1, column=0, padx=5, pady=5,
                                                      sticky=W + E)

        monkey_timeout = tk.StringVar()
        self.monkey_timeout = monkey_timeout
        monkey_timeout.set(f"{MONKEY_TEST_TIMEOUT_MINUTE}")
        entry_monkey_timeout = ttk.Entry(
            monkey_frame, textvariable=monkey_timeout)
        entry_monkey_timeout.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E + tk.S)
        Label(monkey_frame, text="Monkey Timeout \n (minutes):").grid(row=2, column=0, padx=5, pady=5,
                                                                      sticky=W + E)

        folder_frame = tk.LabelFrame(super().tab_system, text='Log Directory Config',
                                     padx=5, pady=5, background="#05F2DB", font=font_style)
        self.folder_frame = folder_frame
        folder_frame.grid(column=6, row=0, ipadx=5, ipady=5, sticky=N + S)

        Label(folder_frame, text="Project Name:").grid(
            column=0, row=0, padx=5, pady=5, sticky=tk.E)
        project_selector = ttk.Combobox(folder_frame, width=17)
        project_selector.grid(column=1, row=0, padx=5, pady=5, sticky=W + E)

        Label(folder_frame, text="App Name:").grid(
            column=0, row=1, padx=5, pady=5, sticky=W + E)
        application_selector = ttk.Combobox(folder_frame, width=17)
        application_selector.grid(column=1, row=1, padx=5, pady=5, sticky=W + E)

        Label(folder_frame, text="Tester Name:").grid(
            column=0, row=2, padx=5, pady=5, sticky=W + E)
        # tester_selector = ttk.Combobox(folder_frame, width=17)
        tester_selector = tk.Label(folder_frame)
        tester_selector.grid(column=1, row=2, padx=5, pady=5, sticky=W + E)
        self.project_selector = project_selector
        self.application_selector = application_selector
        self.tester_selector = tester_selector

        test_package_list = get_package_data(config_test_package_list)

        super().init_packages_tab(process_array, test_package_list)
        self.package_frame.configure(bg="#05F2DB", font=font_style)
        self.package2_frame.configure(bg="#05F2DB", font=font_style)
        self.check_all_btn.configure(bg="#FFCC66", font=font_style)
        self.uncheck_all_btn.configure(bg="#FFCC66", font=font_style)
        for project in PROJECTS:
            project_selector['values'] = (*project_selector['values'], project)
            # Project_Selector.bind('<<ComboboxSelected>>', dev_changed)
            project_selector.current(0)

        for app in APPLICATIONS:
            application_selector['values'] = (*application_selector['values'], app)
            # Application_Selector.bind('<<ComboboxSelected>>', dev_changed)
            application_selector.current(0)

        # for tester in TESTERS:
        #     tester_selector['values'] = (*tester_selector['values'], tester)
        #     # Tester_Selector.bind('<<ComboboxSelected>>', dev_changed)
        #     tester_selector.current(0)

    def switch_mode(self):
        if self.is_monkey_test.get():

            self.folder_frame.grid_remove()
            self.monkey_frame.grid(column=6, row=0, ipadx=5, ipady=5, sticky=N + S)
        else:
            self.monkey_frame.grid_remove()
            self.folder_frame.grid(column=6, row=0, ipadx=5, ipady=5, sticky=N + S)
        self.main_page.update()

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

    def generate_monkey_command(self):
        monitor_loop_list = [
            self.value_cpu_loop_count.get(),
            self.value_mem_loop_count.get(),
            self.value_disk_loop_count.get()
        ]
        monitor_interval_list = [
            self.value_cpu_interval_minute.get(),
            self.value_mem_interval_minute.get(),
            self.value_disk_interval_minute.get()
        ]
        update_config_data("MONKEY_ACTION_COUNT", self.event_count.get())
        update_config_data("MONKEY_ACTION_INTERVAL", self.throttle_count.get())
        update_config_data("MONKEY_TEST_TIMEOUT_MINUTE", self.monkey_timeout.get())
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
        # self.input_text(" ".join(monkey_test_command) + "\n")
        return monkey_test_command

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
        # print(f"adb push {ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2 " +
        #       f"{DUT_LOG_DIRECTORY}qa_{system}_monitor.sh")
        subprocess.call(
            self.adb_command + ["push", Path(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2"),
                                f"{DUT_LOG_DIRECTORY}qa_{system}_monitor.sh"]
        )
        # remove qa_{system}_monitor.sh2
        # print("rm " + str(Path(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2")))
        os.remove(Path(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2"))
        # grant execute permission
        # print(f"adb shell chmod +x {DUT_LOG_DIRECTORY}qa_{system}_monitor.sh \n")
        subprocess.call(self.adb_command + ["shell", "chmod", "+x",
                                            f"{DUT_LOG_DIRECTORY}qa_{system}_monitor.sh"])
        # put the qa_restart{system}.sh to DUT
        # print(f"adb push {ABS_DIR_PATH}/shell/qa_restart{system}.PDU.sh " +
        #       f"{DUT_LOG_DIRECTORY}qa_restart{system}.PDU.sh")
        subprocess.call(
            self.adb_command + ["push", Path(f"{ABS_DIR_PATH}/shell/qa_restart{system}.PDU.sh"),
                                f"{DUT_LOG_DIRECTORY}qa_restart{system}.PDU.sh"]
        )
        # grant execute permission
        # print(
        #     f"adb shell chmod +x {DUT_LOG_DIRECTORY}qa_restart{system}.PDU.sh \n")
        subprocess.call(
            self.adb_command + ["shell", "chmod", "+x",
                                f"{DUT_LOG_DIRECTORY}qa_restart{system}.PDU.sh"]
        )
        # trigger qa_restart{system}.PDU.sh in another process
        subprocess.call(self.adb_command + ["shell",
                                            f"cd /data/local/tmp/qa && nohup ./qa_restart{system}.PDU.sh &"])

    def trigger_monitor(self):
        """
            To modify the monitor by given config and  create a thread for log monitor
            """
        # trigger logcat in a new thread
        threading.Thread(target=self.trigger_logcat).start()
        for shell_script in os.listdir(f"{ABS_DIR_PATH}" + os.sep + "shell"):
            Base_TT.modify_eol_to_linux(f"{ABS_DIR_PATH}" + os.sep + "shell" + os.sep + shell_script)
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
                # system_thread.join()
        print("Thread started")

    def get_device_build_info(self):
        return subprocess.check_output(self.adb_command + ["shell", "uname", "-a"]).decode("utf-8")

    def start_log(self):
        """
                start monitor function (CPU/MEM/DISK/LOGCAT)
        """
        super().start_log()
        # self.input_text("Start logging")
        subprocess.call(self.adb_command + ["root"])
        subprocess.call(self.adb_command + ["remount"])
        self.wait_device()
        subprocess.call(self.adb_command + ["shell", "pkill", "logcat"])
        # modify system time to current time
        subprocess.call(self.adb_command + ["shell", "date", datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")])
        self.update_test_packages(config_test_package_list)
        self.delete_monitor_log()
        self.trigger_monitor()
        print("All Done for Start process")
        if self.is_monkey_test.get():
            try:
                # self.input_text("Start monkey testing")
                print("Start monkey testing")
                self.run_monkey_command()
            except KeyboardInterrupt:
                print("interrupt by ctrl+c")
                # self.input_text("interrupt by ctrl+c")
            self.stop_log()

    def stop_log(self):
        """
            stop log recording and pull data
        """
        # self.input_text("Start collecting log")
        print("Start collecting log")
        super().stop_log()
        self.wait_device()
        subprocess.call(self.adb_command + ["shell", "pkill", "logcat"])
        self.wait_device()
        subprocess.call(self.adb_command + ["shell", "pkill", "monkey"])
        self.wait_device()
        self.get_test_log(self.is_monkey_test.get())
        self.wait_device()
        self.pull_and_delete_bugreport(self.is_create_issue.get())
        bugreport_thread = threading.Thread(target=self.generate_bugreport)
        bugreport_thread.start()
        while bugreport_thread.is_alive():
            self.main_page.update()
        with open(LOG_TIME_DIR + "Build_info.txt", 'w') as file:
            build_info = re.findall("SMP PREEMPT (.+)", self.get_device_build_info())[0]
            file.write(build_info + "\n")
        logcat_file = LOG_PDU_LOGCAT + f"{LOG_TIME}-logcat.txt"
        subprocess.call(
            self.adb_command + ["pull", DUT_LOG_DIRECTORY + "logcat.log", logcat_file])
        subprocess.call(self.adb_command + ["shell", "rm",
                                            DUT_LOG_DIRECTORY + "logcat.log"])
        log_combiner.combine_log(LOG_DATE + "outputFolder" + os.sep + LOG_TIME + os.sep)
        if not self.is_monkey_test.get():
            monitor_dir = self.project_selector.get() + os.sep \
                          + self.application_selector.get() + os.sep \
                          + self.tester_selector["text"] + os.sep
            os.makedirs(monitor_dir, exist_ok=True)
            log_date_only = LOG_DATE.replace(LOG_PDU, "")
            copy_log_data_to(LOG_DATE, monitor_dir + os.sep + log_date_only)
            shutil.rmtree(LOG_DATE)
            if not os.listdir(LOG_PDU):
                os.rmdir(LOG_PDU)

        # self.input_text("Uploading log")
        self.upload_files()
        # self.input_text("Log uploaded")
        # self.input_text("All Done for END process")
        print("All Done for END process")

    def reboot(self):
        super().reboot_device()

    def dev_changed(self, event):
        device_id = self.device_selector.get()
        self.change_device(device_id)
        # self.input_text("device sn:" + device_id)

    def create_log_folder_on_device(self):
        subprocess.call(self.adb_command + ["shell", "mkdir", DUT_LOG_DIRECTORY])

    def create_log_folder_at_local(self):
        os.makedirs(LOG_DATE, exist_ok=True)
        os.makedirs(LOG_PDU_LOGCAT, exist_ok=True)
        os.makedirs(LOG_PDU_BUGREPORT, exist_ok=True)
        os.makedirs(LOG_PDU_QA_LOG, exist_ok=True)
        os.makedirs(LOG_TIME_DIR, exist_ok=True)

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
        # try:
        # upload_dirs_to_ftp(dir_path, target_path)
        print("Uploading log \n")
        get_config_data()
        if self.ftp_selector.get() == "TW_FTP":
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
                    upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password, os.path.abspath(directory),
                                       remote_path_add + "Monkey_log")
                elif directory in PROJECTS:
                    for log_dir in os.listdir(directory):
                        upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password,
                                           os.path.abspath(directory + os.sep + log_dir),
                                           remote_path_add + "AOSP_Monitor_log" + os.sep + log_dir)

        for directory in os.listdir(ABS_DIR_PATH):
            if directory == "Log_PDU":
                upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password, os.path.abspath(LOG_PDU),
                                   remote_path_add + "Monkey_log")
            elif directory in PROJECTS:
                for log_dir in os.listdir(directory):
                    upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password,
                                       os.path.abspath(directory + os.sep + log_dir),
                                       remote_path_add + "AOSP_Monitor_log" + os.sep + log_dir)
        print("Upload process is done, please check the data in server.\n")

        # except Exception:
        #     print("Failed to link to ftp server, copy to local location")
        #     print(sys.exc_info())
        #     copy_log_data_to(LOG_DATE, LOCAL_DIRECTION)


class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag
        if tag == "stdout":
            self.terminal = sys.stdout
        elif tag == "stderr":
            self.terminal = sys.stderr

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.terminal.write(str)


if __name__ == '__main__':
    get_config_data()
    # print(globals())
    UI = PDUui()
    UI.start()
    # get_config_data()

import os
import sys
import time
import json
import random
import shutil
import datetime
import threading
import subprocess
import tkinter as tk
from tkinter import scrolledtext
from pathlib import Path
from tkinter import ttk
from PIL import Image

# Add Auto_TT to path
vera_tt_dir = os.path.dirname(os.path.abspath(__file__))
auto_tt_dir = os.path.dirname(vera_tt_dir)
sys.path.append(auto_tt_dir)

try:
    from . import Base_TT
except ModuleNotFoundError and ImportError:
    import Base_TT

try:
    from Auto_TT.modules import ftp_tool
except ModuleNotFoundError and ImportError:
    from modules import ftp_tool

DUT_LOG_DIRECTORY = "/data/local/tmp/qa/"

def resource_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS + os.sep + "Vera_TT"
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path)

ABS_DIR_PATH = resource_path() + os.sep

# Test log directory naming variables
LOG_VERA_MONKEY = ABS_DIR_PATH + "Vera_monkey_log" + os.sep
LOG_DATE = time.strftime("%Y_%m_%d", time.localtime()) + os.sep
LOG_TIME = time.strftime("%Y_%m_%d-%H_%M_%S", time.localtime())
LOG_TIME_DIR = LOG_DATE + "outputFolder" + os.sep + LOG_TIME + os.sep
LOG_VERA_QA_LOG = LOG_DATE + "qalog" + os.sep + LOG_TIME + os.sep

MONITOR_SYSTEM_LIST = ["CPU", "MEM", "DISK"]

config_common = ABS_DIR_PATH + "common.json"
config_package_list = ABS_DIR_PATH + "package_list.json"
config_test_package_list = ABS_DIR_PATH + "test_package_list.json"

LOCAL_DIRECTION = ABS_DIR_PATH

main_color = "#d4e6e8"
tab_select = "#f3f5e8"
button_color = "#d6dbbb"

# # Update variables in common.json
def update_config_data(key, value):
    with open(config_common, "r+") as jsonFile:
        data = json.load(jsonFile)
        data[key] = value
        jsonFile.seek(0)
        json.dump(data, jsonFile, indent=4)
        jsonFile.truncate()
    get_config_data()


# Upload files to ftp
def upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password, dir_path, target_path):
    try:
        ftp_tool.upload_dirs(ftp_ip, ftp_account, ftp_password, dir_path, target_path)
    except Exception as e:
        print(e)
        popup_notify(sys.exc_info())


# Get variables in common.json
def get_config_data():
    with open(config_common) as j:
        data = json.load(j)
        for key, values in data.items():
            globals()[key] = values


# Get test package list from json file
def get_package_data(filename):
    with open(filename) as j:
        variable = json.load(j)
    return variable

# FTP upload meaasge
def popup_notify(message):
    message_box = tk.Toplevel()
    message_box.wm_title("Warning!")
    label_text = tk.Label(message_box, text="Upload failed, error message:")
    label_text.pack()

    label_error_msg = scrolledtext.ScrolledText(message_box, height=2)
    label_error_msg.insert(tk.END, message)
    label_error_msg.pack()

    noted_button = tk.Button(message_box, text="Noted", command=message_box.destroy, bg="#FFCC66")
    noted_button.pack()

# Set Vera time
def set_vera_time():
    print('Set Vera Time')
    now = datetime.datetime.now()
    vera_time = now.strftime("%Y-%m-%d\ %H:%M:%S")
    os.popen('adb shell date -s "' + vera_time + '"' )
    print('Set Time Finished') 

# UI Main
class VeraUI(Base_TT.UIPage):
    def __init__(self):
        super().__init__()
        main_page = super().main_page
        main_page.title("Vera_TestTool                             Contributed by AutoTeam")

        # setting text output
        self.text_output.grid_remove()
        text_output = scrolledtext.ScrolledText(main_page, height=10)
        self.text_output = text_output
        text_output.grid(column=0, row=2, padx=5, pady=5, columnspan=5, sticky=tk.S + tk.E + tk.W + tk.N)
        sys.stdout = TextRedirector(self.text_output, "stdout")
        sys.stderr = TextRedirector(self.text_output, "stderr")

        # setting ui style
        ttk_style = ttk.Style()
        ttk_style.configure("TNotebook", background=main_color)
        ttk_style.configure("TFrame", background=main_color)
        ttk_style.configure("TNotebook.Tab", background=main_color)
        ttk_style.configure("monitor_frame", background=main_color)
        ttk_style.map("TNotebook.Tab", background=[("selected", tab_select)])
        self.monitor_frame.configure(background=main_color)
        ttk_style.configure("TCombobox", background=button_color)

        # setting monitor frame text
        self.monitor_frame.configure(text="CPU / Memory / Storage")

        # setting start button 
        self.start_log_btn.configure(width=10, height=1, background=button_color)

        # setting stop button
        self.stop_log_btn.configure(width=10, height=1, background=button_color)

        # setting check all button
        self.check_all_btn.configure(background=button_color)

        # setting uncheck all button
        self.uncheck_all_btn.configure(background=button_color)

        # config value
        self.value_cpu_interval_minute.set(f"{CPU_MONITOR_INTERVAL_MINUTE}")
        self.value_cpu_loop_count.set(f"{CPU_MONITOR_LOOP_TIMES}")
        self.value_mem_interval_minute.set(f"{MEM_MONITOR_INTERVAL_MINUTE}")
        self.value_mem_loop_count.set(f"{MEM_MONITOR_LOOP_TIMES}")
        self.value_disk_interval_minute.set(f"{DISK_MONITOR_INTERVAL_MINUTE}")
        self.value_disk_loop_count.set(f"{DISK_MONITOR_LOOP_TIMES}")

        # setting Options lable
        sub_label_frame = tk.LabelFrame(super().tab_system, text="Options", padx=5, pady=5, background=main_color)
        sub_label_frame.grid(column=4, row=0, columnspan=2, rowspan=7, ipadx=5, ipady=5, sticky=tk.NW)

        # Monkey Test Checkbox
        is_monkey_test = tk.BooleanVar()
        self.is_monkey_test = is_monkey_test
        monkey_test_checkbox = tk.Checkbutton(sub_label_frame, text="Monkey test", width=17,
                                              variable=is_monkey_test, onvalue=True, offvalue=False,
                                              command=self.switch_mode, anchor=tk.W)
        monkey_test_checkbox.grid(column=0, row=1, padx=5, pady=5, ipadx=5, columnspan=2)
        monkey_test_checkbox.deselect()

        # FTP Server Checkbox
        tk.Label(sub_label_frame, text="FTP server:").grid(
            column=0, row=3, padx=5, pady=5, sticky=tk.E)
        ftp_selector = ttk.Combobox(sub_label_frame, width=17)
        ftp_selector.grid(column=1, row=3, padx=5, pady=5, sticky=tk.W + tk.E)
        ftp_selector['values'] = ["TW_FTP", "CN_FTP"]
        self.ftp_selector = ftp_selector
        self.ftp_selector.current(0)

        # Upload Button
        upload_btn = tk.Button(sub_label_frame, text='Upload log',
                            command=self.upload_files, background=button_color)
        upload_btn.grid(column=0, row=4,
                        padx=5, pady=5, sticky=tk.E + tk.W, columnspan=2)    

        # Device Reboot
        reboot_btn = tk.Button(sub_label_frame, text="Device Reboot", background=button_color, command=self.reboot_device)
        reboot_btn.grid(column=0, row=2, columnspan=2, padx=5, pady=5, sticky=tk.E + tk.W)

        # Package tab
        test_package_list = get_package_data(config_test_package_list)
        packages_list = get_package_data(config_package_list)
        self.init_packages_tab(packages_list, test_package_list)

        # Monkey Config tab
        monkey_frame = tk.LabelFrame(super().tab_system, text='Monkey config',
                                      padx=5, pady=5, background=main_color)
        self.monkey_frame = monkey_frame

        interval_time = tk.StringVar()
        self.interval_time = interval_time
        interval_time.set(f"{MONKEY_ACTION_INTERVAL}")
        entry_interval_time = ttk.Entry(
            monkey_frame, textvariable=interval_time)
        entry_interval_time.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E + tk.S)
        tk.Label(monkey_frame, text="Interval Time \n(seconds):").grid(row=0, column=0,
                                                    padx=5, pady=5, sticky=tk.W + tk.E)

        click_count = tk.StringVar()
        self.click_count = click_count
        click_count.set(f"{MONKEY_ACTION_COUNT}")
        entry_click_count = ttk.Entry(
            monkey_frame, textvariable=click_count)
        entry_click_count.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E + tk.S)
        tk.Label(monkey_frame, text="Click-Count:").grid(row=1, column=0,
                                                       padx=5, pady=5, sticky=tk.W + tk.E)
       
        # Log Directory Config tab
        folder_frame = tk.LabelFrame(super().tab_system, text='Log Directory Config', 
                                     padx=5, pady=5, background=main_color)
        self.folder_frame = folder_frame
        folder_frame.grid(column=6, row=0, ipadx=5, ipady=5, sticky=tk.N + tk.S)

        tk.Label(folder_frame, text="Project Name:").grid(
            column=0, row=0, padx=5, pady=5, sticky=tk.E)
        project_selector = ttk.Combobox(folder_frame, width=17)
        project_selector.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W + tk.E)

        tk.Label(folder_frame, text="App Name:").grid(
            column=0, row=1, padx=5, pady=5, sticky=tk.W + tk.E)
        application_selector = ttk.Combobox(folder_frame, width=17)
        application_selector.grid(column=1, row=1, padx=5, pady=5, sticky=tk.W + tk.E)

        tk.Label(folder_frame, text="Tester Name:").grid(
            column=0, row=2, padx=5, pady=5, sticky=tk.W + tk.E)
        tester_selector = tk.Label(folder_frame)
        tester_selector.grid(column=1, row=2, padx=5, pady=5, sticky=tk.W + tk.E)
        self.project_selector = project_selector
        self.application_selector = application_selector
        self.tester_selector = tester_selector

        # Projects value
        for project in PROJECTS:
            project_selector['values'] = (*project_selector['values'], project)
            project_selector.current(0)

        # APP value
        for app in APPLICATIONS:
            application_selector['values'] = (*application_selector['values'], app)
            application_selector.current(0)

    def push_file_to_vera(self):
        self.push_file(ABS_DIR_PATH + "/shell/get_log.sh", DUT_LOG_DIRECTORY)
        self.push_file(ABS_DIR_PATH + "/shell/stop_script.sh", DUT_LOG_DIRECTORY)
        self.push_file(ABS_DIR_PATH + "/shell/start_journalctl.sh", DUT_LOG_DIRECTORY)
        subprocess.call(self.adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}get_log.sh"])
        subprocess.call(self.adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}stop_script.sh"])
        subprocess.call(self.adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}start_journalctl.sh"])
    
    def switch_mode(self):
        if self.is_monkey_test.get():
            self.folder_frame.grid_remove()
            self.monkey_frame.grid(column=6, row=0, ipadx=5, ipady=5, sticky=tk.N + tk.S)
        else:
            self.monkey_frame.grid_remove()
            self.folder_frame.grid(column=6, row=0, ipadx=5, ipady=5, sticky=tk.N + tk.S)
        self.main_page.update()    

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

    def random_click_position(self):
        self.get_device_size()
        random_x = random.randint(0, self.monkey_x/2)
        random_y = random.randint(0, self.monkey_y)
        self.monkey_thread = subprocess.Popen(
            ["adb", "shell", "inputd-cli", "touch", str(random_x), str(random_y)])
        self.monkey_thread.communicate()
        print(f"Click:({random_x}, {random_y})")

    def random_swipe_position(self):
        self.get_device_size()
        random_x = random.randint(0, self.monkey_x/2)
        random_y = random.randint(0, self.monkey_y)
        random_x1 = random.randint(0, self.monkey_x/2)
        random_y1 = random.randint(0, self.monkey_y)
        self.monkey_thread = subprocess.Popen(
            ["adb", "shell", "inputd-cli", "swipe", str(random_x), str(random_y), str(random_x1), str(random_y1)])
        self.monkey_thread.communicate()

        print(f"Swipe:({random_x}, {random_y}) to ({random_x1}, {random_y1})")

    def vera_monekey(self):
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
    
    # Delete log files in device
    def delete_monitor_log(self):
        print("Delete log files")
        self.remove_file(DUT_LOG_DIRECTORY + "*.csv")
        self.remove_file(DUT_LOG_DIRECTORY + "*.log")
        self.remove_file(DUT_LOG_DIRECTORY + "*.sh")
        self.remove_file("/home/root/system_log")

    # create folder on Vera
    def create_log_folder_on_device(self):
        subprocess.call(self.adb_command + ["shell", "mkdir", "-p", DUT_LOG_DIRECTORY])

    # create folder at local
    def create_log_folder_at_local(self):
        os.makedirs(LOCAL_DIRECTION, exist_ok=True)

    # To modify the monitor by given config and create a thread for log monitor
    def trigger_monitor(self):
        for shell_script in os.listdir(f"{ABS_DIR_PATH}/shell"):
            Base_TT.modify_eol_to_linux(f"{ABS_DIR_PATH}" + os.sep + "shell" + os.sep + shell_script)
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

    def monitor_thread(self, system):
        self.push_file(ABS_DIR_PATH + "/shell/qa_" + system + "_monitor.sh2", DUT_LOG_DIRECTORY + "qa_" + system + "_monitor.sh")
        self.push_file(ABS_DIR_PATH + "/shell/qa_restart" + system + ".sh", DUT_LOG_DIRECTORY + "qa_restart" + system + ".sh")
        os.remove(Path(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2"))
        subprocess.call(self.adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}qa_{system}_monitor.sh"])
        subprocess.call(self.adb_command + ["push", Path(f"{ABS_DIR_PATH}/shell/qa_restart{system}.sh"), f"{DUT_LOG_DIRECTORY}qa_restart{system}.sh"])
        subprocess.call(self.adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}qa_restart{system}.sh"])
        subprocess.call(self.adb_command + ["shell", f"cd /data/local/tmp/qa && nohup ./qa_restart{system}.sh &"])

    def start_log(self):
        set_vera_time()
        self.delete_monitor_log()
        self.push_file_to_vera()
        super().start_log()
        print("Start logging")
        subprocess.call(self.adb_command + ["root"])
        subprocess.call(self.adb_command + ["remount"])
        print("Triggering journalctl service")
        subprocess.Popen(self.adb_command + ["shell", "bash", f"{DUT_LOG_DIRECTORY}start_journalctl.sh"])
        self.update_test_packages(config_test_package_list)
        self.trigger_monitor()
        if self.is_monkey_test.get():
            try:
                print("Start monkey testing")
                self.vera_monekey()
            except KeyboardInterrupt:
                print("interrupt by ctrl+c")
            # self.stop_log()
        print("All Done for Start process")

    # stop monitor and get monitor log
    def stop_log(self):
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
        print("Pulling log")
        getmonitorfiles_thread = threading.Thread(target=self.get_monitor_log)
        getmonitorfiles_thread.start()
        while getmonitorfiles_thread.is_alive():
            self.main_page.update()
        print("Uploading log")
        uploadfiles_thread = threading.Thread(target=self.upload_files)
        uploadfiles_thread.start()
        while uploadfiles_thread.is_alive():
            self.main_page.update()
        print("All Done for END process")
        self.remove_file(DUT_LOG_DIRECTORY + "*")

    # get monitor log function
    def get_monitor_log(self):
        print("Get monitor log")
        monitor_dir =  self.project_selector.get() + os.sep + self.application_selector.get() + os.sep + self.tester_selector["text"] + os.sep
        local_log_dir = LOCAL_DIRECTION + monitor_dir + LOG_VERA_QA_LOG
        os.makedirs(local_log_dir, exist_ok=True)

        for system in MONITOR_SYSTEM_LIST:
            if system != "DISK":
                for item in get_package_data(config_test_package_list):
                    self.pull_file(f"/data/local/tmp/qa/qa_{item}_{system}.csv", local_log_dir)
            self.pull_file(f"/data/local/tmp/qa/qa_{system}_monitor.csv", local_log_dir)
        self.pull_file("/data/local/tmp/qa/vera_journalctl.log", local_log_dir)
        self.pull_file("/data/local/tmp/qa/nohup.out", local_log_dir)
        self.pull_file("/home/root/system_log", local_log_dir)
        

    def upload_files(self):
        print("Uploading log \n")
        get_config_data()
        if self.ftp_selector.get() == "TW_FTP":
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

        for directory in os.listdir(ABS_DIR_PATH):
            if directory in PROJECTS:
                for log_dir in os.listdir(ABS_DIR_PATH + directory):
                    print(os.path.abspath(ABS_DIR_PATH + directory + os.sep + log_dir))
                    upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password, os.path.abspath(ABS_DIR_PATH + directory + os.sep + log_dir),
                                       remote_path_add + "Vera_Monitor_log" + os.sep + log_dir)
            elif directory == "Vera_monkey_log":
                print("123")
                print(os.path.abspath(LOG_VERA_MONKEY))
                upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password,
                                       os.path.abspath(LOG_VERA_MONKEY),
                                       remote_path_add + "Vera_Monitor_log" + os.sep + "Vera_monkey_log")
                shutil.rmtree(os.path.abspath(LOG_VERA_MONKEY))
        

        print("Upload process is done, please check the data in server.\n")

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
    UI = VeraUI()
    UI.start()

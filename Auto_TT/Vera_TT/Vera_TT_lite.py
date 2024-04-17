import os
import random
import shutil
import sys
import threading
import time
import json
import datetime
import subprocess
from pathlib import Path
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from Auto_TT.modules import ftp_tool
except ModuleNotFoundError and ImportError:
    from modules import ftp_tool

def resource_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS + os.sep + "Vera_TT"
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path)

adb_command = ["adb"]

ABS_DIR_PATH = resource_path() + os.sep

LOCAL_DIRECTION = ABS_DIR_PATH
DUT_LOG_DIRECTORY = "/data/local/tmp/qa/"
MONITOR_SYSTEM_LIST = ["CPU", "MEM", "DISK"]

config_test_package_list = ABS_DIR_PATH + "test_package_list.json"
config_common = ABS_DIR_PATH + "common.json"

LOG_VERA_MONKEY = ABS_DIR_PATH + "Vera_monkey_log" + os.sep
LOG_DATE = time.strftime("%Y_%m_%d", time.localtime()) + os.sep
LOG_TIME = time.strftime("%Y_%m_%d-%H_%M_%S", time.localtime())
LOG_TIME_DIR = LOG_DATE + "outputFolder" + os.sep + LOG_TIME + os.sep
LOG_VERA_QA_LOG = LOG_DATE + "qalog" + os.sep + LOG_TIME + os.sep

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

def wait_device():
    subprocess.call(adb_command + ["wait-for-device"])

def remove_file(file):
    subprocess.call(adb_command + ["shell", "rm", "-rf", file])

def push_file(file, location):
    subprocess.call(adb_command + ["push", file, location])

def set_vera_time():
    print('Set Vera Time')
    now = datetime.datetime.now()
    vera_time = now.strftime("%Y-%m-%d\ %H:%M:%S")
    os.popen('adb shell date -s "' + vera_time + '"' )
    print('Set Time Finished') 

def upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password, dir_path, target_path):
    try:
        ftp_tool.upload_dirs(ftp_ip, ftp_account, ftp_password, dir_path, target_path)
    except Exception as e:
        print(e)

def get_execution_time(action):
    global start_time
    global end_time
    if action == "start":
        start_time = datetime.now()
        fmt_start_time = datetime.strftime(start_time, "%Y_%m_%d %H:%M:%S")
        with open(LOG_DATE + "outputFolder" + os.sep + LOG_TIME + os.sep + "Execution_time.txt",
                  "w") as fo:
            fo.writelines(f"Start time : {fmt_start_time}\n")
        return start_time
    elif action == "end":
        end_time = datetime.now()
        duration = end_time - start_time
        fmt_end_time = datetime.strftime(end_time, "%Y_%m_%d %H:%M:%S")
        fmt_duration = \
            f"{int(duration.seconds / 3600)}H:{int((duration.seconds % 3600) / 60)}M:{duration.seconds % 60}S"
        with open(LOG_DATE + "outputFolder" + os.sep + LOG_TIME + os.sep + "Execution_time.txt",
                  "a") as fo:
            fo.writelines(f"End time : {fmt_end_time}\n")
            fo.writelines(f"Execution duration : {fmt_duration}\n")
            fo.close()
        return end_time, duration
    
def check_adb_device(): 
    try:
        check_devices = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        output_lines = check_devices.stdout.strip().split('\n')            
        if len(output_lines) >= 2 and "device" in output_lines[1]:
            print("Devices Connect.")
        else:
            subprocess.call(["sudo", "ip", "addr", "add", "10.1.1.4/24", " dev", "usb0"])
            subprocess.call(["adb", "ifconfig", "usb0", "up"])
            subprocess.call(["adb", "connect", "10.1.1.2"])

    except Exception as e:
        print(e)
        print("Please check devices.")

def get_config_data():
    with open(config_common) as j:
        data = json.load(j)
        for key, values in data.items():
            globals()[key] = values

def get_package_data(filename):
    with open(filename) as j:
        variable = json.load(j)
    return variable

def pull_file(file, location):
    subprocess.call(adb_command + ["pull", file, location])

def get_monitor_log():
    print("Get monitor log")
    monitor_dir = "Vera_monkey_log" + os.sep
    local_log_dir = LOCAL_DIRECTION + monitor_dir + LOG_VERA_QA_LOG
    os.makedirs(local_log_dir, exist_ok=True)

    for system in MONITOR_SYSTEM_LIST:
        if system != "DISK":
            for item in get_package_data(config_test_package_list):
                pull_file(f"/data/local/tmp/qa/qa_{item}_{system}.csv", local_log_dir)
        pull_file(f"/data/local/tmp/qa/qa_{system}_monitor.csv", local_log_dir)
    pull_file("/data/local/tmp/qa/vera_journalctl.log", local_log_dir)
    pull_file("/data/local/tmp/qa/nohup.out", local_log_dir)
    pull_file("/home/root/system_log", local_log_dir)

def delete_monitor_log():
    print("Delete log files")
    remove_file(DUT_LOG_DIRECTORY + "*.csv")
    remove_file(DUT_LOG_DIRECTORY + "*.log")
    remove_file(DUT_LOG_DIRECTORY + "*.sh")
    remove_file("/home/root/system_log")

def push_file_to_vera():
    push_file(ABS_DIR_PATH + "/shell/get_log.sh", DUT_LOG_DIRECTORY)
    push_file(ABS_DIR_PATH + "/shell/stop_script.sh", DUT_LOG_DIRECTORY)
    push_file(ABS_DIR_PATH + "/shell/start_journalctl.sh", DUT_LOG_DIRECTORY)
    subprocess.call(adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}get_log.sh"])
    subprocess.call(adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}stop_script.sh"])
    subprocess.call(adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}start_journalctl.sh"])

def trigger_monitor():
    for shell_script in os.listdir(f"{ABS_DIR_PATH}/shell"):
        modify_eol_to_linux(f"{ABS_DIR_PATH}" + os.sep + "shell" + os.sep + shell_script)
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
            system_thread = threading.Thread(target=monitor_thread, args=(system,))
            system_thread.start()
    print("Thread started")

def monitor_thread(system):
    push_file(ABS_DIR_PATH + "/shell/qa_" + system + "_monitor.sh2", DUT_LOG_DIRECTORY + "qa_" + system + "_monitor.sh")
    push_file(ABS_DIR_PATH + "/shell/qa_restart" + system + ".sh", DUT_LOG_DIRECTORY + "qa_restart" + system + ".sh")
    os.remove(Path(f"{ABS_DIR_PATH}/shell/qa_{system}_monitor.sh2"))
    subprocess.call(adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}qa_{system}_monitor.sh"])
    subprocess.call(adb_command + ["push", Path(f"{ABS_DIR_PATH}/shell/qa_restart{system}.sh"), f"{DUT_LOG_DIRECTORY}qa_restart{system}.sh"])
    subprocess.call(adb_command + ["shell", "chmod", "+x", f"{DUT_LOG_DIRECTORY}qa_restart{system}.sh"])
    subprocess.call(adb_command + ["shell", f"cd /data/local/tmp/qa && nohup ./qa_restart{system}.sh &"])

def get_device_size():
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
    monkey_x, monkey_y = img.size
    return monkey_x, monkey_y

def random_click_position():
    monkey_x, monkey_y = get_device_size()
    random_x = random.randint(0, monkey_x/2)
    random_y = random.randint(0, monkey_y)
    monkey_thread = subprocess.Popen(
        ["adb", "shell", "inputd-cli", "touch", str(random_x), str(random_y)])
    monkey_thread.communicate()
    print(f"Click:({random_x}, {random_y})")

def random_swipe_position():
    monkey_x, monkey_y = get_device_size()
    random_x = random.randint(0, monkey_x/2)
    random_y = random.randint(0, monkey_y)
    random_x1 = random.randint(0, monkey_x/2)
    random_y1 = random.randint(0, monkey_y)
    monkey_thread = subprocess.Popen(
        ["adb", "shell", "inputd-cli", "swipe", str(random_x), str(random_y), str(random_x1), str(random_y1)])
    monkey_thread.communicate()

    print(f"Swipe:({random_x}, {random_y}) to ({random_x1}, {random_y1})")

def run_monkey_actions(setting_count, setting_interval):
    running = True
    count = 0
    while count < setting_count and running:
        funcs = [random_click_position, random_swipe_position]
        proportion = [9, 1]
        func = random.choices(funcs, weights=proportion, k=1)[0]
        func()
        count += 1
        time.sleep(setting_interval)
    print("Monkey Test Finish")

def upload_files():
    ftp_selector = "TW_FTP"
    print("Uploading log \n")
    get_config_data()
    if ftp_selector == "TW_FTP":
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
            print(os.path.abspath(LOG_VERA_MONKEY))
            upload_dirs_to_ftp(ftp_ip, ftp_account, ftp_password,
                                    os.path.abspath(LOG_VERA_MONKEY),
                                    remote_path_add + "Vera_Monitor_log" + os.sep + "Vera_monkey_log")
            shutil.rmtree(os.path.abspath(LOG_VERA_MONKEY))
    print("Upload process is done, please check the data in server.\n")

if __name__ == '__main__':
    check_adb_device()
    get_config_data()
    wait_device()

    is_monkey_test = True

    if len(sys.argv) > 1:
        length = len(sys.argv)
        for i in range(length):
            if sys.argv[i] == "--pass_monkey":
                is_monkey_test = False
                print("skip monkey test")
            elif sys.argv[i] == '--count':
                setting_count = int(sys.argv[i + 1])
            elif sys.argv[i] == '--interval':
                setting_interval = float(sys.argv[i + 1])

    wait_device()

    set_vera_time()
    delete_monitor_log()
    push_file_to_vera()
    print("Start logging")
    subprocess.call(adb_command + ["root"])
    subprocess.call(adb_command + ["remount"])
    print("Triggering journalctl service")
    subprocess.Popen(adb_command + ["shell", "bash", f"{DUT_LOG_DIRECTORY}start_journalctl.sh"])
    trigger_monitor()
    if is_monkey_test == True:
        run_monkey_actions(setting_count,setting_interval)
    wait_device()
    
    print("Start collecting log")
    subprocess.call(adb_command + ["shell", "bash", f"{DUT_LOG_DIRECTORY}stop_script.sh"])
    subprocess.call(adb_command + ["shell", "bash", f"{DUT_LOG_DIRECTORY}get_log.sh"])
    subprocess.call(adb_command + ["shell", "pkill", "journalctl"])
    wait_device()
    print("Pulling log")
    get_monitor_log()
    upload_files()
    print("All Done for END process")
    delete_monitor_log()
    
    os._exit(0)
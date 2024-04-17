import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import PDU_TT_Qt


def get_execution_time(action):
    global start_time
    global end_time
    if action == "start":
        start_time = datetime.now()
        fmt_start_time = datetime.strftime(start_time, "%Y_%m_%d %H:%M:%S")
        with open(PDU_TT_Qt.LOG_DATE + "outputFolder" + os.sep + PDU_TT_Qt.LOG_TIME + os.sep + "Execution_time.txt",
                  "w") as fo:
            fo.writelines(f"Start time : {fmt_start_time}\n")
        return start_time
    elif action == "end":
        end_time = datetime.now()
        duration = end_time - start_time
        fmt_end_time = datetime.strftime(end_time, "%Y_%m_%d %H:%M:%S")
        fmt_duration = \
            f"{int(duration.seconds / 3600)}H:{int((duration.seconds % 3600) / 60)}M:{duration.seconds % 60}S"
        with open(PDU_TT_Qt.LOG_DATE + "outputFolder" + os.sep + PDU_TT_Qt.LOG_TIME + os.sep + "Execution_time.txt",
                  "a") as fo:
            fo.writelines(f"End time : {fmt_end_time}\n")
            fo.writelines(f"Execution duration : {fmt_duration}\n")
            fo.close()
        return end_time, duration


def get_config_data():
    """
    get variables in common.json and append initial as global variables
    """
    PDU_TT_Qt.get_config_data()
    with open(PDU_TT_Qt.config_common) as j:
        data = json.load(j)
        for key, values in data.items():
            globals()[key] = values
    j.close()


def check_device_status(ui):
    adb_devices_output = subprocess.check_output(["adb", "devices"])
    if "offline" in str(adb_devices_output):
        subprocess.call(["adb", "kill-server"])
        subprocess.call(["adb", "start-server"])
        ui.wait_device()


def send_mail(recipients_list, cc_list, file_dir_path):
    sys.path.append("..")
    from modules import mail_tool
    mail_body = create_mail_body(file_dir_path)
    date = time.strftime(
        "%Y_%m_%d", time.localtime()
    )
    mail = mail_tool.Mail(
        title=f"[PDU]Monkey_Test_Result_{date}",
        body=mail_body,
        recipients_list=recipients_list,
        cc_list=cc_list,
        attachment_list=[file_dir_path + os.sep + "test_summary.txt"])
    mail.send_mail()


def create_mail_body(file_dir_path):
    """
       Read the text files under the given folder and parse the data
       Args:
           file_dir_path: the folder to find text files

       Returns: the text data parsed by text file

       """
    test_summary = file_dir_path + os.sep + 'test_summary.txt'
    test_packages = file_dir_path + os.sep + 'Test_packages.txt'
    # Pattern to parse text files
    build_pattern = r"Build_info.txt\n(.+)\n"
    date_pattern = "(Date : [0-9]+_[0-9]+_[0-9]+)"
    execution_time_pattern = "(Execution duration : [0-9 A-Z :]+)"
    jira_new_issue_pattern = "(New issues x [0-9]+)"
    jira_duplicate_issue_pattern = "(Duplicate issues x [0-9]+)"
    anr_pattern = "([0-9]+ ANR crashes)"
    md_anr_pattern = "([0-9]+ MD's ANR crashes)"
    system_app_crash_pattern = "([0-9]+ system_app crashes)"
    system_server_crash_pattern = "([0-9]+ system_server crashes)"
    md_dropbox_app_pattern = "([0-9]+ MD's app crashes)"
    tombstones_pattern = "([0-9]+ tombstones crashes)"
    md_tombstones_pattern = "([0-9]+ MD's tombstones crashes)"
    summary_text = ""
    # Parse and append data in summary text
    with open(test_summary, "r") as file:
        file_content = str(file.read())
    summary_text += re.findall(date_pattern, file_content)[0] + "\n<br>"
    try:
        build_info = re.findall(build_pattern, file_content)[0] + "\n<br>"
        summary_text += "Build info: \n<br>"
        summary_text += "<blockquote>" + build_info + "</blockquote>"
    except IndexError:
        print("Failed to find Build info")
    try:
        with open(test_packages, "r") as file:
            summary_text += "Test packages : \n<br>"
            packages = file.read()
            re.sub("Test_packages.txt\n", "", packages)
            packages_list = packages.split("\n")
            for package in packages_list:
                summary_text += "<blockquote>" + package + "</blockquote>"
    except FileNotFoundError:
        print("failed to find test packages text file in summary")

    if "ANR" in file_content:
        summary_text += "ANR :" + "\n<br>"
        summary_text += "<blockquote>" + re.findall(anr_pattern, file_content)[0] + ", it contains " + \
                        re.findall(md_anr_pattern, file_content)[0] + "</blockquote>"
    if "Dropbox" in file_content:
        summary_text += "Dropbox :" + "\n<br>"
        summary_text += "<blockquote>" + re.findall(system_app_crash_pattern, file_content)[0] + ", it contains " + \
                        re.findall(md_dropbox_app_pattern, file_content)[0] + "\n<br>"
        summary_text += re.findall(system_server_crash_pattern, file_content)[0] + "</blockquote>"
    if "Tombstones" in file_content:
        summary_text += "Tombstone :" + "\n<br>"
        summary_text += "<blockquote>" + re.findall(tombstones_pattern, file_content)[0] + ", it contains " + \
                        re.findall(md_tombstones_pattern, file_content)[0] + "</blockquote>"
    summary_text += re.findall(execution_time_pattern, file_content)[0] + "\n<br>"
    try:
        summary_text += re.findall(jira_new_issue_pattern, file_content)[0] + "\n<br>"
        summary_text += re.findall(jira_duplicate_issue_pattern, file_content)[0] + "\n<br>"
    except IndexError:
        print("failed to find jira issue output in summary")
    server_log_dir = PDU_TT_Qt.SERVER_DIRECTION
    body = ('\n'
            '<html>\n'
            '<body>\n'
            '<p>Hi, all</p>\n'
            '\n'
            '<p>Here\'s today\'s monkey test report</p>\n'
            '\n'
            f'<blockquote>{summary_text}</blockquote>\n'
            '\n'
            f'<p>Full log data directories:<a href="{server_log_dir}">{server_log_dir}</a><br>\n'
            '<blockquote>a. CPU / Memory / Disk usage -> qalog</blockquote>\n'
            '<blockquote>b. logcat -> logcat</blockquote>\n'
            '<blockquote>c. anr / dropbox / tombstone -> bugreport</blockquote>\n'
            '<blockquote>d. Summarized report -> outputfolder</blockquote>\n'
            '<p>===================================================================</p>\n'
            '<p>AutoTeam members:<br>\n'
            'SherlockHuang@mobiledrivetech.com (principal)<br> \n'
            'JeffYJChen@mobiledrivetech.com (App maintenance)<br>\n'
            'LarryHZLai@mobiledrivetech.com (monkey maintenance)</p>\n'
            '\n'
            '<p>備註: 此信件由系統測試完畢自動代為發送Test report，請勿回信。謝謝。</p>\n'
            '<p>===================================================================</p>\n'
            '\n'
            '</body>\n'
            '</html>\n')
    return body


if __name__ == '__main__':
    # init the default flags
    is_file_issue = True
    is_mail_report = True
    test_packages_count = 1
    skip_packages_count = 1
    device_sn = None
    # get config data from common.json
    get_config_data()
    app = PDU_TT_Qt.QtWidgets.QApplication(sys.argv)

    # modify flags from given arguments
    if len(sys.argv) > 1:
        length = len(sys.argv)
        for i in range(length):
            if sys.argv[i] == "-s":
                device_sn = sys.argv[i + 1]
            elif sys.argv[i] == "--pass_jira":
                is_file_issue = False
                print("skip filing issue to JIRA")
            elif sys.argv[i] == "--pass_mail":
                is_mail_report = False
                print("skip mail test report")
            elif sys.argv[i] == '--test_packages_count':
                test_packages_count = int(sys.argv[i + 1])
            elif sys.argv[i] == '--skip_packages_count':
                skip_packages_count = int(sys.argv[i + 1])

    # download "monkey_test_config.json" from FTP and get test configs
    from modules import ftp_tool

    ftp_tool.download_file(AUTO_QA_FTP_IP, AUTO_QA_ACCOUNT, AUTO_QA_PASSWORD, "/SAW/monkey_test_config.json",
                           "monkey_test_config.json")
    monkey_config = json.load(open("monkey_test_config.json", "r"))
    test_packages = monkey_config["test_packages"]
    print("All packages: " + str(test_packages))

    last_test_package = monkey_config['last_test_packages']
    print("Last test package: " + str(last_test_package))
    try:
        last_index = test_packages.index(last_test_package[len(last_test_package) - 1])
    except ValueError:
        last_index = -1
    test_data = []
    # Test all apk if we have tested all packages individually
    if last_index == 7 and len(last_test_package) < len(test_packages):
        test_data = test_packages
    else:
        for i in range(test_packages_count):
            test_package = test_packages[(last_index + i + skip_packages_count) % len(test_packages)]
            if test_package not in test_data:
                test_data.append(test_package)
    print("Test packages: " + str(test_data))
    monkey_config['last_test_packages'] = test_data

    # Write JSON data to a file and upload the monkey test config file to FTP server
    with open("monkey_test_config.json", 'w') as file:
        file.write(json.dumps(monkey_config, separators=(',', ':'), indent=2))
    with open(PDU_TT_Qt.config_test_package_list, 'w') as file:
        file.write(json.dumps(test_data, separators=(',', ':'), indent=2))
    ftp_tool.upload_file(AUTO_QA_FTP_IP, AUTO_QA_ACCOUNT, AUTO_QA_PASSWORD, "monkey_test_config.json", '/SAW')
    # init the ui object
    UI = PDU_TT_Qt.PDUui()
    # Redirect the stdout stderr to terminal back
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    if device_sn:
        UI.change_device(device_sn)
    # modify parameter for folder / path / time
    # test_data_dir = test_data[len(test_data) - 1]
    if len(test_data) > 1:
        test_data_dir = str(len(test_data)) + "_packages"
    else:
        test_data_dir = test_data[0]
    PDU_TT_Qt.LOG_DATE = PDU_TT_Qt.LOG_PDU + time.strftime("%Y_%m_%d", time.localtime()) + "_" + str(
        test_data_dir) + os.sep
    PDU_TT_Qt.LOG_PDU_LOGCAT = PDU_TT_Qt.LOG_DATE + "logcat" + os.sep
    PDU_TT_Qt.LOG_PDU_BUGREPORT = PDU_TT_Qt.LOG_DATE + "bugreport" + os.sep
    PDU_TT_Qt.LOG_PDU_QA_LOG = PDU_TT_Qt.LOG_DATE + "qalog" + os.sep
    PDU_TT_Qt.LOG_TIME = time.strftime(
        "%Y_%m_%d-%H_%M_%S", time.localtime()
    )
    PDU_TT_Qt.LOG_TIME_DIR = PDU_TT_Qt.LOG_DATE + os.sep + "outputFolder" + os.sep + PDU_TT_Qt.LOG_TIME + os.sep
    PDU_TT_Qt.create_log_folder_at_local()
    # write test packages data
    with open(PDU_TT_Qt.LOG_TIME_DIR + "Test_packages.txt", 'w') as file:
        for line in test_data:
            file.write(line + "\n")
    print("reboot device")
    UI.reboot_device()
    UI.wait_device()
    # set monkey test to True and check the test packages in packages tab
    UI.checkBox_monkey_test.setChecked(True)
    UI.checkBox_file_issue_to_jira.setChecked(is_file_issue)

    # write down the start timestamp, set the DUT and start testing
    print("Start time:", get_execution_time("start"))
    check_device_status(UI)
    get_config_data()
    UI.start_log()
    print("End time:", get_execution_time("end"))
    # Combine log again to append execution time in
    PDU_TT_Qt.log_combiner.combine_log(PDU_TT_Qt.LOG_TIME_DIR)
    # upload logs to FTP
    upload_thread = threading.Thread(target=UI.upload_files)
    upload_thread.start()
    # Send report
    if is_mail_report:
        send_mail(monkey_config["recipients_list"], monkey_config["cc_list"], PDU_TT_Qt.LOG_TIME_DIR)
    upload_thread.join(60)
    UI.base_form.destroy()
    sys.exit()

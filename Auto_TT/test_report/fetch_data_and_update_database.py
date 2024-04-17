import glob
import os
import re
import sys
from datetime import datetime, timedelta

from jira import JIRA

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DB_tool import db_tool

db = db_tool.myDB("monkey_test")

SAW_DIR = r"\\MD-TEST\Projects\SAW"
LOCAL_DIR = r"D:\Projects\SAW"
JIRA_PROJCET = "SAW"  # "SAW"  "TEST"
# JIRA_PROJCET = "TEST"


JIRA_URL = "https://jiratepz1.mobiledrivetech.com/"
USERNAME = "qaautotest"
PASSWORD = "MobileDrive#01"
AUTH_INFO = (USERNAME, PASSWORD)

SEARCH_PATTERN = "project = SAW AND reporter = qaautotest"

TODAY = datetime.now()
TODAY_DATE = TODAY.strftime("%Y_%m_%d")


def upload_issue_data():
    jira = JIRA(JIRA_URL, auth=AUTH_INFO)
    search_result = jira.search_issues(SEARCH_PATTERN, maxResults=False)
    data = []
    title_list = ["Issue key", "Status", "Created", "Updated", "Summary"]

    for issue in search_result:
        tz_regular = timedelta(hours=8)
        created = datetime.strftime(datetime.strptime(issue.fields.created, '%Y-%m-%dT%H:%M:%S.000+0000') + tz_regular,
                                    "%Y-%m-%d %H:%M:%S")
        updated = datetime.strftime(datetime.strptime(issue.fields.updated, '%Y-%m-%dT%H:%M:%S.000+0000'),
                                    "%Y-%m-%d %H:%M:%S")
        issue_fields = [issue.key, issue.fields.status.name,
                        created, updated, issue.fields.summary]
        issue_content = {}
        for i in range(len(title_list)):
            issue_content[title_list[i]] = issue_fields[i]
        data.append(issue_content)

    print(data)

    db.delete_data("jira_issues", "WHERE issue_key like \"SAW-%%%%\"")
    columns = ["issue_key", "status", "created_date", "updated_date", "summary", "type", "app_name"]
    for row in data:
        try:
            failed_type = re.search(r"\[([a-z A-Z]+)\]", row["Summary"]).group(1)
        except AttributeError:
            failed_type = "unknown"
        try:
            app_name = re.search(r"\[.+\]\[(.+)\]", row["Summary"]).group(1)
        except AttributeError:
            app_name = "unknown"

        values = [row["Issue key"], row["Status"], row["Created"], row["Updated"], row["Summary"],
                  failed_type, app_name]
        db.insert_data("jira_issues", columns, values)


def upload_monkey_log_data(dir_path, date):
    monkey_log_folder = os.path.abspath(dir_path + os.sep + "Monkey_log")
    monkey_log_list = os.listdir(monkey_log_folder)
    issue_list = {}
    monkey_log_data = []
    for folder in monkey_log_list:
        if re.match("[0-9_]+_[a-z.]+", folder):
            # print(folder)
            text_file_list = glob.glob(
                monkey_log_folder + os.sep + folder + os.sep + "outputFolder" + os.sep + f"{date}*")
            for output_folder in text_file_list:
                print(output_folder)
                datetime_info = os.path.basename(output_folder)
                if os.path.exists(output_folder + os.sep + "JIRA_result_output.txt"):

                    # print(datetime_info)
                    with open(output_folder + os.sep + "JIRA_result_output.txt", "r") as jira_data:
                        if datetime_info not in issue_list.keys():
                            issue_list[f"{datetime_info}"] = []
                        for issue, count in re.findall("([A-Z]+-[0-9]+) x([0-9]+)", jira_data.read()):
                            for listed_issue in issue_list[f"{datetime_info}"]:
                                if listed_issue["issue_key"] is issue:
                                    listed_issue["count"] += count
                            if not any(listed_issue["issue_key"] is issue
                                       for listed_issue in issue_list[f"{datetime_info}"]):
                                issue_list[f"{datetime_info}"].append({"issue_key": issue, "count": count})
                if all(os.path.exists(output_folder + os.sep + file) for file in ["Build_info.txt",
                                                                                  "Test_packages.txt",
                                                                                  "CrashReport.txt",
                                                                                  "Execution_time.txt"]):
                    test_log_dict = {
                        "Date": datetime.strftime(datetime.strptime(datetime_info, "%Y_%m_%d-%H_%M_%S"),
                                                  "%Y-%m-%d %H:%M:%S"),
                        "Build Version": None,
                        "APK & Version": None,
                        "Execution Time": None,
                        "New Issues": None,
                        "Known Issues": None,
                        "ANR": None,
                        "MD_ANR": None,
                        "MD_App_Crash": None,
                        "System_App_Crash": None,
                        "System_Server_Crash": None,
                        "ANR Failed Count": None,
                        "MTBF": None
                    }

                    with open(output_folder + os.sep + "Build_info.txt", "r") as build_info_file:
                        build_info = build_info_file.read()
                        test_log_dict["Build Version"] = build_info

                    with open(output_folder + os.sep + "Test_packages.txt", "r") as test_apps_file:
                        test_apps = test_apps_file.read()
                        test_log_dict["APK & Version"] = test_apps

                    with open(output_folder + os.sep + "Execution_time.txt", "r") as execution_time_file:
                        execution_time_data = execution_time_file.read()

                        execution_time_str = re.findall(r"Execution duration : (.+)", execution_time_data)
                        if execution_time_str:
                            matches = re.findall(r'(\d+)H:(\d+)M:(\d+)S', execution_time_str[0])
                            if matches:
                                hours, minutes, seconds = map(int, matches[0])
                                total_hours = hours + minutes / 60 + seconds / 3600
                            else:
                                total_hours = 0
                        else:
                            total_hours = None
                        test_log_dict["Execution Time"] = total_hours

                    with open(output_folder + os.sep + "CrashReport.txt", "r") as crash_data_file:
                        crash_data = crash_data_file.read()
                        anr_count = re.findall(r"There are ([0-9]+) ANR crashes in logs", crash_data)[0]
                        try:
                            md_anr_count = re.findall(r"There are ([0-9]+) MD's ANR crashes in logs", crash_data)[0]
                            test_log_dict["MD_ANR"] = md_anr_count
                        except IndexError:
                            md_anr_count = None
                            pass
                        dropbox_app_crash_count = \
                            re.findall(r"There are ([0-9]+) system_app crashes in logs", crash_data)[0]
                        dropbox_system_crash_count = \
                            re.findall(r"There are ([0-9]+) system_server crashes in logs", crash_data)[0]
                        try:
                            md_dropbox_count = \
                                re.findall(r"There are ([0-9]+) MD's app crashes in logs", crash_data)[0]
                            test_log_dict["MD_App_Crash"] = md_dropbox_count
                        except IndexError:
                            md_dropbox_count = None
                            pass
                        test_log_dict["ANR"] = anr_count
                        test_log_dict["System_App_Crash"] = dropbox_app_crash_count
                        test_log_dict["System_Server_Crash"] = dropbox_system_crash_count
                    if os.path.exists(output_folder + os.sep + "JIRA_result_output.txt"):
                        with open(output_folder + os.sep + "JIRA_result_output.txt", "r") as jira_file:
                            jira_data = jira_file.read()
                            new_issues_count = re.findall(r"New issues x ([0-9]+):\n", jira_data)[0]
                            duplicate_issues_count = re.findall(r"Duplicate issues x ([0-9]+):\n", jira_data)[0]
                            test_log_dict["New Issues"] = new_issues_count
                            test_log_dict["Known Issues"] = duplicate_issues_count
                    else:
                        test_log_dict["New Issues"] = 0
                        test_log_dict["Known Issues"] = 0
                    if all(crash is not None for crash in [md_anr_count, md_dropbox_count]):
                        anr_failed_count = int(md_anr_count) + int(md_dropbox_count)
                        test_log_dict["ANR Failed Count"] = anr_failed_count
                        test_log_dict["MTBF"] = total_hours / (anr_failed_count + 1)

                    monkey_log_data.append(test_log_dict)

    # print(issue_list)
    # print(monkey_log_data)

    date_list = [item[0] for item in db.select_data("monkey_test_log", ["*"])]
    for row in monkey_log_data:
        if datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S") not in date_list:
            print(row)
            columns = ["datetime", "build_version", "apk", "execution_time", "new_issues", "known_issues",
                       "anr", "system_app_crash", "system_server_crash", "md_anr", "md_app_crash",
                       "anr_failed_count", "mtbf"]
            values = [row["Date"], row["Build Version"],
                      row["APK & Version"], row["Execution Time"], row["New Issues"],
                      row["Known Issues"], row["ANR"], row["System_App_Crash"],
                      row["System_Server_Crash"], row["MD_ANR"], row["MD_App_Crash"],
                      row["ANR Failed Count"], row["MTBF"]]
            db.insert_data("monkey_test_log", columns, values)

    for key in issue_list.keys():
        datetime_data = datetime.strftime(datetime.strptime(key, "%Y_%m_%d-%H_%M_%S"), "%Y-%m-%d %H:%M:%S")
        if len(issue_list[key]) != 0:
            test = str(issue_list[key]).replace("\'", "\"")
            print(f"UPDATE monkey_test_log SET issue_list='{test}' WHERE datetime = '{datetime_data}'")
            db.update_data("monkey_test_log", {"issue_list": f"'{test}'"}, f"WHERE datetime = '{datetime_data}'")


if __name__ == '__main__':
    if os.path.exists(LOCAL_DIR + os.sep + "SAW_Auto_Weekly Report.xlsx"):
        file_folder = LOCAL_DIR
    else:
        file_folder = SAW_DIR

    for i in range(7):
        day = TODAY - timedelta(days=i)
        upload_monkey_log_data(file_folder, day.strftime("%Y_%m_%d"))
    upload_issue_data()

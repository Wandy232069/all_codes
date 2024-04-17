# 設定要遍歷的目錄
import csv
import sys
import traceback
from datetime import date

import numpy
import glob
import os
import re
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DB_tool import db_tool
from modules import mail_tool

DIRECTORY = r"\\md-test\Projects\SAW"
DASHBOARD_LINK = "http://10.57.41.216:3000/d/d1e1050e-a2f2-49fe-a55b-3ab9eaf3c11b/system-monitor-info?orgId=1&from=now-7d&to=now&var-app_name=All"
COLUMN_LIST = ["datetime", "app_name",
               "cpu_average", "cpu_max", "cpu_min", "cpu_p75", "cpu_p25",
               "memory_average", "memory_max", "memory_min", "memory_p75", "memory_p25",
               "platform"]
TIME_RANGE = 24 * 60 * 60

VERA_PACKAGE_LIST = ["com.stellantis.hvac",
                     "com.stellantis.minimalhvac",
                     "com.stellantis.panelwidgets",
                     "com.stellantis.settings",
                     "com.stellantis.devicemanager",
                     "com.stellantis.rvc",
                     "com.stellantis.statusbar",
                     "com.stellantis.notification",
                     "com.stellantis.vehicle",
                     "com.stellantis.appdrawer",
                     "com.stellantis.svc",
                     "com.amazon.ivihomelauncherwidgetpanel"]


def parse_all_data_total(folder):
    text_file_list = glob.glob(os.path.join(folder, r"Monkey_log\**\qa_*_Monitor.csv"), recursive=True) + \
                     glob.glob(os.path.join(folder, r"Vera_Monitor_log\**\qa_*_Monitor.csv"), recursive=True)
    # qa_CPU_monitor.csv / qa_MEM_monitor.csv / qa_{process}_CPU.csv / qa_{process}_MEM.csv / qa_DISK_monitor.csv
    current_time = time.time()
    result_list = list()
    for file in text_file_list:
        if current_time - os.stat(file).st_mtime < TIME_RANGE:
            print(file)
            datetime = re.search(r"\\([0-9_]+-[0-9_]+)\\", file).group(1)
            file_folder = os.path.dirname(file)
            data = {"datetime": datetime, "folder_path": file_folder}
            if any(keyword in file for keyword in ["Monkey_log", "AOSP_Monitor_log"]):
                data["platform"] = "AOSP"
            elif "Vera_Monitor_log" in file:
                data["platform"] = "Vera"
            if "CPU" in file:
                cpu_usage_list = get_csv_data(file, "CPU Loading")
                if len(cpu_usage_list) <= 0:
                    continue
                cpu_average = numpy.average(cpu_usage_list)
                cpu_max = numpy.max(cpu_usage_list)
                cpu_min = numpy.min(cpu_usage_list)
                cpu_p75 = numpy.percentile(cpu_usage_list, 75)
                cpu_p25 = numpy.percentile(cpu_usage_list, 25)
                # print(cpu_average)
                for result in result_list:
                    if result["datetime"] == data["datetime"]:
                        result["cpu_average"] = cpu_average
                        result["cpu_max"] = cpu_max
                        result["cpu_min"] = cpu_min
                        result["cpu_p75"] = cpu_p75
                        result["cpu_p25"] = cpu_p25
                if not any(result["datetime"] == data["datetime"]
                           for result in result_list):
                    data["cpu_average"] = cpu_average
                    data["cpu_max"] = cpu_max
                    data["cpu_min"] = cpu_min
                    data["cpu_p75"] = cpu_p75
                    data["cpu_p25"] = cpu_p25
                    result_list.append(data)
            elif "MEM" in file:
                memory_usage_list = get_csv_data(file, "Memory Usage")
                if len(memory_usage_list) <= 0:
                    continue
                memory_average = numpy.average(memory_usage_list)
                memory_max = numpy.max(memory_usage_list)
                memory_min = numpy.min(memory_usage_list)
                memory_p75 = numpy.percentile(memory_usage_list, 75)
                memory_p25 = numpy.percentile(memory_usage_list, 25)
                # print(memory_average)
                for result in result_list:
                    if result["datetime"] == data["datetime"]:
                        result["memory_average"] = memory_average
                        result["memory_max"] = memory_max
                        result["memory_min"] = memory_min
                        result["memory_p75"] = memory_p75
                        result["memory_p25"] = memory_p25
                if not any(result["datetime"] == data["datetime"]
                           for result in result_list):
                    data["memory_average"] = memory_average
                    data["memory_max"] = memory_max
                    data["memory_min"] = memory_min
                    data["memory_p75"] = memory_p75
                    data["memory_p25"] = memory_p25
                    result_list.append(data)
            elif "DISK" in file:
                disk_usage_list = get_csv_data(file, "Storage Used")
                if len(disk_usage_list) <= 0:
                    continue
                disk_average = numpy.average(disk_usage_list)
                disk_max = numpy.max(disk_usage_list)
                disk_min = numpy.min(disk_usage_list)
                disk_p75 = numpy.percentile(disk_usage_list, 75)
                disk_p25 = numpy.percentile(disk_usage_list, 25)
                for result in result_list:
                    if result["datetime"] == data["datetime"]:
                        result["disk_average"] = disk_average
                        result["disk_max"] = disk_max
                        result["disk_min"] = disk_min
                        result["disk_p75"] = disk_p75
                        result["disk_p25"] = disk_p25
                if not any(result["datetime"] == data["datetime"]
                           for result in result_list):
                    data["disk_average"] = disk_average
                    data["disk_max"] = disk_max
                    data["disk_min"] = disk_min
                    data["disk_p75"] = disk_p75
                    data["disk_p25"] = disk_p25
                    result_list.append(data)
    # print(text_file_list)
    return result_list


def parse_all_data(folder):
    folder_list = ["Vera_Monitor_log", "Monkey_log"]
    monitor_system_list = ["CPU", "MEM"]
    text_file_list = list()
    for platform_folder in folder_list:
        for monitor_system in monitor_system_list:
            text_file_list += glob.glob(
                os.path.join(folder, rf"{platform_folder}\**\qa_*_{monitor_system}.csv"), recursive=True)
    # qa_CPU_monitor.csv / qa_MEM_monitor.csv / qa_{process}_CPU.csv / qa_{process}_MEM.csv / qa_DISK_monitor.csv
    current_time = time.time()
    result_list = list()
    for file in text_file_list:
        if current_time - os.stat(file).st_mtime < TIME_RANGE \
                and "8_packages" not in file:
            print(file)
            datetime = re.search(r"\\([0-9_]+-[0-9_]+)\\", file).group(1)
            app_name = re.search(r"qa_com\.\w+\.(.+)_\w+\.csv", file).group(1).replace(".main", "")
            if "Vera" in file and not any(package in file for package in VERA_PACKAGE_LIST):
                continue
            file_folder = os.path.dirname(file)
            data = {"datetime": datetime, "app_name": app_name, "folder_path": file_folder}
            print(data)
            if any(keyword in file for keyword in ["Monkey_log", "AOSP_Monitor_log"]):
                data["platform"] = "AOSP"
            elif "Vera" in file:
                data["platform"] = "Vera"
            if "CPU" in file:
                cpu_data = []
                if any(is_column_exist(file, column_name) for column_name in ["CPU", "CPU %"]):
                    for column_name in ["CPU", "CPU %"]:
                        if is_column_exist(file, column_name):
                            cpu_data = get_csv_data(file, column_name)
                if len(cpu_data) <= 0:
                    continue
                cpu_average = numpy.average(cpu_data)
                cpu_max = numpy.max(cpu_data)
                cpu_min = numpy.min(cpu_data)
                cpu_p75 = numpy.percentile(cpu_data, 75)
                cpu_p25 = numpy.percentile(cpu_data, 25)

                for result in result_list:
                    if result["datetime"] == data["datetime"] and result["app_name"] == data["app_name"]:
                        result["cpu_average"] = cpu_average
                        result["cpu_max"] = cpu_max
                        result["cpu_min"] = cpu_min
                        result["cpu_p75"] = cpu_p75
                        result["cpu_p25"] = cpu_p25
                if not any(result["datetime"] == data["datetime"] and result["app_name"] == data["app_name"]
                           for result in result_list):
                    data["cpu_average"] = cpu_average
                    data["cpu_max"] = cpu_max
                    data["cpu_min"] = cpu_min
                    data["cpu_p75"] = cpu_p75
                    data["cpu_p25"] = cpu_p25
                    result_list.append(data)
            elif "MEM" in file:
                if "Monkey" in file:
                    column_name = "Memory"
                elif "Vera" in file:
                    column_name = "Memory %"
                else:
                    continue
                memory_data = get_csv_data(file, column_name)
                if len(memory_data) <= 0:
                    continue
                memory_average = numpy.average(memory_data)
                memory_max = numpy.max(memory_data)
                memory_min = numpy.min(memory_data)
                memory_p75 = numpy.percentile(memory_data, 75)
                memory_p25 = numpy.percentile(memory_data, 25)
                # print(memory_average)

                for result in result_list:
                    if result["datetime"] == data["datetime"] and result["app_name"] == data["app_name"]:
                        result["memory_average"] = memory_average
                        result["memory_max"] = memory_max
                        result["memory_min"] = memory_min
                        result["memory_p75"] = memory_p75
                        result["memory_p25"] = memory_p25
                        result["memory_data"] = memory_data
                if not any(result["datetime"] == data["datetime"] and result["app_name"] == data["app_name"]
                           for result in result_list):
                    data["memory_average"] = memory_average
                    data["memory_max"] = memory_max
                    data["memory_min"] = memory_min
                    data["memory_p75"] = memory_p75
                    data["memory_p25"] = memory_p25
                    data["memory_data"] = memory_data
                    result_list.append(data)
    # print(text_file_list)
    return result_list


def is_column_exist(file_path, column):
    with open(file_path, newline="") as csvfile:
        csv_dict = csv.DictReader(csvfile)

        if all(column in row.keys() and row[column] is not None for row in csv_dict):
            return True
        else:
            return False


def get_csv_data(file_path, column):
    if is_column_exist(file_path, column):
        with open(file_path, newline="") as csvfile:
            csv_dict = csv.DictReader(csvfile)
            result = list()
            for row in csv_dict:
                try:
                    result.append(float(row[column]))
                except (ValueError, TypeError):
                    continue
            return result
    else:
        return list()


def threshold_alert(result_list):
    database = db_tool.myDB("suspicious_log")
    alert_list = list()

    for result in (result for result in result_list if all(key in result.keys() for key in COLUMN_LIST)):
        app_name = result["app_name"]
        platform = result["platform"]
        where_clause = f"WHERE app_name='{app_name}' and platform='{platform}'"
        cpu_data_list = database.select_data("system_monitor_data", ["cpu_p75"], where_clause +
                                             " and cpu_p75 is not null")
        mem_data_list = database.select_data("system_monitor_data", ["memory_p75"], where_clause +
                                             " and memory_p75 is not null")
        cpu_p75 = round(result["cpu_p75"], 2)
        memory_p75 = round(result["memory_p75"], 2)
        cpu_threshold = round(numpy.average(cpu_data_list) * 1.1, 2)
        memory_threshold = round(numpy.average(mem_data_list) * 1.1, 2)
        if cpu_p75 > cpu_threshold:
            print(f"cpu p75: {cpu_p75} > {cpu_threshold}")
            status = "Fail"
        else:
            status = "Pass"
        cpu_content_dict = {"app_name": app_name, "platform": platform, "data_type": "CPU", "value": cpu_p75,
                            "threshold": cpu_threshold, "status": status}
        alert_list.append(cpu_content_dict)
        if memory_p75 > memory_threshold:
            print(f"memory p75: {memory_p75} > {memory_threshold}")
            status = "Fail"
        else:
            status = "Pass"
        memory_content_dict = {"app_name": app_name, "platform": platform, "data_type": "Memory",
                               "value": memory_p75,
                               "threshold": memory_threshold, "status": status, "memory_data": result["memory_data"]}
        alert_list.append(memory_content_dict)

    sending_report_mail(alert_list)


def sending_report_mail(alert_list):
    today_date = date.strftime(date.today(), "%Y_%m_%d")
    summary = f"[SAW] System Monitor - {today_date}"
    recipients = [
        "JackCHLin@mobiledrivetech.com"
    ]
    ccs = ["StanleyCLChang@mobiledrivetech.com",
           "LynnLYLin@mobiledrivetech.com",
           "AllenACLiu@mobiledrivetech.com",
           "JalenWang@mobiledrivetech.com",
           "SherlockHuang@mobiledrivetech.com",
           "LarryHZLai@mobiledrivetech.com",
           "JeffYJChen@mobiledrivetech.com",
           "WandyWTChang@mobiledrivetech.com",
           "JackyQLCai@mobiledrivetech.com"
           ]
    recipients += set(mail_tool.fetch_mail_group("saw_mail_group",
                                                 "where position = 'Tech Leader' "
                                                 "or position like '%QA%'"))
    mail_body = f"<h1> [SAW] System Monitor Log, {today_date} </h1><p>\n"
    mail_body += "<h2>Please refer to the link below for details</h2>"
    mail_body += f"<h2><a href=\"{DASHBOARD_LINK}\">Dashboard link</a></h2>\n"
    cpu_filter_data = [filter_data for filter_data in alert_list if filter_data["data_type"] == "CPU"]
    mem_filter_data = [filter_data for filter_data in alert_list if filter_data["data_type"] == "Memory"]
    print(cpu_filter_data)
    print(mem_filter_data)

    if len(cpu_filter_data) > 0:
        mail_body += "<h3>Cpu :</h3>\n"
        cpu_table_html = f"<blockquote><table border=\"1\">" \
                         "<tr>" \
                         "<th>Platform</th>\n" \
                         "<th>App name</th>\n" \
                         "<th>CPU P75</th>\n" \
                         "<th>Threshold</th>\n" \
                         "<th>Status</th></tr>\n"
        for alert_data in cpu_filter_data:
            cpu_table_html += "<tr>"
            for data in [alert_data["platform"], alert_data["app_name"], alert_data["value"], alert_data["threshold"]]:
                cpu_table_html += f"<th>{data}</th>"
            if alert_data["status"] == "Pass":
                cpu_table_html += f"<th><font color='green'>Pass</font></th>"
            else:
                cpu_table_html += f"<th><font color='red'>Fail</font></th>"
            cpu_table_html += "</tr>"
        cpu_table_html += "</table></blockquote>"
        mail_body += cpu_table_html

    if len(mem_filter_data) > 0:
        mail_body += "<h3>Memory :</h3>\n"
        mem_table_html = f"<blockquote><table border=\"1\">" \
                         "<tr>" \
                         "<th>Platform</th>\n" \
                         "<th>App name</th>\n" \
                         "<th>Memory P75</th>\n" \
                         "<th>Threshold</th>\n" \
                         "<th>Status</th></tr>\n"
        for alert_data in mem_filter_data:
            mem_table_html += "<tr>"
            for data in [alert_data["platform"], alert_data["app_name"], alert_data["value"], alert_data["threshold"]]:
                mem_table_html += f"<th>{data}</th>"
            if alert_data["status"] == "Pass":
                mem_table_html += f"<th><font color='green'>Pass</font></th>"
            else:
                mem_table_html += f"<th><font color='red'>Fail</font></th>"
            mem_table_html += "</tr>"
        mem_table_html += "</table></blockquote>"
        mail_body += mem_table_html
        mail_body += "<i>The status will show fail while this P75's value > past P75 average * 1.1 </i><br>\n"

    mail_body += "</blockquote><br>\n"
    body = (
            "<html>\n"
            "<body>\n"
            + mail_body
            + "This tool scans all CPU / Memory monitor logs generated by QA on a daily basis.<br>\n"
              "Thank you for your attention. If any questions, please contact with auto test team.<br>"
              "===================================================================<br>\n"
              "AutoTeam members:<br>\n"
              "SherlockHuang@mobiledrivetech.com <br> \n"
              "LarryHZLai@mobiledrivetech.com <br>\n"
              "JeffYJChen@mobiledrivetech.com <br>\n"
              "Note: This email is automated sent by system. Do not reply this mail.<br>\n"
              "To add or remove receivers, Please contact with Sherlock. Thanks<br>\n"
              "===================================================================<br>\n"
              "\n"
              "</body>\n"
              "</html>\n"
    )
    report_mail = mail_tool.Mail(recipients_list=recipients, cc_list=ccs,
                                 title=summary, body=body)
    print(report_mail.recipients_list)
    with open("output.html", "w+") as file:
        file.write(body)
    report_mail.send_mail()


def modify_recipients(recipients, result_list):
    keyword_dict = [
        {
            "module": "Settings",
            "keyword": "setting",
        },
        {
            "module": "Home Screen",
            "keyword": "launcher",
        },
        {
            "module": "HVAC",
            "keyword": "hvac",
        },
        {
            "module": "HMI-IVI Applications",
            "keyword": "devicemanager"
        }
    ]
    for result_dict in result_list:
        app_name = result_dict["app_name"]
        for item in keyword_dict:
            if re.search(item["keyword"], app_name):
                module = item["module"]
                mail_group = mail_tool.fetch_mail_group("saw_mail_group", module=f"{module}")
                recipients += mail_group
    recipients = list(set(recipients))
    print(recipients)
    return recipients


if __name__ == '__main__':
    db = db_tool.myDB("suspicious_log")
    data_list = parse_all_data(DIRECTORY)
    print(data_list)
    threshold_alert(data_list)
    for dataset in data_list:
        key_list = ["datetime", "app_name",
                    "cpu_average", "cpu_max", "cpu_min", "cpu_p75", "cpu_p25",
                    "memory_average", "memory_max", "memory_min", "memory_p75", "memory_p25",
                    "platform"]
        insert_key_list = list()
        insert_data_list = list()
        for key in key_list:
            if key in dataset.keys():
                insert_key_list.append(key)
                insert_data_list.append(dataset[key])
        try:
            db.insert_data("system_monitor_data", insert_key_list, insert_data_list)
        except db_tool.pymysql.err.IntegrityError:
            print(traceback.format_exc())

    data_total_list = parse_all_data_total(DIRECTORY)
    for dataset in data_total_list:
        print(dataset)
        key_list = ["datetime",
                    "cpu_average", "cpu_max", "cpu_min", "cpu_p75", "cpu_p25",
                    "memory_average", "memory_max", "memory_min", "memory_p75", "memory_p25",
                    "disk_average", "disk_max", "disk_min", "disk_p75", "disk_p25",
                    "platform"]
        insert_key_list = list()
        insert_data_list = list()
        for key in key_list:
            if key in dataset.keys():
                insert_key_list.append(key)
                insert_data_list.append(dataset[key])
        try:
            db.insert_data("system_monitor_data_total",
                           insert_key_list,
                           insert_data_list)
        except db_tool.pymysql.err.IntegrityError:
            print(traceback.format_exc())

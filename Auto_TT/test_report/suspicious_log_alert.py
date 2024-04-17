import glob
import os
import re
import sys
import time
import traceback
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules import mail_tool
from DB_tool import db_tool

# 設定要遍歷的目錄
DIRECTORY = r"\\md-test\Projects\SAW"

DASHBOARD_LINK = "http://10.57.41.216:3000/d/ca62e05b-c3de-4324-b27d-884601552ed5/" \
                 "suspicious-log?orgId=1&from=now-7d&to=now"
# 設定要打撈的key word， 一律小寫，方便字串比對
KEYWORD_LIST = [
    "deprecated",
    "catch exception",
    "must override",
    "illegalargument",
    "illegalstate",
    "never happen",
    "unlikely happen",
    "intentionally poll",
    "retry",
    "force delay",
    "workaround"
]
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
KEYWORD_COUNT = dict().fromkeys(KEYWORD_LIST, 0)
APP_RESULT_LIST = list()
TODAY = date.today()
TODAY_DATE = date.strftime(TODAY, "%Y_%m_%d")
OUTPUT_FILE = f"{TODAY.year}-{TODAY.month}-{TODAY.day}.html"

# All recipients
RECIPIENTS_LIST = [
    "JohnJYChen@mobiledrivetech.com",
    "HueiJheYu@mobiledrivetech.com",
    "JackCHLin@mobiledrivetech.com",
    "AllenACLiu@mobiledrivetech.com",
    "SherlockHuang@mobiledrivetech.com",
    "LarryHZLai@mobiledrivetech.com",
    "TingATTsai@mobiledrivetech.com",
    "LeoLMWeng@mobiledrivetech.com",
    "LynnLYLin@mobiledrivetech.com",
    "StanleyCLChang@mobiledrivetech.com"
]


def parse_pid(filename):
    pid_list = list()
    # use several encodings to open logcat file to avoid exception
    encodings = ['utf-8', 'utf-8-sig', 'latin-1']
    for encoding in encodings:
        try:
            with open(filename, "r", encoding=encoding) as file:
                lines = file.readlines()
                break
        except UnicodeDecodeError:
            print("Encode error")
            continue
    if "logcat" in filename:
        for line in lines:
            if any(keyword in line for keyword in ["wm_on_paused_called", "wm_on_resume_called"]):
                regex_package_name = re.search(r"(com\.\w+\.\w+)", line)
                regex_pid = re.search(r"\(\s+([0-9]+)\)", line)
            elif "am_proc_start" in line:
                regex_package_name = re.search(r"(com\.\w+\.\w+)", line)
                regex_pid = re.search(r"\[[0-9]+,([0-9]+),[0-9]+", line)
            else:
                regex_pid, regex_package_name = None, None
            if regex_pid and regex_package_name:
                if any(company_name in regex_package_name.group(1)
                       for company_name in ["mobiledrivetech", "stellantis"]):
                    regex_dict = {"pid": regex_pid.group(1), "package": regex_package_name.group(1)}
                    pid_list.append(regex_dict)
    elif "vera" in filename:
        for line in lines:
            if "resmgr-pss-logger" in line:
                regex_package_name = re.search(r"appName\((com[.\w]+)\)", line)
                regex_pid = re.search(r"pid\(([0-9]+)\)", line)
                try:
                    package_name = regex_package_name.group(1).replace(".main", "")
                    if any(package in line for package in VERA_PACKAGE_LIST):
                        regex_dict = {"pid": regex_pid.group(1), "package": package_name}
                        pid_list.append(regex_dict)
                except AttributeError:
                    # print("Failed, " + line)
                    pass

    return pid_list


def parse_log_file(filename):
    """
    尋找檔案中是否有keyword, 有則輸出到今日報告
    Args:
        filename: File path to parse

    Returns: the parsing result dict

    """
    # 尋找檔案中是否有keyword, 有則輸出到今日報告
    # 開啟的檔案支援三種編碼

    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    for encoding in encodings:
        try:
            with open(filename, "r", encoding=encoding) as file:
                log_data = file.readlines()
                break
        except UnicodeDecodeError:
            print("Encode error")
            continue
    output_data = open(OUTPUT_FILE, "a")
    if "Monkey_log" in filename:
        root = os.path.dirname(filename)
        package_text_file = glob.glob(os.path.dirname(root) + "/**/Test_packages.txt", recursive=True)
        # print(package_text_file)
        with open(package_text_file[0], "r") as data:
            packages = data.readlines()
            # app_name = "\n".join((re.search(r"com.\w+.(.+)", package).group(1) for package in packages))
            # print(app_name)
        platform = "AOSP"
    elif "Vera_Monitor_log" in filename:
        app_name = re.search(r"Vera_Monitor_log\\([a-z A-Z . 0-9 _]+)", filename).group(1)
        # if re.match("[0-9]+", app_name):
        #     app_name = re.search(r"\\[0-9 _ -]+\\([a-z]+)\\", filename).group(1)
        platform = "Vera"
    elif "AOSP_Monitor_log" in filename:
        # app_name = re.search(r"AOSP_Monitor_log\\([a-z A-Z]+)", filename).group(1)
        platform = "AOSP"
    else:
        raise ValueError(f"Error filepath, {filename}")
    datetime = re.search(r"([0-9-]+_[0-9]+_[0-9]+-[0-9]+_[0-9]+_[0-9]+)", filename).group(1)
    # app_result_dict = {"platform": platform, "datetime": datetime, app_name: dict().fromkeys(KEYWORD_LIST, 0)}
    output_data.write(
        f"<h3><span style='color: black;'> [<a href='{filename}'>Log File Link</a>] Suspicious "
        f"Logs Found in this file: </span>"
        f"<span style='color: green;'>{filename}</span> </h3><p>"
    )
    pid_list = parse_pid(filename)
    pid_result_list = list()
    for line_count, line in enumerate(log_data):
        if any(keyword in line for keyword in KEYWORD_COUNT.keys()):
            keyword = list(keyword for keyword in KEYWORD_COUNT.keys() if keyword in line)[0]
            number_list = re.findall("[0-9]+", line)
            if any(pid_dict["pid"] == number for pid_dict in pid_list for number in number_list):
                package = \
                    list(pid_dict["package"] for pid_dict in pid_list for number in number_list
                         if pid_dict["pid"] == number)[0]
            else:
                package = "other"
            pid_result_list.append({"datetime": datetime,
                                    "package": package,
                                    "platform": platform,
                                    "keyword": keyword,
                                    "line": line,
                                    "line_count": line_count})

    package_list = set(pid["package"] for pid in pid_list)
    table_data = f"<table border=\"1\">" \
                 "<tr><th>pid</th>\n" \
                 "<th>package</th></tr>\n"
    for package in package_list:
        pid_str = ",".join(set(list(pid['pid'] for pid in pid_list if pid['package'] == package)))
        table_data += f"<tr><th>{pid_str}</th>\n"
        table_data += f"<th>{package}</th></tr>\n"
    table_data += "</table>"
    output_data.write(table_data)
    for package in package_list:
        result_list = list(result for result in pid_result_list if package == result["package"])
        if len(result_list) > 0:
            output_data.write(f"<h3><span style='color: black;'> {package} </span></h3>")
            for result in result_list:
                output_data.write(
                    f" <span style='color: blue;'> [line:{result['line_count'] + 1}, KeyWord:{result['keyword']}] "
                    f"--> </span> <span style='color: black;'>{result['line']}"
                    + "</span><br>"
                )
    if len(list(result for result in pid_result_list if result["package"] == "other")) > 0:
        output_data.write(f"<h3><span style='color: black;'> other </span></h3>")
        for result in list(result for result in pid_result_list if result["package"] == "other"):
            output_data.write(
                f" <span style='color: blue;'> [line:{result['line_count'] + 1}, KeyWord:{result['keyword']}] "
                f"--> </span> <span style='color: black;'>{result['line']}"
                + "</span><br>"
            )

    global APP_RESULT_LIST
    APP_RESULT_LIST += pid_result_list
    return pid_result_list


def parse_all_data(folder):
    """
    To call parse_log_file by for loop and os.walk()
    Args:
        folder: The top folder of log data
    """
    # 獲取當前時間

    current_time = time.time()
    time_range = 24 * 60 * 60
    # 開始遍歷目錄
    for root, dirs, files in os.walk(folder):
        # 獲取目錄的修改時間
        modified_time = os.stat(root).st_mtime

        # 判斷目錄是否在最近一天內有變動
        if current_time - modified_time > time_range:
            continue

        for file in files:
            # 獲取檔案的完整路徑
            file_path = os.path.join(root, file)
            if any(keyword in file_path for keyword in ["logcat.txt", "vera_log.log", "vera_journalctl.log"]):
                # 獲取檔案的修改時間
                modified_time = os.stat(file_path).st_mtime

                # 判斷檔案是否在最近一天內有變動
                if current_time - modified_time <= time_range:
                    # 如果是 logcat 或 vera 產出的 log file 才進行分析
                    print(file_path)
                    try:
                        parse_log_file(file_path)
                    except Exception:
                        print(f"Parsing data failed for {file}, " + traceback.format_exc())
                        continue


def modify_mail_body(filename):
    """
    Create HTML mail body for sending mail
    Args:
        filename: the output file path

    Returns: the mail body

    """
    with open(filename, "r+") as file:
        content = file.read()
        file.seek(0, 0)
        file.write(f"<head> <title> [SAW] Suspicious Logs Alert </title></head>")
        file.write(
            f"<body> <h1> [SAW] Suspicious Logs Alert, {TODAY.year}-{TODAY.month}-{TODAY.day} </h1><p>\n"
        )
        mail_body = f"<body> <h1> [SAW] Suspicious Logs Alert, {TODAY.year}-{TODAY.month}-{TODAY.day} </h1><p>\n"

        file.write(f"<h2><a href=\"{DASHBOARD_LINK}\">Dashboard link</a>\n")
        mail_body += f"<h2><a href=\"{DASHBOARD_LINK}\">Dashboard link</a>\n"
        file.write("<h2>Total :</h2>\n<blockquote>")
        mail_body += "<h2>Total :</h2>\n<blockquote>"
        for key in KEYWORD_COUNT.keys():

            # 計數器不為 0 的 keyword 才顯示
            value = len(list(data for data in APP_RESULT_LIST if data["keyword"] == key))
            if value > 0:
                result = f"<h2>[<span style='color: blue;'>{key}</span>] " \
                         f"appears [<span style='color: blue;'>{value}</span>] times</h2>\n"
                file.write(result)
                mail_body += result
        file.write("</blockquote>\n")
        mail_body += "</blockquote>\n"
        table_html = f"<table border=\"1\">" \
                     "<tr>" \
                     "<th>Platform</th>\n" \
                     "<th>Package name</th>\n"
        for keyword in KEYWORD_LIST:
            table_html += f"<th>{keyword}</th>\n"
        table_html += "</tr>"
        for platform in set(list(result["platform"] for result in APP_RESULT_LIST)):
            for package_name in set(
                    list(result["package"] for result in APP_RESULT_LIST if result["platform"] == platform)):
                table_html += f"<tr><th>{platform}</th>\n"
                table_html += f"<th>{package_name}</th>\n"
                for keyword in KEYWORD_LIST:
                    keyword_count = len(list(result for result in APP_RESULT_LIST if
                                             result["platform"] == platform and result["package"] == package_name and
                                             result["keyword"] == keyword))
                    table_html += f"<th>{keyword_count}</th>\n"
                table_html += "</tr></th>\n"
        table_html += "</table>"

        file.write(table_html)
        mail_body += table_html

        file.write("<br><p>")
        file.write(content)
    body = (
            "<html>\n"
            "<body>\n"
            + mail_body
            + "<br><br>Attachment is today's Suspicious Logs Alert Report for [SAW].<br>\n"
              "This tool scans all logs generated by QA on a daily basis.<br>\n"
              "And attachment is the summary of suspicious keywords found in the test logs.<br>\n"
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
    return body


def upload_result_to_db():
    """
    Insert data to database which keyword's count > 0
    """
    database = db_tool.myDB("suspicious_log")
    for datetime in set(list(result["datetime"] for result in APP_RESULT_LIST)):
        for platform in set(list(result["platform"] for result in APP_RESULT_LIST)):
            for package in set(list(result["package"] for result in APP_RESULT_LIST)):
                for keyword in KEYWORD_LIST:
                    keyword_count = len(list(result for result in APP_RESULT_LIST if result["platform"] == platform
                                             and result["keyword"] == keyword
                                             and result["package"] == package
                                             and result["datetime"] == datetime))
                    if keyword_count > 0:
                        database.insert_data("log_data",
                                             ["datetime", "package", "keyword", "count", "platform"],
                                             [datetime, package, keyword, keyword_count, platform])


def modify_recipients(recipient_list, result_list):
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
    for app_result_dict in result_list:
        app_name = list(app_result_dict.keys())[1]
        for item in keyword_dict:
            if re.search(item["keyword"], app_name):
                module = item["module"]
                mail_group = mail_tool.fetch_mail_group("saw_mail_group", module=f"{module}")
                print(mail_group)
                recipient_list += mail_group
                print(recipient_list)
    return recipient_list


if __name__ == '__main__':
    parse_all_data(DIRECTORY)
    # print(APP_RESULT_LIST)
    # modify_recipients(RECIPIENTS_LIST, APP_RESULT_LIST)
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
    import zipfile
    zip_file = f'{TODAY.year}-{TODAY.month}-{TODAY.day}.zip'
    with zipfile.ZipFile(zip_file, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=5) as zf:
        zf.write(OUTPUT_FILE)

    if os.path.getsize(OUTPUT_FILE) > 480:
        mail = mail_tool.Mail(recipients_list=recipients,
                              cc_list=ccs,
                              attachment_list=[zip_file],
                              body=modify_mail_body(OUTPUT_FILE),
                              title=f"[SAW] Suspicious Log - {TODAY_DATE}")
        try:
            mail.send_mail()
        except Exception:
            print("Mail sending fail:" + traceback.format_exc())
    else:
        print("檔案內容僅含標題，今日無 suspicious log alert 。已删除文件")
    os.remove(OUTPUT_FILE)
    os.remove(zip_file)
    try:
        upload_result_to_db()

    except db_tool.pymysql.err.IntegrityError:
        print(traceback.format_exc())

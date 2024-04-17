import glob
import os
import re
import sys
import time

from .common import *

# 設定 Regular expression 的Pattern
REGEX_PATTERN_SUBJECT_ANR = "(.+Exception: [a-z A-Z 0-9 .]+)\n"
REGEX_PATTERN_SUBJECT_CRASH = "(.+Exception: [a-z A-Z 0-9 .]+)"
REGEX_PATTERN_SUBJECT_NATIVE_CRASH = "Abort message: '(.+)'\n"
REGEX_PATTERN_PROCESS = "Process: ([a-z . A-Z]+)\n"
REGEX_PATTERN_BUILD = "Build: (.+)"
# 將帶入的參數作為list 帶入
path_list = sys.argv
# 將Parse完的結果儲存起來
result_list = []


def get_all_full_filepath(filepath):
    """
    get the files under the given path
    Args:
        filepath:

    Returns: list with log files

    """
    result = []
    # 因為dropbox的資料夾內會有壓縮檔,沒辦法讀取, 所以透過副檔名篩選的方式找出txt檔
    for f in os.listdir(filepath):
        if f.endswith(".txt") and os.path.isfile(os.path.join(filepath, f)):
            result.append(os.path.join(filepath, f))
    return result


# input: filepath - 欲parse的檔案路徑
def log_parser(filepath):
    """
    Parse all data under the given route
    Args:
        filepath: the folder which stored data
    """
    result = get_all_full_filepath(filepath)
    # print(result)
    for file in result:
        # 這邊因為要取撈出的資料的第一筆資料([0]), 有幾筆資料會撈不到東西所以會報error, 所以用try catch的方式去處理
        try:
            f = open(file)
            ctx = f.read()
            if "anr" in file or "native_crash" in file:
                subject = os.path.basename(file)
            elif "app_crash" in file or "system_server_crash" in file:
                regex_pattern_subject = REGEX_PATTERN_SUBJECT_CRASH
                subject = re.findall(regex_pattern_subject, ctx)[0]
            else:
                continue
            process = re.findall(REGEX_PATTERN_PROCESS, ctx)[0]
            build = re.findall(REGEX_PATTERN_BUILD, ctx)[0]
            f.close()
            issue_result = JiraIssue(subject, process, build, file)
            # To filter the duplicate issue and add times for each issue to count fail times
            if not any(
                    issue_result.build == result.build
                    and issue_result.process == result.process
                    and issue_result.subject == result.subject
                    for result in result_list
            ):
                result_list.append(issue_result)
            else:
                next((result for result in result_list if
                      issue_result.build == result.build
                      and issue_result.process == result.process
                      and issue_result.subject == result.subject), None).times += 1

        except IndexError:
            print(str(sys.exc_info()))


if __name__ == "__main__":
    for path in path_list:
        if path == path_list[0]:
            pass
        else:
            log_parser(path)
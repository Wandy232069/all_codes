import os
import re
import sys

from .common import *

# 設定 Regular expression 的Pattern
REGEX_PATTERN_SUBJECT = r"(^Subject:[\w ()]+)"
REGEX_PATTERN_PROCESS = "Cmd line: (.+)"
REGEX_PATTERN_BUILD = "Build fingerprint: '(.+)'"
# 將Parse完的結果儲存起來
result_list = []


def get_all_full_filepath(filepath):
    """
    get the files under the given path
    Args:
        filepath:

    Returns: list with log files

    """
    result = [
        os.path.join(filepath, f)
        for f in os.listdir(filepath)
        if os.path.isfile(os.path.join(filepath, f))
    ]
    return result


def log_parser(filepath):
    """
    Parse all data under the given route
    Args:
        filepath: the folder which stored data
    """
    result = get_all_full_filepath(filepath)
    # 透過for 迴圈跟 regular expression 把三個資訊撈出+寫入result_list
    for file in result:
        f = open(file)
        ctx = f.read()
        f.close()
        try:
            process = re.findall(REGEX_PATTERN_PROCESS, ctx)[0]
            build = re.findall(REGEX_PATTERN_BUILD, ctx)[0]
            if "trace" not in file:
                subject = re.findall(REGEX_PATTERN_SUBJECT, ctx)[0]
                issue_result = JiraIssue(subject, process, build, file)
            else:
                issue_result = JiraIssue("no subject, file by trace file", process, build, file)
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
    log_parser(
        r"\\MD-TEST\Projects\SAW\Monkey_log\2023_08_29_com.mobiledrivetech.assisteddrivingpage\bugreport\BR_2023_08_29-03_30_17\anr")

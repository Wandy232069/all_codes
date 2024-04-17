import os
import re
import sys

from .common import *


# 設定 Regular expression 的Pattern
REGEX_PATTERN_SUBJECT = "Cause: (.+)"
REGEX_PATTERN_PROCESS = "Cmdline: (.+)"
REGEX_PATTERN_BUILD = "Build fingerprint: '(.+)'"
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
    # tombstone.pb檔,沒辦法讀取, 所以透過副檔名篩選的方式找出txt檔
    for f in os.listdir(filepath):
        if not (f.endswith(".pb")) & os.path.isfile(os.path.join(filepath, f)):
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

    for file in result:
        try:
            f = open(file)
            ctx = f.read()
            subject = re.findall(REGEX_PATTERN_SUBJECT, ctx)[0]
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

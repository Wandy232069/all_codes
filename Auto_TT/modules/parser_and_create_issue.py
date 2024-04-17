import traceback
try:
    from issue_parsers import issue_parser_anr, issue_parser_dropbox, issue_parser_tombstone
    from jira_tool import jira_issue_create_tool
except ImportError:
    from .issue_parsers import issue_parser_anr, issue_parser_dropbox, issue_parser_tombstone
    from .jira_tool import jira_issue_create_tool
import sys

from pathlib import Path
import os

# 將帶入的參數作為list 帶入
PATH_LIST = sys.argv


def call_parser(dir_path):
    """
    init the bugreports folders and call the parsers
    Args:
        dir_path: string : the folder path
    """
    filepath_anr = str(Path(dir_path + "/anr/"))
    filepath_dropbox = str(Path(dir_path + "/dropbox"))
    filepath_tombstone = str(Path(dir_path + "/tombstones"))
    if os.path.exists(filepath_anr):
        issue_parser_anr.log_parser(filepath_anr)
    if os.path.exists(filepath_dropbox):
        issue_parser_dropbox.log_parser(filepath_dropbox)
    if os.path.exists(filepath_tombstone):
        issue_parser_tombstone.log_parser(filepath_tombstone)


def fetch_data(dir_path, time):
    """
    fetch, parse data in bugreport folder and file issue to JIRA
    Args:
        dir_path: the bugreport path
        time: string time, to combine the folder path
    """
    call_parser(dir_path)
    jira = jira_issue_create_tool.jira_tool()
    jira_link = jira_issue_create_tool.JIRA_LINK
    # Use for loop to get those parsed data
    new_issue_list = list()
    duplicate_issue_list = list()

    for results in [issue_parser_anr.result_list, issue_parser_dropbox.result_list, issue_parser_tombstone.result_list]:
        for result in results:
            print(result)
            summary_prefix = ""
            if results == issue_parser_anr.result_list:
                summary_prefix = "[ANR]"
            elif results == issue_parser_dropbox.result_list:
                summary_prefix = "[DROPBOX]"
            elif results == issue_parser_tombstone.result_list:
                summary_prefix = "[TOMBSTONE]"
            if get_build_into(dir_path, time):
                build = get_build_into(dir_path, time)
            else:
                build = result.build
            # Format the data from log and create issues
            summary = summary_prefix + "[" + result.process + "]" + result.subject
            description = (
                    "Process:  "
                    + result.process
                    + "\nBuild:  "
                    + build
                    + "\nError message: "
                    + result.subject
            )
            print(summary)
            search_keyword = result.process + " " + result.subject

            # if the issue is already filed, upload attachment. File new issue if not.
            try:
                if len(jira.fetch_duplicated_issues(search_keyword)) != 0:
                    for issue in jira.fetch_duplicated_issues(search_keyword):
                        # duplicate_issue_list.append(issue)

                        jira_issue = jira.create_issue(search_keyword, summary, description, result.filename)
                        result.attach_jira_issue(jira_issue)
                        duplicate_issue_list.append(result)
                else:
                    new_issue = jira.create_issue(search_keyword, summary, description, result.filename)
                    # new_issue_list.append(new_issue)
                    result.attach_jira_issue(new_issue)
                    new_issue_list.append(result)
            except Exception:
                print(traceback.format_exc())
    # Write down the output summary
    output_folder = os.path.dirname(os.path.dirname(dir_path)) + os.sep + "outputFolder" + os.sep
    with open(output_folder + time + os.sep + "JIRA_result_output.txt", "w") as fo:
        fo.writelines(f"New issues x {len(new_issue_list)}:\n")
        for issue in new_issue_list:
            fo.writelines(
                issue.jira_issue.key + " x" + str(issue.times) + " " + issue.jira_issue.fields.summary + "\n")
            fo.writelines(jira_link + issue.jira_issue.key + "\n")
        fo.writelines(f"Duplicate issues x {len(duplicate_issue_list)}:\n")
        for issue in duplicate_issue_list:
            fo.writelines(
                issue.jira_issue.key + " x" + str(issue.times) + " " + issue.jira_issue.fields.summary + "\n")
            fo.writelines(jira_link + issue.jira_issue.key + "\n")


def get_build_into(folder, date):
    output_folder = os.path.dirname(os.path.dirname(folder)) + os.sep + "outputFolder" + os.sep + date
    build_info_file = list(output_folder + os.sep + file for file in os.listdir(output_folder) if "Build_info" in file)
    if len(build_info_file) > 0:
        with open(build_info_file[0], mode="r", encoding="utf-8") as file:
            return file.readline()
    else:
        return None


if __name__ == "__main__":
    fetch_data(
       r"\\MD-TEST\Projects\SAW\Monkey_log\2024_03_27_com.stellantis.devicemanager\bugreport\BR_2024_03_27-05_43_58",
        "2024_03_27-05_43_58")
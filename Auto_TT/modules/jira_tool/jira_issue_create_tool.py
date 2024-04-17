import re

from jira import JIRA

JIRA_PROJECT = "SAW"  # "SAW"  "TEST"
# JIRA_PROJCET = "TEST"

JIRA_LINK = "https://jiratepz1.mobiledrivetech.com/browse/"


class jira_tool:
    JIRA_URL = "https://jiratepz1.mobiledrivetech.com/"
    USERNAME = "qaautotest"
    PASSWORD = "MobileDrive#01"
    AUTH_INFO = (USERNAME, PASSWORD)

    # init jira service, ask user to input account & password
    def __init__(self):
        # self.username = input("Please Enter your JIRA account\n")
        # self.password = getpass.getpass("Please Enter your JIRA password\n")
        self.AUTH_INFO = (self.USERNAME, self.PASSWORD)
        self.jira = JIRA(self.JIRA_URL, auth=self.AUTH_INFO)

    # To search issue by given key
    # self: object, jira_tool
    # key: str, the issue key, e,g, "SAW-0001"
    def search_issue_by_key(self, key):
        issue = self.jira.issue(key)
        print(issue.key, issue.fields.summary)

    # check if there are duplicated issue(s), return the result list
    def fetch_duplicated_issues(self, keyword):
        keyword = re.sub("([{}()])", " ", keyword)
        search_test = (
                "project="
                + JIRA_PROJECT
                + " AND resolution=Unresolved AND description ~'"
                + keyword
                + "'"
        )
        search_issue = self.jira.search_issues(search_test)
        return search_issue

    def create_issue(self, keyword, summary, description, filename):
        """
        create new issue by given data if there is no same issue on JIRA.
        Attach new log to the deplicated issue if it exist.
        Args:
            keyword: the keyword to find if there is any duplicate issue in Jira
            summary: the issue summary
            description: the content to add in issue
            filename: the attachment filename

        Returns: the Jira object - Issue

        """
        if len(self.fetch_duplicated_issues(keyword)) > 0:
            for duplicated_issue in self.fetch_duplicated_issues(keyword):
                self.jira.add_attachment(issue=duplicated_issue, attachment=filename)
                self.jira.add_comment(duplicated_issue, description)
                print(duplicated_issue)
                return duplicated_issue
        else:
            issue_info = {
                "project": {"key": JIRA_PROJECT},
                "issuetype": {"name": "Bug"},  # {"name": "Bug"} {"name": "SW Bug"}
                # "issuetype": {"name": "SW Bug"},
                "summary": summary,
                "description": description,
            }
            new_issue = self.jira.create_issue(fields=issue_info)
            print(new_issue)
            self.jira.add_attachment(
                issue=self.jira.issue(new_issue), attachment=filename
            )
            return new_issue


if __name__ == "__main__":
    jira = jira_tool()
    jira.search_issue_by_key("SAW-3284")

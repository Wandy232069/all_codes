# 定義一個類別 issue 把結果作為物件儲存起來
class JiraIssue:
    times = 1

    def __init__(self, subject, process, build, filename):
        self.jira_issue = None
        self.subject = subject
        self.process = process
        self.build = build
        self.filename = filename

    def attach_jira_issue(self, jira_issue):
        self.jira_issue = jira_issue

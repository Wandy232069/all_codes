import os
import smtplib
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..')))
from DB_tool import db_tool


def make_attachment(name, file_path):
    """
    Add attachment in mail
    Args:
        name: the filename which will show in mail
        file_path: the path to get attachment file

    Returns:

    """
    with open(file_path, 'rb') as file:
        attachment_content = MIMEApplication((file.read()))
        file.close()

    attachment_content["Content-Disposition"] = f'attachment; filename="{name}"'

    return attachment_content


class Mail:

    def __init__(self, title, body, recipients_list, cc_list=None, attachment_list=None):
        if cc_list is None:
            self.cc_list = []
        else:
            self.cc_list = cc_list
        if attachment_list is None:
            self.attachment_list = []
        else:
            self.attachment_list = attachment_list

        self.body = body
        self.title = title
        self.recipients_list = recipients_list

    def send_mail(self):
        smtp = smtplib.SMTP('10.57.48.9', 25)
        smtp.ehlo()
        smtp.starttls()
        mail = MIMEMultipart()
        mail.attach(MIMEText(self.body, 'html', 'utf-8'))
        mail['From'] = 'qaautotest@fih-foxconn.com'
        mail["To"] = ",".join(self.recipients_list)
        mail["Cc"] = ",".join(self.cc_list)
        mail["Subject"] = self.title

        for result in self.attachment_list:
            attachment = make_attachment(f"{os.path.basename(result)}", result)
            mail.attach(attachment)

        print("Sending test report...")
        print(mail)
        print(smtp.send_message(mail))
        smtp.close()


def fetch_mail_group(table_name: str, where_clause: str):
    """
    to get user list from database by given condition
    Args:
        where_clause: the filter for SQL
        table_name: the table to search mail group data

    Returns:the list of tuple, which contain all value for all fields, can specific the datatype by  column_list

    """

    mail_group_db = db_tool.myDB("mail_group")
    mail_list = list()
    for mail_data in mail_group_db.select_data(table_name=table_name, column_list=["mail"],
                                               where_clause=where_clause):
        mail_list.append(mail_data[0])
    return mail_list


if __name__ == '__main__':
    print(set(fetch_mail_group("saw_mail_group",
                               "where position in ('PM', 'SM', 'Tech Leader') "
                               "or position like '%PO%'")))
    print(set(fetch_mail_group("saw_mail_group",
                               "where position like '%QA%'")))

import sys, os, shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules import ftp_tool

# FTP related info
AUTO_FTP_SERVER_IP = "10.57.41.216"
AUTO_QA_ACCOUNT = "qaautotest"
AUTO_QA_PASSWORD = "MobileDrive#01"

CN_FTP_IP = "ftp1and1.mobiledrivetech.com"
CN_FTP_ACCOUNT = "sharpmdt"
CN_FTP_PASSWORD = "sharpmdtTheLostWorld"

if __name__ == '__main__':
    ftp_tool.download_dirs(CN_FTP_IP, CN_FTP_ACCOUNT, CN_FTP_PASSWORD, "/mobiledrivetech/PROJECT/SAW/Auto_team",
                           os.path.dirname(__file__))
    ftp_tool.upload_dirs(AUTO_FTP_SERVER_IP, AUTO_QA_ACCOUNT, AUTO_QA_PASSWORD, os.path.dirname(__file__), "/")
    path = os.path.dirname(__file__)
    for item in os.listdir(path):
        if os.path.isdir(os.path.join(path, item)):
            shutil.rmtree(os.path.join(path, item))

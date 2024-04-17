import sys
from ftplib import FTP, error_perm
import os
import ftputil


def upload_dirs_recursive(ftp, path):
    """
    upload file & folders by recursive function
    Args:
        ftp: ftp object
        path: the dir path to fetch all files and folders
    """
    for name in os.listdir(path):
        local_path = os.path.join(path, name)
        if os.path.isfile(local_path):
            file_list = ftp.nlst()
            if not any(name in files and os.path.getsize(local_path) == ftp.size(files) for files in file_list):
                # print("STOR", name, local_path)
                ftp.storbinary('STOR ' + name, open(local_path, 'rb'))
                print(f"{name} in {path} is uploaded.")
        elif os.path.isdir(local_path):
            # print("MKD", name)
            try:
                ftp.mkd(name)
            # ignore "directory already exists"
            except error_perm as e:
                if not e.args[0].startswith('550'):
                    raise
            # print("CWD", name)
            ftp.cwd(name)
            upload_dirs_recursive(ftp, local_path)
            # print("CWD", "..")
            ftp.cwd("..")


def upload_dirs(ftp_ip, ftp_account, ftp_password, local_path, remote_path):
    """
    Init FTP object and upload folders / files to server
    Args:
        ftp_ip: ip for the ftp server
        ftp_account: the account to log in to ftp server
        ftp_password: the password for the log in account
        local_path: the local folder to upload
        remote_path: the path to upload files
    """
    ftp = FTP(ftp_ip)
    ftp.login(ftp_account, ftp_password)
    try:
        ftp.cwd(remote_path)
    except error_perm:
        ftp.mkd(remote_path)
        ftp.cwd(remote_path)
    upload_dirs_recursive(ftp, local_path)

    ftp.close()


def upload_file(ftp_ip, ftp_account, ftp_password, local_file_path, remote_directory):
    """
    upload the specific file to ftp server with the given path
    Args:
        ftp_ip: ip for the ftp server
        ftp_account: the account to log in to ftp server
        ftp_password: the password for the log in account
        local_file_path: the file path on local site
        remote_directory: the folder to upload file
    """
    ftp = FTP(ftp_ip)
    ftp.login(ftp_account, ftp_password)
    ftp.cwd(remote_directory)
    name = os.path.basename(local_file_path)
    ftp.storbinary('STOR ' + name, open(local_file_path, 'rb'))


def download_file(ftp_ip, ftp_account, ftp_password, remote_file_path, local_file_path):
    """
    Download the specific file from ftp server to the given path
    Args:
        ftp_ip: ip for the ftp server
        ftp_account: the account to log in to ftp server
        ftp_password: the password for the log in account
        remote_file_path: the file path on FTP server
        local_file_path: the local file path to store the downloaded file
    """
    ftp = FTP(ftp_ip)
    ftp.login(ftp_account, ftp_password)
    # buffer_size = 1024
    fp = open(local_file_path, 'w')
    ftp.retrlines('RETR ' + remote_file_path, fp.write)
    fp.close()


def download_dirs(ftp_ip, ftp_account, ftp_password, remote_directory, local_file_path):
    ftp = ftputil.FTPHost(ftp_ip, ftp_account, ftp_password)
    remote_directory += "/"
    ftp.chdir(remote_directory)
    print(remote_directory)
    for item in ftp.listdir(remote_directory):
        print(item)
        if ftp.path.isdir(os.path.join(remote_directory, item)):
            os.makedirs(os.path.join(local_file_path, item), exist_ok=True)
            download_dirs(ftp_ip, ftp_account, ftp_password,
                          os.path.join(remote_directory, item), os.path.join(local_file_path, item) + os.sep)
            ftp.chdir(remote_directory)
        elif ftp.path.isfile(os.path.join(remote_directory, item)):
            ftp.download(os.path.join(remote_directory, item), os.path.join(local_file_path, item))


if __name__ == '__main__':
    # download_file('/test_package_list.json', 'test_package_list.json')
    # upload_file(r"test_package_list.json", '.')
    pass

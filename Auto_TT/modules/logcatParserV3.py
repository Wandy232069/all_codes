import gzip
import os
import re

processArray = [
    # use lower cases
    "deprecated",
    "catch exception",
    "must override",
    "illegalargument",
    "illegalstate",
    "never happen",
]


def is_md_related(path):
    """
    to read file content and return if the file have specific text in it
    Args:
        path: path of file to read

    Returns: boolean

    """
    try:
        with open(path, "r") as file:
            file_content = file.read()
    except UnicodeDecodeError:
        print("Failed to decode: " + path)
        return False
    package_prefix = ["com.mobiledrivetech", "com.stellantis"]
    if any(re.search(pattern, file_content) for pattern in package_prefix):
        return True
    else:
        return False


# input file name
def parse_logcat_file(filename, time):
    """
    to parse logcat data and create a report in output folder
    Args:
        filename: logcat file path
        time: the log time, will be use in folder combination
    """
    print("logcat:: " + filename)
    file_buff = ""
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
    # generate the summary text
    for j in range(len(lines)):
        line = lines[j]
        for i in range(len(processArray)):
            if processArray[i] in line.lower():
                file_buff = (
                        file_buff + "[" + processArray[i] + ": " + str(j) + "] " + line
                )
    # write down the output report
    print("file_buff:")
    print(file_buff)
    output_folder = os.path.dirname(os.path.dirname(filename)) + os.sep + "outputFolder" + os.sep
    os.makedirs(output_folder + time, exist_ok=True)
    with open(output_folder + time + os.sep + "outputLogcatLog.txt", "w") as fo:
        fo.write(file_buff)


def parse_br_files(br_folder, time):
    """
    to parse data in bugreport folder and create a report in output folder
    Args:
        br_folder: the bugreport folder
        time: the log time, will be use in folder combination
    """
    # anr part
    anr_crash_body = ""
    md_anr_body = ""
    anr_count = 0
    md_anr_count = 0
    output_folder = os.path.dirname(os.path.dirname(br_folder)) + os.sep + "outputFolder" + os.sep
    print("BR folder :" + output_folder)
    os.makedirs(output_folder + time, exist_ok=True)
    anr = br_folder + os.sep + "anr"
    # check if the folder is exists, somtimes the folder had not created in device
    if os.path.exists(anr):
        for filename in os.listdir(anr):
            anr_count += 1
            filepath = anr + os.sep + filename
            # count the files and append the filename in text
            if filename.startswith("anr_"):
                anr_crash_body += "  = [ anr ] = " + filepath + "\n"
            if is_md_related(filepath):
                md_anr_count += 1
                md_anr_body += filepath + '\n'

    # dropbox part
    dropbox = br_folder + os.sep + "dropbox"
    app_count = 0
    md_app_count = 0
    server_count = 0
    dropbox_crash_body = ""
    md_dropbox_body = ""

    # check if the folder is exists, somtimes the folder had not created in device
    if os.path.exists(dropbox):
        # unzip and remove .gz files
        for file in os.listdir(dropbox):
            filename = dropbox + os.sep + file
            if file.endswith(".gz"):
                with gzip.open(filename, 'rb') as f:
                    file_content = f.read()
                    f.close()
                with open(filename[:-3], 'wb') as w:
                    w.write(file_content)
                    w.close()
                os.remove(filename)
        # count the files and append the filename in text
        for filename in os.listdir(dropbox):
            filepath = dropbox + os.sep + filename
            if any(keyword in filename for keyword in ["crash", "anr"]):
                if filename.startswith("system_app"):
                    if "anr" in filename:
                        anr_crash_body += "  = [ anr ] = " + filepath + "\n"
                        if is_md_related(filepath):
                            md_anr_count += 1
                            anr_count += 1
                            md_anr_body += filepath + '\n'
                    else:
                        if is_md_related(filepath):
                            md_app_count += 1
                            md_dropbox_body += filepath + "\n"
                        app_count += 1
                        dropbox_crash_body += "  = [system_app] = " + filepath + "\n"
                        try:
                            with open(filepath, "r") as f:
                                for i, line in enumerate(f):
                                    if i == 4:
                                        dropbox_crash_body = (
                                                dropbox_crash_body + line[0:-1] + "           @" + filename + "\n"
                                        )
                                        break
                        except UnicodeDecodeError:
                            print("Failed to decode: " + filename)

                if filename.startswith("system_server"):
                    dropbox_crash_body += '  = [system_server] = ' + filepath + '\n'
                    server_count += 1

    # tombstone part
    tombstones_dir = br_folder + os.sep + "tombstones"
    tombstone_count = 0
    md_tombstone_count = 0
    tombstone_body = ""
    md_tombstone_body = ""

    # check if the folder is exists, somtimes the folder had not created in device
    if os.path.exists(tombstones_dir):
        for filename in os.listdir(tombstones_dir):
            filepath = tombstones_dir + os.sep + filename
            if not filename.endswith(".pb"):
                tombstone_body += filepath + "\n"
                tombstone_count += 1
                try:
                    with open(filepath, "r") as f:
                        for i, line in enumerate(f):
                            if i == 6:
                                tombstone_body = (
                                        tombstone_body + line[9:-1] + "           @" + filename + "\n"
                                )
                                break
                except UnicodeDecodeError:
                    print("Failed to decode: " + filename)
                if is_md_related(filepath):
                    md_tombstone_count += 1
                    md_dropbox_body += filepath + "\n"

    # write the text contain to Crashreport.txt
    with open(output_folder + time + os.sep + "CrashReport.txt", "w") as fo:
        fo.writelines("[[[********  ANR Session  ********]]]\n")
        fo.writelines("There are {} ANR crashes in logs\n".format(anr_count))
        fo.writelines(anr_crash_body)
        fo.writelines("There are {} MD's ANR crashes in logs\n".format(md_anr_count))
        fo.writelines(md_anr_body)
    with open(output_folder + time + os.sep + "CrashReport.txt", "a") as fo:
        fo.writelines("\n\n[[[********  Dropbox Session  ********]]]\n")
        fo.writelines("There are {} system_app crashes in logs\n".format(app_count))
        fo.writelines(
            "There are {} system_server crashes in logs\n".format(server_count)
        )
        fo.writelines(dropbox_crash_body)
        fo.writelines("There are {} MD's app crashes in logs\n".format(md_app_count))
        fo.writelines(md_dropbox_body)
    with open(output_folder + time + os.sep + "CrashReport.txt", "a") as fo:
        fo.writelines("\n\n[[[********  Tombstones Session  ********]]]\n")
        fo.writelines("There are {} tombstones crashes in logs\n".format(tombstone_count))
        fo.writelines(tombstone_body)
        fo.writelines("There are {} MD's tombstones crashes in logs\n".format(md_tombstone_count))
        fo.writelines(md_tombstone_body)

    print(anr_crash_body)
    print(dropbox_crash_body)
    print(tombstone_body)


if __name__ == "__main__":
    parse_br_files(
        r"\\MD-TEST\Projects\SAW\Monkey_log\2024_01_31_8_packages\bugreport\BR_2024_01_31-04_20_32",
        "2024_01_31-04_20_32")

import os
import time


def combine_log(path=os.getcwd()):
    """
    To combine all text file under the given folder to test_summary.txt
    Args:
        path: the folder where all text files saved
    """
    data = list()
    for log_file in os.listdir(path):
        print(log_file)
        # Read text files in the given folder and append to the data
        if log_file.endswith(".txt") and log_file != "test_summary.txt":
            with open(path + log_file, mode="r") as file:
                data.append(f"{log_file}\n")
                data.append(file.readlines())
                data.append("\n")
    # Write down the data to test_summary.txt
    with open(path + "test_summary.txt", mode="w") as file:
        today = time.strftime("%Y_%m_%d", time.localtime())
        file.writelines(f"Date : {today}\n")
        for lines in data:
            file.writelines(lines)


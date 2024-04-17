import json
import os
import re
import subprocess
import sys
from tkinter import scrolledtext
from tkinter import *
import tkinter as tk
from tkinter import ttk


def modify_eol_to_linux(filename):
    windows_line_end = b'\r\n'
    unix_line_end = b'\n'

    # relative or absolute file path, e.g.:
    with open(filename, 'rb') as open_file:
        content = open_file.read()
    # Windows ➡ Unix
    content = content.replace(windows_line_end, unix_line_end)

    with open(filename, 'wb') as open_file:
        open_file.write(content)


def get_devices():
    devices_output = os.popen('adb devices').readlines()
    devices = []
    if len(devices_output) != 1:
        for device in devices_output:
            print(device)
            if "\tdevice\n" in device:
                devices.append(re.sub("\tdevice\n", "", device))
    return devices


class UIPage:
    main_page = tk.Tk()
    main_page.title("Base_TT")
    adb_command = ["adb"]

    text_output = scrolledtext.ScrolledText(main_page, height=8)
    text_output.grid(column=0, row=1, columnspan=3, padx=5,
                     pady=5, sticky=S + E + W)

    tab_control = ttk.Notebook(main_page)

    # Add Tabs
    tab_system = ttk.Frame(tab_control)

    tab_control.add(tab_system, text='System')

    tab_control.grid(row=0, column=0, sticky=W)
    monitor_frame = tk.LabelFrame(tab_system, text='CPU / Memory / Storage / logcat',
                                  padx=5, pady=5)
    monitor_frame.grid(column=2, row=0, columnspan=2,
                       rowspan=5, ipadx=5, ipady=5, sticky=tk.N)
    Label(monitor_frame, text="CPU_Interval").grid(
        column=0, row=0, padx=5, pady=5, sticky=W + E)
    value_cpu_interval_minute = tk.StringVar()
    # value_cpu_interval_minute.set(f"{CPU_MONITOR_INTERVAL_MINUTE}")
    cpu_interval_minute = ttk.Entry(
        monitor_frame, textvariable=value_cpu_interval_minute, width=10)
    cpu_interval_minute.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)

    Label(monitor_frame, text="CPU_Loop").grid(
        column=0, row=1, padx=5, pady=5, sticky=W + E)
    value_cpu_loop_count = tk.StringVar()
    # value_cpu_loop_count.set(f"{CPU_MONITOR_LOOP_TIMES}")
    cpu_loop_count = ttk.Entry(
        monitor_frame, textvariable=value_cpu_loop_count, width=10)
    cpu_loop_count.grid(column=1, row=1, padx=5, pady=5, sticky=W)

    Label(monitor_frame, text="Memory_Interval").grid(
        column=0, row=2, padx=5, pady=5, sticky=W + E)
    value_mem_interval_minute = tk.StringVar()
    # value_mem_interval_minute.set(f"{MEM_MONITOR_INTERVAL_MINUTE}")
    mem_interval_minute = ttk.Entry(
        monitor_frame, textvariable=value_mem_interval_minute, width=10)
    mem_interval_minute.grid(column=1, row=2, padx=5, pady=5, sticky=W)

    Label(monitor_frame, text="Memory_Loop").grid(
        column=0, row=3, padx=5, pady=5, sticky=W + E)
    value_mem_loop_count = tk.StringVar()
    # value_mem_loop_count.set(f"{MEM_MONITOR_LOOP_TIMES}")
    mem_loop_count = ttk.Entry(
        monitor_frame, textvariable=value_mem_loop_count, width=10)
    mem_loop_count.grid(column=1, row=3, padx=5, pady=5, sticky=tk.W)

    Label(monitor_frame, text="Disk_Interval").grid(
        column=0, row=4, padx=5, pady=5, sticky=W + E)
    value_disk_interval_minute = tk.StringVar()
    # value_disk_interval_minute.set(f"{DISK_MONITOR_INTERVAL_MINUTE}")
    disk_interval_minute = ttk.Entry(
        monitor_frame, textvariable=value_disk_interval_minute, width=10)
    disk_interval_minute.grid(column=1, row=4, padx=5, pady=5, sticky=tk.W)

    Label(monitor_frame, text="Disk_Loop").grid(
        column=0, row=5, padx=5, pady=5, sticky=W + E)
    value_disk_loop_count = tk.StringVar()
    # value_disk_loop_count.set(f"{DISK_MONITOR_LOOP_TIMES}")
    disk_loop_count = ttk.Entry(
        monitor_frame, textvariable=value_disk_loop_count, width=10)
    disk_loop_count.grid(column=1, row=5, padx=5, pady=5, sticky=tk.W)

    start_log_btn = Button(monitor_frame, text='Start')
    start_log_btn.grid(column=0, row=10, padx=5, pady=5,
                       rowspan=2, sticky=tk.E + tk.W)

    stop_log_btn = Button(monitor_frame, text='End')
    stop_log_btn.grid(column=1, row=10, padx=5, pady=5, rowspan=2, sticky=tk.E + tk.W)

    device_selector = ttk.Combobox(main_page, width=17)
    device_selector.grid(column=2, row=0, sticky=tk.E + tk.N)
    tab_packages = ttk.Frame(tab_control)
    packages1 = {}
    packages2 = {}
    is_check_packages1 = {}
    is_check_packages2 = {}
    all_packages_button = []
    check_all_btn = Button(tab_packages, text='Check All')
    uncheck_all_btn = Button(tab_packages, text='Uncheck All')
    package_frame = tk.LabelFrame(
        tab_packages, text='Packages_1', padx=5, pady=5)
    package2_frame = tk.LabelFrame(tab_packages, text='Packages_2',
                                   padx=5, pady=5)

    def __init__(self):
        # self.main_page.geometry("1150x660")

        device_selector = self.device_selector
        devices = get_devices()
        try:
            for device in devices:
                device_selector['values'] = (*device_selector['values'], device)
            device_selector.bind('<<ComboboxSelected>>', self.dev_changed)
            device_selector.current(0)
        except tk.TclError:
            print("No device detected")
        self.dev_changed(Event)

        self.start_log_btn.configure(command=self.start_log)
        self.stop_log_btn.configure(command=self.stop_log)

    def init_packages_tab(self, packages_list, test_packages_list):
        package_frame = self.package_frame
        package2_frame = self.package2_frame
        packages1_count = int(len(packages_list) / 2)
        tab_control = self.tab_control
        tab_packages = self.tab_packages
        tab_control.add(tab_packages, text='Packages')

        package_frame.grid(column=0, row=0, ipadx=5,
                           ipady=5, padx=5, pady=5, sticky=tk.N)

        packages1 = self.packages1
        for i in range(packages1_count):
            packages1[i] = packages_list[i]

        is_check_packages1 = self.is_check_packages1
        is_check_packages2 = self.is_check_packages2

        all_packages_button = self.all_packages_button
        for i in range(len(packages1)):
            is_check_packages1[i] = tk.BooleanVar()
            check_btn = tk.Checkbutton(
                package_frame, text=packages1[i], variable=is_check_packages1[i], anchor=W)
            all_packages_button.append(check_btn)
            if packages1[i] in test_packages_list:
                check_btn.select()
            check_btn.grid(row=i + 1, sticky=E + W)

        package2_row = len(packages_list) - packages1_count

        package2_frame.grid(column=1, row=0,
                            ipadx=5, ipady=5, padx=5, pady=5, sticky=tk.N)

        packages2 = self.packages2
        for i in range(package2_row):
            packages2[i] = packages_list[i + packages1_count]

        for i in range(len(packages2)):
            is_check_packages2[i] = tk.BooleanVar()
            check_btn = tk.Checkbutton(
                package2_frame, text=packages2[i], variable=is_check_packages2[i], anchor=W)
            all_packages_button.append(check_btn)
            if packages2[i] in test_packages_list:
                check_btn.select()
            check_btn.grid(row=i + 1, columnspan=2, sticky=W + E)
        self.check_all_btn.configure(command=self.check_all)
        self.check_all_btn.grid(column=0, row=packages1_count + 1, padx=5, pady=5, sticky=tk.E + tk.W)
        self.uncheck_all_btn.configure(command=self.uncheck_all)
        self.uncheck_all_btn.grid(column=1, row=packages1_count + 1, padx=5, pady=5, sticky=tk.E + tk.W)

    def start(self):
        self.main_page.mainloop()

    def quit(self):
        self.main_page.quit()

    def change_device(self, device_sn):
        if device_sn != "":
            self.adb_command = ["adb", "-s", device_sn]
        else:
            self.adb_command = ["adb"]

    def start_log(self):
        self.create_log_folder_at_local()
        self.create_log_folder_on_device()
        print("start monitoring")
        pass

    def stop_log(self):
        print("stop monitoring")
        pass

    def create_log_folder_at_local(self):
        pass

    def create_log_folder_on_device(self):
        pass

    def wait_device(self):
        subprocess.call(self.adb_command + ["wait-for-device"])

    def reboot_device(self):
        subprocess.call(self.adb_command + ["reboot"])

    def dev_changed(self, event):
        device_id = self.device_selector.get()
        self.change_device(device_id)

    def push_file(self, file, location):
        subprocess.call(self.adb_command + ["push", file, location])

    def pull_file(self, file, location):
        subprocess.call(self.adb_command + ["pull", file, location])

    def remove_file(self, file):
        subprocess.call(self.adb_command + ["shell", "rm", "-rf", file])

    def check_all(self):
        for check_button in self.all_packages_button:
            check_button.select()

    def uncheck_all(self):
        for check_button in self.all_packages_button:
            check_button.deselect()

    def input_text(self, text):
        self.text_output.delete('1.0', END)
        self.text_output.insert(END, text)

    def update_test_packages(self, file):
        package_list = []
        for i in range(len(self.packages1)):
            if self.is_check_packages1[i].get():
                package_list.append(self.packages1[i])
        for j in range(len(self.packages2)):
            if self.is_check_packages2[j].get():
                package_list.append(self.packages2[j])

        json_data = json.dumps(package_list, separators=(',', ':'), indent=2)

        # Write JSON data to a file
        with open(file, 'w') as file:
            file.write(json_data)

    def set_label_text(self, label: tk.Label, text):
        label.configure(text=text)


if __name__ == '__main__':
    UI = UIPage()
    UI.start()

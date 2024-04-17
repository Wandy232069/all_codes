import datetime, sys, subprocess, time, os
import platform, images
import sqlite3
import threading
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, QThread, Qt, QMutex, QPointF, QDateTime, QSortFilterProxyModel, QModelIndex
from PyQt5.QtGui import QPainter, QColor, QStandardItemModel, QPixmap
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtChart import QChart, QValueAxis, QChartView, QSplineSeries, QDateTimeAxis

from main_ui import Ui_Start_Window  # 載入開始視窗ui
from monitor_ui import Ui_MainWindow  # 載入Online Version ui
from off_monitor_ui import Ui_Off_MainWindow  # 載入Offline Version ui
from pid_sub_monitor_dialog_ui import Ui_PID_Dialog  # 載入搜尋PID子視窗ui
from command_sub_monitor_dialog_ui import Ui_COMMAND_Dialog  # 載入搜尋COMMAND子視窗ui

WINDOWS_LOCAL_DIRECTION = r"C:/Monitor_data"  # 存data - Windows作業系統路徑
LINUX_LOCAL_DIRECTION = r"/tmp/Monitor_data"  # 存data - Linux作業系統路徑
LOCAL_DIRECTION = ""

os_name = platform.system()  # 判斷作業系統
if os_name == "Windows":
    LOCAL_DIRECTION = WINDOWS_LOCAL_DIRECTION
elif os_name == "Linux":
    LOCAL_DIRECTION = LINUX_LOCAL_DIRECTION


class StartWindow(QtWidgets.QMainWindow):  # 開始視窗
    def __init__(self):
        super().__init__()
        self.ui = Ui_Start_Window()
        self.ui.setupUi(self)
        self.device_group = QtWidgets.QButtonGroup(self)  # Radio按鈕群組 - devices
        self.device_group.addButton(self.ui.rtbm)  # 加入單選按鈕 - RTBM
        self.device_group.addButton(self.ui.aosp)  # 加入單選按鈕 - AOSP
        self.device_group.addButton(self.ui.vera)  # 加入單選按鈕 - Vera
        self.version_group = QtWidgets.QButtonGroup(self)  # Radio按鈕群組 - Version
        self.version_group.addButton(self.ui.online)  # 加入單選按鈕 - Online
        self.version_group.addButton(self.ui.offline)  # 加入單選按鈕 - Offline
        self.ui.open_btn.clicked.connect(self.open_monitor_window)  # 定義OPEN按鈕觸發事件
        self.second_window = None  # 第二視窗需先定義，否則會無法keep，第二視窗會快速關閉

        if not os.path.exists(f'{LOCAL_DIRECTION}/Online'):  # 判斷此路徑是否存在
            os.makedirs(f'{LOCAL_DIRECTION}/Online', mode=0o777)  # 不存在就建立，mode=0o777表示指定目錄的權限設置
        if not os.path.exists(f'{LOCAL_DIRECTION}/Offline'):
            os.makedirs(f'{LOCAL_DIRECTION}/Offline', mode=0o777)
        if not os.path.exists(f'{LOCAL_DIRECTION}/Offline/disk'):
            os.makedirs(f'{LOCAL_DIRECTION}/Offline/disk', mode=0o777)

    def open_monitor_window(self):
        device = ""
        version = ""
        if self.device_group.checkedButton() is not None:  # 判斷是否有點選device
            device = self.device_group.checkedButton().objectName()  # 得到選取device的值
        if self.version_group.checkedButton() is not None:  # 判斷是否有點選version
            version = self.version_group.checkedButton().objectName()  # 得到選取version的值
        if device == "" or version == "":  # 只要device或version其中一個沒有選擇
            dialog_notification(self, "no checked")  # 顯示提醒視窗
        else:  # device與version都有選擇
            self.close()  # 關閉「開始視窗」
            if version == "online":
                self.second_window = MainWindow_controller(device)  # Online版本視窗
                time.sleep(2)
                self.second_window.show()
            elif version == "offline":
                self.second_window = Off_Window_controller(device)  # Offline版本視窗
                time.sleep(2)
                self.second_window.show()


class Off_Window_controller(QtWidgets.QMainWindow):  # Offline Version視窗
    def __init__(self, device):
        super().__init__()
        self.proxy = None
        self.loops_times = None
        self.start_disk_thread = None
        self.start_top_thread = None
        self.loop_count = None
        self.csv_name = None
        self.txt_name = None
        self.path = None
        self.ui = Ui_Off_MainWindow()
        self.ui.setupUi(self)  # 套用Ui介面
        # =============================Total Used 的Table
        self.ui.tableWidget.setColumnWidth(0, 150)  # 設定Time Stamp欄位寬度
        self.ui.tableWidget.setColumnWidth(1, 90)  # 設定CPU欄位寬度
        self.ui.tableWidget.setColumnWidth(2, 90)  # 設定MEM欄位寬度
        self.ui.tableWidget.setColumnWidth(3, 90)  # 設定DISK欄位寬度
        # =============================Row Data 的Table
        self.model = QStandardItemModel(0, 7)  # 建立model以便搜尋功能
        self.model.setHorizontalHeaderLabels(
            ['Time Stamp', 'PID', 'USER', 'COMMAND', 'CPU(%)', 'MEM(%)', 'TIME+'])  # TableView欄位名稱
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.setColumnWidth(0, 180)  # 設定Time Stamp欄位寬度
        self.ui.tableView.setColumnWidth(1, 100)  # 設定PID欄位寬度
        self.ui.tableView.setColumnWidth(2, 100)  # 設定USER欄位寬度
        self.ui.tableView.setColumnWidth(3, 280)  # 設定COMMAND欄位寬度
        self.ui.tableView.setColumnWidth(4, 90)  # 設定CPU欄位寬度
        self.ui.tableView.setColumnWidth(5, 90)  # 設定MEM欄位寬度
        self.ui.tableView.setColumnWidth(6, 120)  # 設定Time+欄位寬度
        self.ui.tableView.setSortingEnabled(True)  # 開啟按表頭排序功能

        if os_name == "Linux":  # 如果是Linux，Start按鈕的文字大小要縮小
            font = QtGui.QFont()
            font.setPointSize(18)
            self.ui.start_btn.setFont(font)
        self.ui.load_btn.setIconSize(QtCore.QSize(20, 20))  # 設定按鈕的圖片大小
        self.ui.load_btn.setIcon(QtGui.QIcon(':/load.png'))  # 設定按鈕的圖片
        self.ui.stop_btn.setEnabled(False)  # 將Stop按鈕disable
        self.ui.start_btn.clicked.connect(lambda: self.start(device))  # 定義Start按鈕觸發事件
        self.ui.stop_btn.clicked.connect(lambda: self.stop())  # 定義Stop按鈕觸發事件
        self.ui.load_btn.clicked.connect(lambda: self.getfile(device))  # 定義load按鈕觸發事件
        self.flash_time = self.ui.interval_edit.toPlainText()  # 取得interval的值

        self.plot_qchart = QChartViewPlot(int(self.flash_time))  # 建立CPU折線圖
        self.plot_qchart.setTitle("CPU 使用率")
        self.plot_qchart.axis_y.setTitleText("CPU")
        if device == "aosp":
            self.plot_qchart.axis_y.setRange(0, 800)  # 設定y軸的範圍
        elif device == "rtbm":
            self.plot_qchart.axis_y.setRange(0, 200)  # 設定y軸的範圍
        elif device == "vera":
            self.plot_qchart.axis_y.setRange(0, 500)  # 設定y軸的範圍
        self.ui.plot_view.setChart(self.plot_qchart)
        self.ui.plot_view.setRenderHint(QPainter.Antialiasing)  # 抗鋸齒
        self.ui.plot_view.setRubberBand(QChartView.RectangleRubberBand)

        self.plot_qchart1 = QChartViewPlot(int(self.flash_time))  # 建立MEM折線圖
        self.plot_qchart1.setTitle("Memory 使用率")
        self.plot_qchart1.series.setColor(QColor(0, 153, 76))  # 設定折線的顏色
        self.plot_qchart1.axis_y.setTitleText("MEM")
        self.ui.plot_view1.setChart(self.plot_qchart1)
        self.ui.plot_view1.setRenderHint(QPainter.Antialiasing)  # 抗鋸齒
        self.ui.plot_view1.setRubberBand(QChartView.RectangleRubberBand)

        self.plot_qchart2 = QChartViewPlot(int(self.flash_time))  # 建立DISK折線圖
        self.plot_qchart2.setTitle("Disk 使用率")
        self.plot_qchart2.series.setColor(QColor(238, 118, 33))  # 設定折線的顏色
        self.plot_qchart2.axis_y.setTitleText("Disk")
        self.ui.plot_view2.setChart(self.plot_qchart2)
        self.ui.plot_view2.setRenderHint(QPainter.Antialiasing)  # 抗鋸齒
        self.ui.plot_view2.setRubberBand(QChartView.RectangleRubberBand)

        self.model = self.ui.tableView.model()
        self.local_path = LOCAL_DIRECTION + r'/Offline/'  # 將top資料拉回本機存放的路徑
        self.local_path_disk = LOCAL_DIRECTION + r'/Offline/disk/'  # 將disk資料拉回本機存放的路徑

    def start(self, device):  # 「Start」按鈕觸發事件
        try:
            if not isConnectingDevice():  # 判斷是否有連接設備
                dialog_notification(self, 'no connect devices')
            else:
                interval = self.ui.interval_edit.toPlainText()  # interval的值 (幾秒更新一次)
                loop = self.ui.loop_edit.toPlainText()  # loop的值 (更新幾次)
                if interval.isdigit() and loop.isdigit():  # 判斷是否都是數字
                    self.path = "/data/local/tmp/qa/offline/"  # 設備上要存放data的路徑
                    subprocess.call(['adb', 'shell', 'mkdir', '-p', self.path])  # 設備上建立路徑
                    subprocess.call(['adb', 'shell', 'chmod', '+x', self.path])  # 修改路徑權限

                    time_stamp = datetime.datetime.now()
                    print(time_stamp)
                    self.txt_name = "monitor_{}.txt".format(time_stamp.strftime("%Y%m%d%H%M%S"))  # 存top指令輸出的txt檔案名稱
                    self.csv_name = "disk_{}.txt".format(time_stamp.strftime("%Y%m%d%H%M%S"))  # 存disk的txt檔案名稱

                    self.start_top_thread = off_top_Thread(interval, loop, self.path, self.txt_name, device)  # top指令的執行緒
                    self.start_top_thread.start()
                    self.start_disk_thread = off_disk_Thread(interval, loop, self.path, self.csv_name, device)  # disk shell的執行緒
                    self.start_disk_thread.start()

                    self.loop_count = 1
                    self.loops_times = WorkerThread(int(interval))  # 預計次數的執行緒
                    self.loops_times.data_ready.connect(lambda: self.Expected_loop_time(loop))  # 預計次數計算function
                    self.loops_times.start()

                    self.ui.start_btn.setEnabled(False)
                    self.ui.stop_btn.setEnabled(True)
                else:
                    dialog_notification(self, "digit")
        except Exception as e:
            print(e)

    def Expected_loop_time(self, loop):  # 預計次數計算
        try:
            if self.loop_count <= int(loop):  # 如果次數小於使用者設定的次數
                self.ui.pre_count.setText('{}'.format(self.loop_count))
                if self.loop_count == int(loop):
                    time.sleep(1)
                    self.loops_times.stop()  # 停止執行緒
                    dialog_notification(self, 'can stop')
                self.loop_count += 1
        except Exception as e:
            print(e)

    def stop(self):  # 「Stop」按鈕觸發事件
        try:
            if not isConnectingDevice():  # 判斷是否連接設備
                dialog_notification(self, 'no connect devices')
            else:
                self.loops_times.stop()  # 停止預計次數執行緒
                output = subprocess.check_output(['adb', 'shell', 'ls', self.path])  # 列出路徑上所有的檔案
                file_b = bytes(self.txt_name, 'utf8')  # 將檔名轉乘byte
                if not file_b in output:  # 判斷此檔案是否在設備上
                    dialog_notification(self, 'not the same device')  # 不在設備時提醒使用者
                else:
                    subprocess.Popen(['adb', 'shell', 'pkill', 'top'], stdout=subprocess.PIPE)  # kill top程序
                    subprocess.Popen(['adb', 'pull', self.path + self.txt_name, self.local_path + self.txt_name], stdout=subprocess.PIPE)  # 下載設備上的檔案到本機端
                    subprocess.Popen(['adb', 'pull', self.path + self.csv_name, self.local_path_disk + self.csv_name], stdout=subprocess.PIPE)  # 下載設備上的檔案到本機端
                    subprocess.call(['adb', 'root'])  # 切換為root
                    subprocess.call(['adb', 'shell', 'rm', '-f', self.path + '*'])  # 移除設備上的檔案
                    self.ui.start_btn.setEnabled(True)
                    self.ui.stop_btn.setEnabled(False)
        except Exception as e:
            print(e)

    def getfile(self, device):  # 讀取取回的檔案
        try:
            all_data = []
            filePath, filterType = QFileDialog.getOpenFileName(self, 'Open file', self.local_path, 'Text files (*.txt)')  # 開啟選擇檔案視窗
            if filePath != '':
                file_split = filePath.split('/')
                if file_split[-3] != 'Monitor_data' or file_split[-2] != 'Offline' or not file_split[-1].startswith('monitor'):  # 如果路徑與檔案名稱不符
                    dialog_notification(self, 'incorrect file')  # 提醒視窗
                else:
                    file_time = file_split[-1].replace('.txt', '').replace('monitor_', '')  # 取檔案名稱的time stamp部分
                    time_list = []
                    disk_list = []
                    with open(f'{self.local_path_disk}disk_{file_time}.txt', 'r') as fp:  # 開啟disk的txt
                        for line in fp.readlines():
                            if line.strip() != '':
                                line_split = line.strip('\n').replace('%', '').replace('\\n', '').split(',')  # 以逗號分隔
                                time_list.append(line_split[0])  # 存時間
                                disk_list.append(int(line_split[1].strip()))  # 存disk使用率
                    with open(filePath, 'r') as f:  # 開啟top輸出的txt
                        self.ui.tableWidget.setRowCount(0)  # 將Total Used頁籤的Table清空
                        self.ui.tableWidget.clearContents()
                        rowcount = self.model.rowCount()
                        self.model.removeRows(0, rowcount, QModelIndex())  # 將Row Data頁籤的Table清空
                        self.save_time_data = []
                        self.save_cpu_data = []
                        self.save_mem_data = []
                        self.save_disk_data = []
                        self.buffer_cpu = []  # 折線圖存CPU每個點
                        self.buffer_mem = []  # 折線圖存MEM每個點
                        self.buffer_disk = []  # 折線圖存DISK每個點
                        count = 0
                        while True:
                            line = f.readline()
                            if not line:
                                break
                            if line.strip('\n') != '':
                                task = handle_top_text(device, 'offline', f, None, line, 'Tasks:')  # 處理每一行
                                all_data = row_data(None, int(task[0]), all_data, f)
                                self.load_data(all_data, time_list, disk_list, count)
                                count += 1

                        self.proxy = QSortFilterProxyModel()  # 建立ProxyModel
                        self.proxy.setSourceModel(self.model)  # 將Tabel modelr加入ProxyModel
                        self.proxy.setFilterKeyColumn(-1)  # 可以搜尋哪一行，-1表示全部都可以
                        self.ui.tableView.setModel(self.proxy)  # 將TableView的model設定為ProxyModel
                        self.ui.textEdit.textChanged.connect(lambda: self.filter(self.ui.textEdit.toPlainText()))  # 當搜尋PID/COMMAND輸入框文字改變，就會觸發filter function

                        threading.Thread(target=self.draw_line_chart).start()  # 畫折線圖的執行緒
        except Exception as e:
            print(e)

    def load_data(self, all_data, time_list, disk_list, i):
        try:
            save_cpu_once = []  # 存每一筆CPU
            save_mem_once = []  # 存每一筆MEM
            self.save_time_data.append(time_list[i])  # 將時間加入self的參數以便畫折線圖
            self.save_disk_data.append(disk_list[i])  # 將DISK加入self的參數以便畫折線圖
            # =======================Row Data=======================
            for d in all_data:
                rowPosition = self.model.rowCount()  # 讀取目前有多少Row
                self.model.insertRow(rowPosition)  # 新增新的Row
                self.model.setData(self.model.index(rowPosition, 0, QModelIndex()), time_list[i], Qt.DisplayRole)  # Time Stamp
                self.model.setData(self.model.index(rowPosition, 1, QModelIndex()), d[0], Qt.DisplayRole)  # PID
                self.model.setData(self.model.index(rowPosition, 2, QModelIndex()), d[1], Qt.DisplayRole)  # USER
                self.model.setData(self.model.index(rowPosition, 3, QModelIndex()), d[11], Qt.DisplayRole)  # COMMAND
                self.model.setData(self.model.index(rowPosition, 4, QModelIndex()), d[8], Qt.DisplayRole)  # CPU
                self.model.setData(self.model.index(rowPosition, 5, QModelIndex()), d[9], Qt.DisplayRole)  # MEM
                self.model.setData(self.model.index(rowPosition, 6, QModelIndex()), d[10], Qt.DisplayRole)  # TIME+
                save_cpu_once.append(float(d[8]))
                save_mem_once.append(float(d[9]))
            total_cpu = sum(save_cpu_once)  # 算出CPU total使用率
            total_mem = sum(save_mem_once)  # 算出MEM total使用率
            self.save_cpu_data.append(total_cpu)  # 將CPU total使用率加入self的參數以便畫折線圖
            self.save_mem_data.append(total_mem)  # 將MEM total使用率加入self的參數以便畫折線圖
            # =======================Total Used=======================
            total_rowPosition = self.ui.tableWidget.rowCount()  # 讀取目前有多少Row
            self.ui.tableWidget.insertRow(total_rowPosition)  # 新增新的Row
            self.ui.tableWidget.setItem(total_rowPosition, 0, QtWidgets.QTableWidgetItem(time_list[i]))  # Time Stamp
            self.ui.tableWidget.setItem(total_rowPosition, 1, QtWidgets.QTableWidgetItem('{:.1f}'.format(total_cpu)))  # CPU
            self.ui.tableWidget.setItem(total_rowPosition, 2, QtWidgets.QTableWidgetItem('{:.1f}'.format(total_mem)))  # MEM
            self.ui.tableWidget.setItem(total_rowPosition, 3, QtWidgets.QTableWidgetItem('{}'.format(disk_list[i])))  # DISK
            self.ui.cpu_high.setText('{:.1f}'.format(max(self.save_cpu_data)))  # 顯示CPU最高值
            self.ui.cpu_low.setText('{:.1f}'.format(min(self.save_cpu_data)))  # 顯示CPU最低值
            self.ui.cpu_avg.setText('{:.1f}'.format(sum(self.save_cpu_data) / len(self.save_cpu_data)))  # 顯示CPU平均值
            self.ui.mem_high.setText('{:.1f}'.format(max(self.save_mem_data)))  # 顯示MEM最高值
            self.ui.mem_low.setText('{:.1f}'.format(min(self.save_mem_data)))  # 顯示MEM最低值
            self.ui.mem_avg.setText('{:.1f}'.format(sum(self.save_mem_data) / len(self.save_mem_data)))  # 顯示MEM平均值
            print('data time stamp:', time_list[i])
        except Exception as e:
            print(e)

    def draw_line_chart(self):
        try:
            if len(self.save_time_data) != 0 and len(self.save_cpu_data) != 0 and len(self.save_mem_data) != 0:
                for i in range(len(self.save_time_data)):
                    myPythonicDate = self.save_time_data[i]
                    qtDateTime = QtCore.QDateTime.fromString(myPythonicDate, 'yyyy-MM-dd hh:mm:ss')  # 將時間轉成QDateTime格式
                    self.buffer_cpu.append(QPointF(qtDateTime.toMSecsSinceEpoch(), self.save_cpu_data[i]))  # 新增CPU點
                    self.buffer_mem.append(QPointF(qtDateTime.toMSecsSinceEpoch(), self.save_mem_data[i]))  # 新增MEM點
                    self.buffer_disk.append(QPointF(qtDateTime.toMSecsSinceEpoch(), self.save_disk_data[i]))  # 新增DISK點
                first_qtDateTime = QtCore.QDateTime.fromString(self.save_time_data[0], 'yyyy-MM-dd hh:mm:ss')  # 第一筆的時間
                last_qtDateTime = QtCore.QDateTime.fromString(self.save_time_data[-1], 'yyyy-MM-dd hh:mm:ss')  # 最後一筆的時間

                self.plot_qchart.axis_x.setRange(first_qtDateTime, last_qtDateTime)  # 設定CPU折線圖x軸的範圍
                self.plot_qchart.axis_x.setTickCount(len(self.save_time_data))  # 設定CPU折線圖x軸顯示的數量
                self.plot_qchart.series.replace(self.buffer_cpu)

                self.plot_qchart1.axis_x.setRange(first_qtDateTime, last_qtDateTime)  # 設定MEM折線圖x軸的範圍
                self.plot_qchart1.axis_x.setTickCount(len(self.save_time_data))  # 設定MEM折線圖x軸顯示的數量
                self.plot_qchart1.series.replace(self.buffer_mem)

                self.plot_qchart2.axis_x.setRange(first_qtDateTime, last_qtDateTime)  # 設定DISK折線圖x軸的範圍
                self.plot_qchart2.axis_x.setTickCount(len(self.save_time_data))  # 設定DISK折線圖x軸顯示的數量
                self.plot_qchart2.series.replace(self.buffer_disk)
        except Exception as e:
            print(e)

    def filter(self, filter_text):  # Row Data頁籤搜尋用
        self.proxy.setFilterFixedString(filter_text)

    def closeEvent(self, event):  # 視窗關閉觸發事件
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            if isConnectingDevice():
                subprocess.Popen(['adb', 'shell', 'pkill', 'top'], stdout=subprocess.PIPE)  # 結束top命令
            sys.exit()  # 終止所有執行緒
        else:
            event.ignore()

class MainWindow_controller(QtWidgets.QMainWindow):  # Online Version 視窗
    def __init__(self, device):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # 套用Ui
        self.dialog_group = []  # 存子視窗
        self.flash_time = '3'  # 預設更新時間
        self.sorted = '+%CPU'  # 預設以CPU排序
        self.device = device
        self.worker_thread = None
        self.main_worker_thread = None
        self.con = None
        self.menu = None
        self.ui.tableWidget.setColumnWidth(0, 60)  # 設定PID欄位寬度
        self.ui.tableWidget.setColumnWidth(1, 80)  # 設定USER欄位寬度
        self.ui.tableWidget.setColumnWidth(2, 130)  # 設定COMMAND欄位寬度
        self.ui.tableWidget.setColumnWidth(3, 80)  # 設定CPU欄位寬度
        self.ui.tableWidget.setColumnWidth(4, 80)  # 設定MEM欄位寬度
        self.ui.tableWidget.setColumnWidth(5, 120)  # 設定TIME+欄位寬度
        self.ui.flush_btn.setIcon(QtGui.QIcon(':/cycle.png'))  # 設定更新按鈕的圖片
        self.ui.flush_btn.setIconSize(QtCore.QSize(20, 20))
        self.ui.return_btn.setVisible(False)  # 隱藏Return to Menu按鈕
        self.close_or_not = True  # 因應Return to Menu功能
        self.ui.progressBar.setVisible(False)  # 隱藏進度條

        try:
            if isConnectingDevice():
                if self.device == "rtbm":
                    self.main_worker_thread = Main_WorkerThread(
                        command=['adb', 'shell', 'export', 'TERM=xterm', '&&', 'top', '-b', '-o', '+%CPU', '-d', self.flash_time], device=self.device, win=self)
                    self.main_worker_thread.start()
                elif self.device == "vera" or self.device == "aosp":
                    self.main_worker_thread = Main_WorkerThread(
                        command=['adb', 'shell', 'top', '-b', '-d', self.flash_time], device=self.device, win=self)
                    self.main_worker_thread.start()

                self.ui.pushButton.clicked.connect(lambda: self.open_PID_Window(self.device))  # 定義PID查詢按鈕觸發事件
                self.ui.pushButton_2.clicked.connect(lambda: self.open_COMMAND_Window(self.device))  # 定義COMMAND查詢按鈕觸發事件
                self.ui.flush_btn.clicked.connect(lambda: self.change_reflash_time(self.device))  # 定義更新時間按鈕觸發事件
                self.ui.tableWidget.horizontalHeader().sectionClicked.connect(self.headerClicked)  # 定義點擊表頭觸發事件
                self.ui.stop_btn.clicked.connect(lambda: self.stop_and_download())  # 定義Stop and download按鈕觸發事件
                self.ui.return_btn.clicked.connect(lambda: self.return_to_menu())  # 定義Return to menu按鈕觸發事件
                self.save_time_data = []
                self.save_cpu_data = []
                self.save_mem_data = []
                self.buffer_cpu = []
                self.buffer_mem = []
                self.buffer_disk = []

                if os.path.exists("row_data.db"):  # 判斷sqlite資料庫是否存在
                    os.remove("row_data.db")  # 有就刪除，只存單次監控的Row data
                self.con = sqlite3.connect("row_data.db")  # 連線db，沒有會自動建立
                cur = self.con.cursor()
                cur.execute("CREATE TABLE row_data(Time_stamp, PID, USER, COMMAND, CPU, MEM, TIME)")  # 建立Table
                self.con.commit()
                self.con.close()

                self.plot_qchart = QChartViewPlot(int(self.flash_time))  # 建立CPU折線圖
                self.plot_qchart.setTitle("CPU 使用率")
                self.plot_qchart.axis_y.setTitleText("CPU")
                if device == "aosp":
                    self.plot_qchart.axis_y.setRange(0, 800)  # 設定y軸範圍
                elif device == "rtbm":
                    self.plot_qchart.axis_y.setRange(0, 200)  # 設定y軸範圍
                elif device == "vera":
                    self.plot_qchart.axis_y.setRange(0, 500)  # 設定y軸範圍
                self.ui.plot_view.setChart(self.plot_qchart)  # 將QChart加入QChartView
                self.ui.plot_view.setRenderHint(QPainter.Antialiasing)  # 抗鋸齒
                self.ui.plot_view.setRubberBand(QChartView.RectangleRubberBand)

                self.plot_qchart1 = QChartViewPlot(int(self.flash_time))  # 建立MEM折線圖
                self.plot_qchart1.setTitle("Memory 使用率")
                self.plot_qchart1.series.setColor(QColor(0, 153, 76))
                self.plot_qchart1.axis_y.setTitleText("MEM")
                self.ui.plot_view1.setChart(self.plot_qchart1)  # 將QChart加入QChartView
                self.ui.plot_view1.setRenderHint(QPainter.Antialiasing)  # 抗鋸齒
                self.ui.plot_view1.setRubberBand(QChartView.RectangleRubberBand)

                self.plot_qchart2 = QChartViewPlot(int(self.flash_time))  # 建立DISK折線圖
                self.plot_qchart2.setTitle("Disk 使用率")
                self.plot_qchart2.series.setColor(QColor(238, 118, 33))
                self.plot_qchart2.axis_y.setTitleText("Disk")
                self.ui.plot_view2.setChart(self.plot_qchart2)  # 將QChart加入QChartView
                self.ui.plot_view2.setRenderHint(QPainter.Antialiasing)  # 抗鋸齒
                self.ui.plot_view2.setRubberBand(QChartView.RectangleRubberBand)

                # 更新折線圖執行緒
                self.worker_thread = WorkerThread(int(self.flash_time))
                self.worker_thread.data_ready.connect(self.updateChartData)
                self.worker_thread.start()
            else:
                dialog_notification(self, 'no connect devices')
                self.return_to_menu()
        except Exception as e:
            print(e)

    def change_reflash_time(self, device):  # 更改刷新時間
        try:
            sec = self.ui.textEdit_3.toPlainText().strip()  # 刷新秒數
            if sec.isdigit():  # 判斷是否為數字
                self.flash_time = sec
                self.main_worker_thread.stop()  # 將正在的執行緒停止
                self.worker_thread.stop()  # 將正在的執行緒停止
                for dialog in self.dialog_group:  # 將所有子視窗關閉
                    dialog.close()
                os.popen('adb shell "pkill top"')  # 結束所有top命令
                time.sleep(2)

                # ==================重新下top指令==================
                if device == "rtbm":
                    self.main_worker_thread = Main_WorkerThread(
                        command=['adb', 'shell', 'export', 'TERM=xterm', '&&', 'top', '-b', '-o', '+%CPU', '-d', self.flash_time], device=device, win=self)
                    self.main_worker_thread.start()
                elif device == "aosp" or device == "vera":
                    self.main_worker_thread = Main_WorkerThread(
                        command=['adb', 'shell', 'top', '-b', '-d', self.flash_time], device=device, win=self)
                    self.main_worker_thread.start()

                now = QDateTime.currentDateTime()
                after = QDateTime.currentDateTime().addSecs(int(self.flash_time) * 60)
                self.plot_qchart.axis_x.setRange(now, after)  # 設定x軸範圍
                self.plot_qchart1.axis_x.setRange(now, after)  # 設定x軸範圍
                self.plot_qchart2.axis_x.setRange(now, after)  # 設定x軸範圍

                self.worker_thread = WorkerThread(int(self.flash_time))  # 折線圖執行緒，重新設定折線圖刷新時間
                self.worker_thread.data_ready.connect(self.updateChartData)
                self.worker_thread.start()
            else:
                dialog_notification(self, 'digit')
        except Exception as e:
            print(e)

    def headerClicked(self, logicalIndex):  # 點擊表頭排序
        try:
            if logicalIndex == 3:  # 點擊CPU欄位
                if self.sorted != '+%CPU':  # 如果目前排序不是以CPU，才執行
                    self.sorted = '+%CPU'
                    self.main_worker_thread.stop()
                    time.sleep(1)
                    if not self.main_worker_thread.running:
                        if self.device == "rtbm":
                            self.main_worker_thread = Main_WorkerThread(
                                command=['adb', 'shell', 'export', 'TERM=xterm', '&&', 'top', '-b', '-o', self.sorted, '-d', self.flash_time],
                                device=self.device, win=self)
                        elif self.device == "aosp":
                            self.main_worker_thread = Main_WorkerThread(
                                command=['adb', 'shell', 'top', '-b', '-s', '9', '-d', self.flash_time],
                                device=self.device, win=self)
                        elif self.device == "vera":
                            self.main_worker_thread = Main_WorkerThread(
                                command=['adb', 'shell', 'top', '-b', '-o', '%CPU', '-d', self.flash_time],
                                device=self.device, win=self)
                        self.main_worker_thread.start()

            elif logicalIndex == 4:  # 點擊MEM欄位
                if self.sorted != '+%MEM':  # 如果目前排序不是以MEM，才執行
                    self.sorted = '+%MEM'
                    self.main_worker_thread.stop()
                    time.sleep(1)
                    if not self.main_worker_thread.running:
                        if self.device == "rtbm":
                            self.main_worker_thread = Main_WorkerThread(
                                command=['adb', 'shell', 'export', 'TERM=xterm', '&&', 'top', '-b', '-o', self.sorted,'-d', self.flash_time],
                                device=self.device, win=self)
                        elif self.device == "aosp":
                            self.main_worker_thread = Main_WorkerThread(
                                command=['adb', 'shell', 'top', '-b', '-s', '10', '-d', self.flash_time],
                                device=self.device, win=self)
                        elif self.device == "vera":
                            self.main_worker_thread = Main_WorkerThread(
                                command=['adb', 'shell', 'top', '-b', '-o', '%MEM', '-d', self.flash_time],
                                device=self.device, win=self)
                        self.main_worker_thread.start()
        except Exception as e:
            print(e)

    def open_PID_Window(self, device):  # 開啟PID視窗
        try:
            pid = self.ui.textEdit.toPlainText()
            dialog = PID_DialogWindow(pid, device, self.flash_time)
            self.dialog_group.append(dialog)
            dialog.show()
        except Exception as e:
            print(e)

    def open_COMMAND_Window(self, device):  # 開啟COMMAND視窗
        try:
            cmd = self.ui.textEdit_2.toPlainText()
            dialog = CMD_DialogWindow(cmd, device, self.flash_time)
            self.dialog_group.append(dialog)
            dialog.show()
        except Exception as e:
            print(e)

    def updateChartData(self):  # 更新折線圖
        try:
            # 取得Disk /data 使用率
            disk_use_num = 0
            f = os.popen('adb shell "df | grep data | grep -v database | grep -v nvdata | grep -v aipc"')
            disk_command = f.read()
            if disk_command != '':
                disk_use = disk_command.split(' ')
                disk_use = list(filter(None, disk_use))[4]
                if disk_use != '':
                    disk_use_num = int(disk_use.replace('%', ''))
            f.close()

            # 更新折線圖數據
            if len(self.save_time_data) != 0 and len(self.save_cpu_data) != 0 and len(self.save_mem_data) != 0:
                self.buffer_cpu.append(QPointF(self.save_time_data[-1].toMSecsSinceEpoch(), self.save_cpu_data[-1]))
                self.buffer_mem.append(QPointF(self.save_time_data[-1].toMSecsSinceEpoch(), self.save_mem_data[-1]))
                self.buffer_disk.append(QPointF(self.save_time_data[-1].toMSecsSinceEpoch(), disk_use_num))

                self.plot_qchart.series.replace(self.buffer_cpu)
                self.plot_qchart1.series.replace(self.buffer_mem)
                self.plot_qchart2.series.replace(self.buffer_disk)
                if self.plot_qchart.series.count() > 60:  # 如果折線圖點的數量超過60，顯示最新60筆，所以調整x軸範圍
                    fist_time = self.save_time_data[-60]
                    last_time = self.save_time_data[-1]
                    self.plot_qchart.axis_x.setRange(fist_time, last_time)
                    self.plot_qchart1.axis_x.setRange(fist_time, last_time)
                    self.plot_qchart2.axis_x.setRange(fist_time, last_time)
        except Exception as e:
            print(e)
            self.worker_thread.stop()

    def update_progress(self, progress):  # 更新進度條
        self.ui.progressBar.setValue(progress)

    def stop_and_download(self):  # 暫停並下載chart、data
        try:
            self.main_worker_thread.stop()  # 停止正在進行的執行緒
            self.worker_thread.stop()  # 停止正在進行的執行緒
            for dialog in self.dialog_group:
                dialog.close()
            # =================撈取Row data=================
            con = sqlite3.connect("row_data.db")
            df = pd.read_sql("SELECT * FROM row_data", con)  # 查詢資料
            con.close()
            # =================設定存放資料夾=================
            time_stamp_folder_name = f"{LOCAL_DIRECTION}/Online/" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            if not os.path.exists(time_stamp_folder_name):
                os.mkdir(time_stamp_folder_name)
            # =================匯出並更新進度條=================
            self.ui.progressBar.setVisible(True)
            self.excel_exporter = ExcelExporter(time_stamp_folder_name, df, self)  # 匯出png、xlsx執行緒
            self.excel_exporter.progress_updated.connect(self.update_progress)  # 更新進度條
            self.excel_exporter.start()
            # =================將所有button Disable=================
            self.ui.flush_btn.setEnabled(False)
            self.ui.pushButton.setEnabled(False)
            self.ui.pushButton_2.setEnabled(False)
            self.ui.stop_btn.setEnabled(False)
            self.ui.return_btn.setVisible(True)  # 顯示Return to menu
        except Exception as e:
            print(e)

    def return_to_menu(self):  # 回到開始選擇畫面
        self.close_or_not = False  # 判斷是否關閉程序
        self.close()
        self.menu = StartWindow()  # 開始選擇視窗
        self.menu.show()

    def closeEvent(self, event):  # 關閉Online視窗觸發事件
        if self.close_or_not:
            reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
                if isConnectingDevice():
                    subprocess.Popen(['adb', 'shell', 'pkill', 'top'],
                                     stdout=subprocess.PIPE)  # 結束top命令
                self.worker_thread.stop()
                self.main_worker_thread.stop()
                self.con.close()
            else:
                event.ignore()
        else:
            if isConnectingDevice():
                subprocess.Popen(['adb', 'shell', 'pkill', 'top'],
                                 stdout=subprocess.PIPE)  # 結束top命令
            if self.worker_thread is not None:
                self.worker_thread.stop()
            if self.main_worker_thread is not None:
                self.main_worker_thread.stop()
            if self.con is not None:
                self.con.close()


class Main_WorkerThread(QThread):  # Online Version主視窗執行緒
    finished = pyqtSignal(str)
    
    def __init__(self, command, device, win):
        super().__init__()
        self.con = None
        self.process = None
        self.all_data = None
        self.tasks_info = None
        self.now_stamp = None
        self.command = command
        self.device = device
        self.window = win
        self.running = True

    def stop(self):  # 停止執行緒
        self.running = False
        if self.process is not None:
            self.process.kill()

    def run(self):  # 開始執行緒
        try:
            self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # 執行top指令
            while self.running:
                self.all_data = []
                self.now_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 顯示在介面上
                line = self.process.stdout.readline().decode('utf-8').strip('\r\n')
                if line.strip('\n') != '':
                    task = handle_top_text(self.device, 'online', None, self.process, line, 'Tasks:')
                    self.tasks_info = task[1]
                    self.all_data = row_data(self.process, int(task[0]), self.all_data)
                    self.main_load_data()
        except Exception as e:
            print(e)

    def main_load_data(self):
        try:
            self.window.ui.tableWidget.setRowCount(0)
            self.window.ui.tableWidget.clearContents()
            self.window.ui.label_2.setText('時間：{}'.format(self.now_stamp))
            self.window.ui.label_3.setText('{}'.format(self.tasks_info))
            qtDateTime = QtCore.QDateTime.fromString(self.now_stamp, 'yyyy-MM-dd hh:mm:ss')  # 將時間轉成QDateTime格式
            self.window.save_time_data.append(qtDateTime)  # 將時間加進self的參數以便畫圖使用
            save_cpu_once = []
            save_mem_once = []

            self.con = sqlite3.connect("row_data.db")  # 連線db
            cur = self.con.cursor()
            time.sleep(0.1)
            row = 0
            sql_cmd = "INSERT INTO row_data VALUES "  # 存row data
            self.window.ui.tableWidget.setRowCount(len(self.all_data))
            for d in self.all_data:
                self.window.ui.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(d[0]))  # PID
                self.window.ui.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(d[1]))  # USER
                self.window.ui.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(d[11]))  # COMMAND
                self.window.ui.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(d[8]))  # CPU
                self.window.ui.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(d[9]))  # MEM
                self.window.ui.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(d[10]))  # TIME+
                save_cpu_once.append(float(d[8]))
                save_mem_once.append(float(d[9]))
                if row == (len(self.all_data) - 1):  # 判斷是不是最後一筆
                    sql_cmd += f"('{self.now_stamp}', {d[0]}, '{d[1]}', '{d[11]}', {d[8]}, {d[9]}, '{d[10]}')"  # 最後一筆，後面不加逗號
                else:
                    sql_cmd += f"('{self.now_stamp}', {d[0]}, '{d[1]}', '{d[11]}', {d[8]}, {d[9]}, '{d[10]}'),"
                row = row + 1
            cur.execute(sql_cmd)  # 執行Sql
            self.con.commit()
            self.con.close()
            total_cpu = sum(save_cpu_once)  # 計算CPU total使用率
            total_mem = sum(save_mem_once)  # 計算MEM total使用率
            self.window.save_cpu_data.append(total_cpu)  # 將CPU total使用率加進self的參數以便畫圖使用
            self.window.save_mem_data.append(total_mem)  # 將MEM total使用率加進self的參數以便畫圖使用
            self.window.ui.total_cpu.setText('{:.1f} '.format(total_cpu))  # 顯示CPU total使用率
            self.window.ui.total_mem.setText('{:.1f} '.format(total_mem))  # 顯示MEM total使用率
            self.window.ui.cpu_high.setText('{:.1f}'.format(max(self.window.save_cpu_data)))  # 顯示CPU total使用率最高值
            self.window.ui.cpu_low.setText('{:.1f}'.format(min(self.window.save_cpu_data)))  # 顯示CPU total使用率最低值
            self.window.ui.cpu_avg.setText('{:.1f}'.format(sum(self.window.save_cpu_data) / len(self.window.save_cpu_data)))  # 顯示CPU total使用率平均值
            self.window.ui.mem_high.setText('{:.1f}'.format(max(self.window.save_mem_data)))  # 顯示MEM total使用率最高值
            self.window.ui.mem_low.setText('{:.1f}'.format(min(self.window.save_mem_data)))  # 顯示MEM total使用率最低值
            self.window.ui.mem_avg.setText('{:.1f}'.format(sum(self.window.save_mem_data) / len(self.window.save_mem_data)))  # 顯示MEM total使用率平均值
            print('load end time:', datetime.datetime.now())
        except Exception as e:
            self.con.close()
            print(e)

class PID_DialogWindow(QtWidgets.QDialog, Ui_PID_Dialog):  # PID子視窗
    def __init__(self, pid, device, flash_sec):
        super(PID_DialogWindow, self).__init__()
        self.setupUi(self)
        self.save_time_data = []
        self.save_cpu_data = []
        self.save_mem_data = []
        self.buffer_cpu = []
        self.buffer_mem = []
        self.max_cpu = 100  # 預設CPU使用率折線圖y軸最高值
        self.max_mem = 100  # 預設MEM使用率折線圖y軸最高值

        self.tableWidget_2.setColumnWidth(0, 60)  # 設定PID欄位寬度
        self.tableWidget_2.setColumnWidth(1, 80)  # 設定USER欄位寬度
        self.tableWidget_2.setColumnWidth(2, 160)  # 設定COMMAND欄位寬度
        self.tableWidget_2.setColumnWidth(3, 70)  # 設定CPU欄位寬度
        self.tableWidget_2.setColumnWidth(4, 70)  # 設定MEM欄位寬度
        self.tableWidget_2.setColumnWidth(5, 100)  # 設定TIME+欄位寬度

        # ==================執行top指令==================
        if device == "rtbm":
            self.PID_worker_thread = PID_WorkerThread(
                command=['adb', 'shell', 'export', 'TERM=xterm', '&&', 'top', '-b', '-d', flash_sec, '-p', pid],
                device=device, window=self)
        elif device == "aosp" or device == "vera":
            self.PID_worker_thread = PID_WorkerThread(
                command=['adb', 'shell', 'top', '-b', '-d', flash_sec, '-p', pid],
                device=device, window=self)
        self.PID_worker_thread.start()

        self.plot_qchart = QChartViewPlot(int(flash_sec))  # 建立CPU使用率折線圖
        self.plot_qchart.setTitle("CPU 使用率")
        self.plot_qchart.axis_y.setTitleText("CPU")
        self.plot_view.setChart(self.plot_qchart)
        self.plot_view.setRenderHint(QPainter.Antialiasing)  # 抗鋸齒
        self.plot_view.setRubberBand(QChartView.RectangleRubberBand)

        self.plot_qchart1 = QChartViewPlot(int(flash_sec))  # 建立CPU使用率折線圖
        self.plot_qchart1.setTitle("Memory 使用率")
        self.plot_qchart1.series.setColor(QColor(0, 153, 76))
        self.plot_qchart1.axis_y.setTitleText("MEM")
        self.plot_view1.setChart(self.plot_qchart1)
        self.plot_view1.setRenderHint(QPainter.Antialiasing)  # 抗鋸齒
        self.plot_view1.setRubberBand(QChartView.RectangleRubberBand)

        # 更新折線圖數據執行緒
        self.worker_thread = WorkerThread(int(flash_sec))
        self.worker_thread.data_ready.connect(self.updateChartData)
        self.worker_thread.start()

        if device == "rtbm":
            self.pid_sub_worker_thead = PID_subprocess_WorkerThread(
                command=['adb', 'shell', 'export', 'TERM=xterm', '&&', 'top', '-H', '-b', '-d', flash_sec, '-p', pid],
                device=device, dialog=self)
        elif device == "aosp" or device == "vera":
            self.pid_sub_worker_thead = PID_subprocess_WorkerThread(
                command=['adb', 'shell', 'top', '-H', '-b', '-d', flash_sec, '-p', pid],
                device=device, dialog=self)
        self.pid_sub_worker_thead.start()

    def closeEvent(self, event):  # 關閉PID子視窗觸發事件
        self.worker_thread.stop()  # 更新折線圖執行緒
        self.pid_sub_worker_thead.stop()  # 搜尋PID的所有子程序執行緒
        self.PID_worker_thread.stop()  # 搜尋PID的執行緒

    def updateChartData(self):  #更新折線圖數據
        try:
            if len(self.save_time_data) != 0 and len(self.save_cpu_data) != 0 and len(self.save_mem_data) != 0:
                if self.save_cpu_data[-1] > self.max_cpu:  # 最新一筆的CPU是否有大於預設，有就調整y軸範圍
                    self.max_cpu = self.save_cpu_data[-1]
                    if 100 < self.max_cpu <= 150:
                        self.plot_qchart.axis_y.setRange(0, 150)
                    elif 150 < self.max_cpu <= 200:
                        self.plot_qchart.axis_y.setRange(0, 200)
                if self.save_mem_data[-1] > self.max_mem:  # 最新一筆的MEM是否有大於預設，有就調整y軸範圍
                    self.max_mem = self.save_mem_data[-1]
                    if 100 < self.max_mem <= 150:
                        self.plot_qchart1.axis_y.setRange(0, 150)
                    elif 150 < self.max_mem <= 200:
                        self.plot_qchart1.axis_y.setRange(0, 200)
                self.buffer_cpu.append(QPointF(self.save_time_data[-1].toMSecsSinceEpoch(), self.save_cpu_data[-1]))
                self.buffer_mem.append(QPointF(self.save_time_data[-1].toMSecsSinceEpoch(), self.save_mem_data[-1]))
                self.plot_qchart.series.replace(self.buffer_cpu)
                self.plot_qchart1.series.replace(self.buffer_mem)
                if self.plot_qchart.series.count() > 60:
                    fist_time = self.save_time_data[-60]
                    last_time = self.save_time_data[-1]
                    self.plot_qchart.axis_x.setRange(fist_time, last_time)
                    self.plot_qchart1.axis_x.setRange(fist_time, last_time)
        except Exception as e:
            print(e)

class PID_WorkerThread(QThread):  # 搜尋PID執行緒
    finished = pyqtSignal(str)

    def __init__(self, command, device, window):
        super().__init__()
        self.sub_all_data = None
        self.now_stamp1 = None
        self.process = None
        self.command = command
        self.device = device
        self.window = window
        self.running = True

    def stop(self):  # 停止執行緒
        self.running = False
        if self.process is not None:
            self.process.kill()

    def run(self):  # 開始執行緒
        try:
            self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while self.running:
                self.sub_all_data = []
                self.now_stamp1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 顯示執行時間
                line = self.process.stdout.readline().decode('utf-8').strip('\r\n')
                if line.strip('\n') != '':
                    task = handle_top_text(self.device, 'online', None, self.process, line, 'Tasks:')
                    self.sub_all_data = row_data(self.process, int(task[0]), self.sub_all_data)
                    self.sub_pid_load_data()
        except Exception as e:
            print(e)

    def sub_pid_load_data(self):
        try:
            self.window.label_2.setText('時間：{}'.format(self.now_stamp1))
            qtDateTime = QtCore.QDateTime.fromString(self.now_stamp1, 'yyyy-MM-dd hh:mm:ss')  # 將時間轉成QDateTime格式
            self.window.save_time_data.append(qtDateTime)  # 將時間加進self的參數以便畫圖使用
            row = 0
            for d in self.sub_all_data:  # 不顯示在Table上，PID所有子程序才要顯示
                self.window.save_cpu_data.append(float(d[8]))  # 以便畫圖使用
                self.window.save_mem_data.append(float(d[9]))  # 以便畫圖使用
                row = row + 1
            self.window.cpu_high.setText('{:.1f}'.format(max(self.window.save_cpu_data)))  # 顯示此PID的CPU使用率最高值
            self.window.cpu_low.setText('{:.1f}'.format(min(self.window.save_cpu_data)))  # 顯示此PID的CPU使用率最低值
            self.window.cpu_avg.setText('{:.1f}'.format(sum(self.window.save_cpu_data) / len(self.window.save_cpu_data)))  # 顯示此PID的CPU使用率平均值
            self.window.mem_high.setText('{:.1f}'.format(max(self.window.save_mem_data)))  # 顯示此PID的MEM使用率最高值
            self.window.mem_low.setText('{:.1f}'.format(min(self.window.save_mem_data)))  # 顯示此PID的MEM使用率最低值
            self.window.mem_avg.setText('{:.1f}'.format(sum(self.window.save_mem_data) / len(self.window.save_mem_data)))  # 顯示此PID的MEM使用率平均值
            print('sub_pid_end:', datetime.datetime.now())
        except Exception as e:
            print(e)

class PID_subprocess_WorkerThread(QThread): # 搜尋PID所有子程序的執行緒
    finished = pyqtSignal()

    def __init__(self, command, device, dialog):
        super().__init__()
        self.data = None
        self.now_stamp1 = None
        self.process = None
        self.command = command
        self.device = device
        self.dialog = dialog
        self.running = True

    def stop(self):  # 停止執行緒
        self.running = False
        if self.process is not None:
            self.process.kill()

    def run(self):  # 開始執行緒
        try:
            self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while self.running:
                self.data = []
                line = self.process.stdout.readline().decode('utf-8').strip('\r\n')
                if line.strip('\n') != '':
                    task = handle_top_text(self.device, 'online', None, self.process, line, 'Threads:')
                    self.data = row_data(self.process, int(task[0]), self.data)
                    self.load_data()
        except Exception as e:
            print(e)

    def load_data(self):
        self.dialog.tableWidget_2.setRowCount(0)
        self.dialog.tableWidget_2.clearContents()
        time.sleep(0.1)
        for d in self.data:  # PID所有子程序顯示在Table
            rowPosition = self.dialog.tableWidget_2.rowCount()
            self.dialog.tableWidget_2.insertRow(rowPosition)
            self.dialog.tableWidget_2.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(d[0]))  # PID
            self.dialog.tableWidget_2.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(d[1]))  # USER
            self.dialog.tableWidget_2.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(d[11]))  # COMMAND
            self.dialog.tableWidget_2.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(d[8]))  # CPU
            self.dialog.tableWidget_2.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(d[9]))  # MEM
            self.dialog.tableWidget_2.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(d[10]))  # TIME+
        print('sub_pid_sub_end:', datetime.datetime.now())

class CMD_DialogWindow(QtWidgets.QDialog, Ui_COMMAND_Dialog):  # COMMAND視窗
    def __init__(self, cmd, device, flash_sec):
        super(CMD_DialogWindow, self).__init__()
        self.setupUi(self)
        self.analyze_first = True
        self.save_all_data = []
        self.save_cmd_time_data = []
        self.save_cmd_cpu_data = []
        self.save_cmd_mem_data = []
        self.save_each_pid_draw = []
        self.save_each_cpu_draw = []
        self.save_each_mem_draw = []
        self.flash_sec = flash_sec
        self.max_cpu = 10
        self.max_mem = 10

        self.tableWidget_2.setColumnWidth(0, 60)  # 設定PID欄位寬度
        self.tableWidget_2.setColumnWidth(1, 80)  # 設定USER欄位寬度
        self.tableWidget_2.setColumnWidth(2, 160)  # 設定COMMAND欄位寬度
        self.tableWidget_2.setColumnWidth(3, 70)  # 設定CPU欄位寬度
        self.tableWidget_2.setColumnWidth(4, 70)  # 設定MEM欄位寬度
        self.tableWidget_2.setColumnWidth(5, 100)  # 設定TIME+欄位寬度
        self.tableWidget_2.cellClicked.connect(self.cell_was_clicked)  # 定義點擊PID欄位觸發事件
        self.analyze_btn.clicked.connect(self.draw_multiple_line_chart)  # 定義分析按鈕觸發事件
        self.reset_btn.clicked.connect(self.reset_selected_pid)  # 定義清除按鈕觸發事件

        # ====================執行top指令====================
        if device == "rtbm":
            self.CMD_worker_thread = COMMAND_WorkerThread(
                command=['adb', 'shell', 'export', 'TERM=xterm', '&&', 'top', '-b', '-d', flash_sec, '-p', '$(pgrep',
                         '-d', '","', '--ignore-case', cmd, ')'], device=device, window=self)
        elif device == "aosp" or device == "vera":
            self.CMD_worker_thread = COMMAND_WorkerThread(
                command=['adb', 'shell', 'top', '-b', '-d', flash_sec, '-p', '$(pgrep', '-d', '","', '--ignore-case',
                         cmd, ')'], device=device, window=self)
        self.CMD_worker_thread.start()

        self.plot_qchart = QChartMultipleViewPlot(int(self.flash_sec))  # 建立CPU使用率折線圖
        self.plot_qchart.setTitle("CPU 使用率")
        self.plot_qchart.axis_y.setTitleText("CPU")
        self.plot_view.setChart(self.plot_qchart)
        self.plot_view.setRenderHint(QPainter.Antialiasing)  # 抗鋸齒
        self.plot_view.setRubberBand(QChartView.RectangleRubberBand)

        self.plot_qchart1 = QChartMultipleViewPlot(int(self.flash_sec))  # 建立MEM使用率折線圖
        self.plot_qchart1.setTitle("Memory 使用率")
        self.plot_qchart1.axis_y.setTitleText("MEM")
        self.plot_view1.setChart(self.plot_qchart1)
        self.plot_view1.setRenderHint(QPainter.Antialiasing)  # 抗鋸齒
        self.plot_view1.setRubberBand(QChartView.RectangleRubberBand)

    def closeEvent(self, event):  # 關閉COMMAND視窗事件
        if not self.analyze_first:
            self.worker_thread.stop()
        self.CMD_worker_thread.stop()

    def updateChartData(self):  # 更新折線圖數據
        try:
            if len(self.save_cmd_time_data) != 0 and len(self.save_each_cpu_draw) != 0 and len(self.save_each_mem_draw) != 0:
                for i in range(self.series_length):  # 根據使用者選擇幾個PID就產生幾個折線
                    pid_ = self.series_pid_list[i]  # 取得PID
                    index = self.save_each_pid_draw[-1].index(pid_)  # 取PID的index位置
                    if self.save_each_cpu_draw[-1][index] > self.max_cpu:
                        self.max_cpu = self.save_each_cpu_draw[-1][index]
                        if 10 < self.max_cpu <= 50:
                            self.plot_qchart.axis_y.setRange(0, 50)
                        elif 50 < self.max_cpu <= 100:
                            self.plot_qchart.axis_y.setRange(0, 100)
                        elif 100 < self.max_cpu <= 200:
                            self.plot_qchart.axis_y.setRange(0, 200)
                    if self.save_each_mem_draw[-1][index] > self.max_mem:
                        self.max_mem = self.save_each_mem_draw[-1][index]
                        if 10 < self.max_mem <= 50:
                            self.plot_qchart1.axis_y.setRange(0, 50)
                        elif 50 < self.max_mem <= 100:
                            self.plot_qchart1.axis_y.setRange(0, 100)
                        elif 100 < self.max_mem <= 200:
                            self.plot_qchart1.axis_y.setRange(0, 200)
                    getattr(self, f"buffer_cpu_{i}", None).append(QPointF(self.save_cmd_time_data[-1].toMSecsSinceEpoch(), self.save_each_cpu_draw[-1][index]))  # 動態產生的buffer_cpu_X參數要存折線圖的點
                    getattr(self, f"buffer_mem_{i}", None).append(QPointF(self.save_cmd_time_data[-1].toMSecsSinceEpoch(), self.save_each_mem_draw[-1][index]))  # 動態產生的buffer_cpu_X參數要存折線圖的點
                    self.series_cpu_list[i].replace(getattr(self, f"buffer_cpu_{i}", None))
                    self.series_mem_list[i].replace(getattr(self, f"buffer_mem_{i}", None))
                if self.series_count > 0:
                    if self.series_cpu_list[0].count() > 60:
                        fist_time = self.save_cmd_time_data[-60]
                        last_time = self.save_cmd_time_data[-1]
                        self.plot_qchart.axis_x.setRange(fist_time, last_time)
                        self.plot_qchart1.axis_x.setRange(fist_time, last_time)
        except Exception as e:
            print(e)

    def cell_was_clicked(self, row, column):  # 點擊選擇PID觸發事件
        if column == 0:  # PID欄位，如要改別成COMMAND欄位就是2
            item = self.tableWidget_2.item(row, column).text()  # 取得PID值
            if self.pid_group.toPlainText() == '':  # 如果輸入框是空的
                self.pid_group.setText(item)
            else:
                pid_list = self.pid_group.toPlainText().strip().split(',')  # 將PID以逗號分隔
                if item not in pid_list:  # 如果沒有選到重複的PID
                    if len(pid_list) > 4:  # 如果已經超過五個
                        dialog_notification(self, 'over_five')  # 提醒不要超過五個
                    else:
                        self.pid_group.setText(self.pid_group.toPlainText() + ',' + item)  # 新增至輸入框
                else:
                    dialog_notification(self, 'repeat')  # 提醒不要重複

    def reset_selected_pid(self):  # 清除輸入框文字並移除折線
        if not self.analyze_first:
            self.plot_qchart.removeAllSeries()  # 移除所有折線
            self.plot_qchart1.removeAllSeries()  # 移除所有折線
            self.worker_thread.stop()
        self.pid_group.setText('')

    def draw_multiple_line_chart(self):  # 畫多折線圖
        if not self.analyze_first:  # 如果不是第一次畫圖
            self.plot_qchart.removeAllSeries()  # 移除所有折線
            self.plot_qchart1.removeAllSeries()  # 移除所有折線
            self.worker_thread.stop()  # 停止更新折線圖數據執行緒
        pid_list = self.pid_group.toPlainText().strip().split(',')
        if len(pid_list) > 5:
            dialog_notification(self, 'over_five')
        else:
            pid_list = list(filter(None, pid_list))  # 移掉空的值
            self.plot_qchart.legend().setVisible(True)  # 顯示折線圖例
            self.plot_qchart1.legend().setVisible(True)  # 顯示折線圖例
            self.series_cpu_list = []
            self.series_mem_list = []
            self.series_pid_list = []
            self.series_length = len(pid_list)
            self.series_count = 0
            now = QDateTime.currentDateTime()
            after = QDateTime.currentDateTime().addSecs(int(self.flash_sec) * 60)
            self.plot_qchart.axis_x.setRange(now, after)
            self.plot_qchart1.axis_x.setRange(now, after)
            for i in range(self.series_length):
                self.series_count += 1
                buffer_cpu = []
                buffer_mem = []
                setattr(self, f"buffer_cpu_{i}", buffer_cpu)  # 動態產生參數
                setattr(self, f"buffer_mem_{i}", buffer_mem)  # 動態產生參數

                series_cpu = QSplineSeries()  # CPU折線
                self.plot_qchart.addSeries(series_cpu)
                series_cpu.attachAxis(self.plot_qchart.axis_x)
                series_cpu.attachAxis(self.plot_qchart.axis_y)
                series_cpu.setName(pid_list[i])
                self.series_pid_list.append(pid_list[i])
                self.series_cpu_list.append(series_cpu)

                series_mem = QSplineSeries()  # MEM折線
                self.plot_qchart1.addSeries(series_mem)
                series_mem.attachAxis(self.plot_qchart1.axis_x)
                series_mem.attachAxis(self.plot_qchart1.axis_y)
                series_mem.setName(pid_list[i])
                self.series_mem_list.append(series_mem)

            # 更新折線圖數據
            self.worker_thread = WorkerThread(int(self.flash_sec))
            self.worker_thread.data_ready.connect(self.updateChartData)
            self.worker_thread.start()
            self.analyze_first = False


class COMMAND_WorkerThread(QThread):  # 搜尋COMMAND執行緒
    finished = pyqtSignal(str)

    def __init__(self, command, device, window):
        super().__init__()
        self.sub_cmd_all_data = None
        self.now_stamp2 = None
        self.process = None
        self.command = command
        self.device = device
        self.window = window
        self.running = True

    def stop(self):  # 停止執行緒
        self.running = False
        if self.process is not None:
            self.process.kill()

    def run(self):  # 開始執行緒
        try:
            self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while self.running:
                self.sub_cmd_all_data = []
                self.now_stamp2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                line = self.process.stdout.readline().decode('utf-8').strip('\r\n')
                if line.strip('\n') != '':
                    task = handle_top_text(self.device, 'online', None, self.process, line, 'Tasks:')
                    self.sub_cmd_all_data = row_data(self.process, int(task[0]), self.sub_cmd_all_data)
                    self.sub_cmd_load_data()
        except Exception as e:
            print(e)
            self.process.kill()

    def sub_cmd_load_data(self):
        try:
            self.window.tableWidget_2.setRowCount(0)
            self.window.tableWidget_2.clearContents()
            self.window.label_2.setText('時間：{}'.format(self.now_stamp2))
            qtDateTime = QtCore.QDateTime.fromString(self.now_stamp2, 'yyyy-MM-dd hh:mm:ss')  # 將時間轉成QDateTime格式
            self.window.save_cmd_time_data.append(qtDateTime)  # 將時間加進self的參數以便畫圖使用
            self.window.save_all_data = self.sub_cmd_all_data
            row = 0
            save_pid_once = []
            save_cpu_once = []
            save_mem_once = []
            time.sleep(0.1)
            self.window.tableWidget_2.setRowCount(len(self.sub_cmd_all_data))
            for d in self.sub_cmd_all_data:
                self.window.tableWidget_2.setItem(row, 0, QtWidgets.QTableWidgetItem(d[0]))  # PID
                self.window.tableWidget_2.setItem(row, 1, QtWidgets.QTableWidgetItem(d[1]))  # USER
                self.window.tableWidget_2.setItem(row, 2, QtWidgets.QTableWidgetItem(d[11]))  # COMMAND
                self.window.tableWidget_2.setItem(row, 3, QtWidgets.QTableWidgetItem(d[8]))  # CPU
                self.window.tableWidget_2.setItem(row, 4, QtWidgets.QTableWidgetItem(d[9]))  # MEM
                self.window.tableWidget_2.setItem(row, 5, QtWidgets.QTableWidgetItem(d[10]))  # TIME+
                save_pid_once.append(d[0])  # 存pid
                save_cpu_once.append(float(d[8]))
                save_mem_once.append(float(d[9]))
                self.window.save_cmd_cpu_data.append(float(d[8]))
                self.window.save_cmd_mem_data.append(float(d[9]))
                row = row + 1
            self.window.save_each_pid_draw.append(save_pid_once)  # 以便畫圖使用
            self.window.save_each_cpu_draw.append(save_cpu_once)  # 以便畫圖使用
            self.window.save_each_mem_draw.append(save_mem_once)  # 以便畫圖使用
            self.window.cpu_high.setText('{:.1f}'.format(max(self.window.save_cmd_cpu_data)))  # 顯示所有COMMAND的CPU使用率最高值
            self.window.cpu_low.setText('{:.1f}'.format(min(self.window.save_cmd_cpu_data)))  # 顯示所有COMMAND的CPU使用率最低值
            self.window.cpu_avg.setText('{:.1f}'.format(sum(self.window.save_cmd_cpu_data) / len(self.window.save_cmd_cpu_data)))  # 顯示所有COMMAND的CPU使用率平均值
            self.window.mem_high.setText('{:.1f}'.format(max(self.window.save_cmd_mem_data)))  # 顯示所有COMMAND的MEM使用率最高值
            self.window.mem_low.setText('{:.1f}'.format(min(self.window.save_cmd_mem_data)))  # 顯示所有COMMAND的MEM使用率最低值
            self.window.mem_avg.setText('{:.1f}'.format(sum(self.window.save_cmd_mem_data) / len(self.window.save_cmd_mem_data)))  # 顯示所有COMMAND的MEM使用率平均值
            print('sub_cmd_end:', datetime.datetime.now())
        except Exception as e:
            print(e)

class WorkerThread(QThread):  # 循環執行緒
    data_ready = pyqtSignal()

    def __init__(self, sec=3):
        super().__init__()
        self.running = True
        self.sec = sec

    def run(self):
        i = 0
        while self.running:
            self.data_ready.emit()
            # 模拟每隔一秒更新一次数据
            time.sleep(self.sec)

    def stop(self):
        self.running = False

class off_top_Thread(QThread):  # Offline Version執行top指令執行緒
    finished = pyqtSignal()

    def __init__(self, interval, loop, path, txt_name, device):
        super().__init__()
        self.interval = interval
        self.loop = loop
        self.path = path
        self.txt_name = txt_name
        self.device = device

    def run(self):
        subprocess.call(['adb', 'root'])  # 用root身分
        time_string = time.strftime('%m%d%H%M%Y.%S')
        subprocess.call(['adb', 'shell', 'date', time_string])  # 修改設備時間
        if self.device == "rtbm":
            subprocess.Popen(
                'adb shell nohup sh -c "export TERM=xterm & top -b -d ' + self.interval + ' -n ' + self.loop + ' >> ' + self.path + self.txt_name + '" 2>&1 &',
                shell=True, stdout=subprocess.PIPE)  # RTBM需設定export TERM=xterm，使用nohup指令
        else:
            subprocess.call(
                ['adb', 'shell', 'nohup', 'sh', '-c', '"top', '-b', '-d', self.interval, '-n', self.loop, '>>',
                 self.path + self.txt_name, '"', '&'])  # 使用nohup指令


class off_disk_Thread(QThread):  # Offline Version執行disk shell執行緒
    finished = pyqtSignal()

    def __init__(self, interval, loop, path, csv_name, device):
        super().__init__()
        self.interval = interval
        self.loop = loop
        self.path = path
        self.csv_name = csv_name
        self.device = device

    def run(self):
        ABS_DIR_PATH = resource_path() + os.sep  # 需判斷執行檔的路徑
        print(ABS_DIR_PATH)
        if self.device == "rtbm":
            file = "Get_Disk_Data_RTBM"
        elif self.device == "vera":
            file = "Get_Disk_Data_Vera"
        else:
            file = "Get_Disk_Data"

        # ======================讀取shell，並將interval、loop寫進shell======================
        fin = open(f"{ABS_DIR_PATH}/shell/{file}.sh", "rt", encoding="utf-8")
        contents = fin.read()
        fin.close()
        fout = open(f"{ABS_DIR_PATH}/shell/{file}.sh2", "w", newline="\n")
        fout.write(f"interval={int(self.interval)}\n")
        fout.write(f"loops={self.loop}\n")
        fout.write(f"path={self.path}\n")
        fout.write(f"filename={self.csv_name}\n")
        fout.write(contents)
        fout.close()

        # copy sh2 to device and rename to sh
        subprocess.call(["adb", "push", f"{ABS_DIR_PATH}shell/{file}.sh2", f"{self.path}{file}.sh"])

        # remove sh2
        os.remove(f"{ABS_DIR_PATH}shell/{file}.sh2")

        # grant execute permission
        subprocess.call(["adb", "shell", "chmod", "+x", f"{self.path}{file}.sh"])

        # 循環背景執行shell
        if self.device == "rtbm":
            procId = subprocess.Popen(f'adb shell ', stdin=subprocess.PIPE)
            procId.communicate(b"cd /data/local/tmp/qa/offline; nohup ./Get_Disk_Data_RTBM.sh >/dev/null 2>&1 & \n")
        else:
            subprocess.call(['adb', 'shell', f"nohup {self.path}{file}.sh &"])

class ExcelExporter(QThread):  # 匯出Excel、折線圖png執行緒
    progress_updated = pyqtSignal(int)

    def __init__(self, folder_name, dataframe, window):
        super().__init__()
        self.progress = 0
        self.cancel_requested = False
        self.time_stamp_folder_name = folder_name
        self.df = dataframe
        self.window = window

    def run(self):
        # 執行Excel匯出操作
        writer = pd.ExcelWriter(f'{self.time_stamp_folder_name}/Row_data.xlsx', engine='xlsxwriter')
        self.df.to_excel(writer, sheet_name='row_data', index=False)
        writer.close()

        # 將QChartView渲染為圖像
        pixmap = QPixmap(900, 400)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        self.window.ui.plot_view.render(painter)  # 將QChartView渲染為圖像
        painter.end()
        pixmap.save(f"{self.time_stamp_folder_name}/CPU_chart.png")  # 將圖像保存為PNG格式

        painter1 = QPainter(pixmap)
        painter1.setRenderHint(QPainter.Antialiasing)
        self.window.ui.plot_view1.render(painter1)  # 將QChartView渲染為圖像
        painter1.end()
        pixmap.save(f"{self.time_stamp_folder_name}/MEM_chart.png")  # 將圖像保存為PNG格式

        painter2 = QPainter(pixmap)
        painter2.setRenderHint(QPainter.Antialiasing)
        self.window.ui.plot_view2.render(painter2)  # 將QChartView渲染為圖像
        painter2.end()
        pixmap.save(f"{self.time_stamp_folder_name}/DISK_chart.png")  # 將圖像保存為PNG格式

        while not self.isInterruptionRequested():  # 沒有中斷
            self.progress += 1
            self.progress_updated.emit(self.progress)  # 更新進度條
            time.sleep(0.01)
            if self.progress == 100:  # 到100就停止
                super().requestInterruption()


class QChartViewPlot(QChart):  # 單折線圖
    def __init__(self, flash_time, parent=None):
        super(QChartViewPlot, self).__init__(parent)
        self.window = parent
        self.legend().setVisible(False)
        self.setGeometry(0, 0, 800, 300)
        self.axis_x = QDateTimeAxis()
        self.axis_x.setTickCount(60)
        now = QDateTime.currentDateTime()
        after = QDateTime.currentDateTime().addSecs(flash_time * 60)
        self.axis_x.setRange(now, after)
        self.axis_x.setFormat("")   # 如要顯示時間，請修改成"HH:mm"
        self.axis_x.setTitleText("時間")
        self.addAxis(self.axis_x, Qt.AlignBottom)

        self.axis_y = QValueAxis()
        self.axis_y.setTickCount(5)
        self.axis_y.setRange(0, 100)
        self.axis_y.setLabelFormat("%.0f%%")
        self.addAxis(self.axis_y, Qt.AlignLeft)

        self.series = QSplineSeries()
        self.addSeries(self.series)
        self.series.attachAxis(self.axis_x)
        # font = QFont()
        # font.setPointSize(7)  # 設定文字大小
        # self.axis_x.setLabelsAngle(-90)  # x軸Label旋轉90度
        # self.axis_x.setLabelsFont(font)
        self.series.attachAxis(self.axis_y)


class QChartMultipleViewPlot(QChart):  # 多折線圖
    def __init__(self, flash_time, parent=None):
        super(QChartMultipleViewPlot, self).__init__(parent)
        self.window = parent
        self.setGeometry(0, 0, 800, 300)
        self.axis_x = QDateTimeAxis()
        self.axis_x.setTickCount(60)
        now = QDateTime.currentDateTime()
        after = QDateTime.currentDateTime().addSecs(flash_time * 60)
        self.axis_x.setRange(now, after)
        self.axis_x.setFormat("")
        self.axis_x.setTitleText("時間")
        self.addAxis(self.axis_x, Qt.AlignBottom)

        self.axis_y = QValueAxis()
        self.axis_y.setTickCount(5)
        self.axis_y.setRange(0, 10)
        self.axis_y.setLabelFormat("%.0f%%")
        self.addAxis(self.axis_y, Qt.AlignLeft)

def row_data(process, data_length=0, all_data=None, file=None):  # top底下row data處理
    if all_data is None or file is not None:
        all_data = []
    for j in range(0, data_length):
        row = b''
        if process is not None:
            row = process.stdout.readline().decode('utf-8').strip('\r\n')  # Online版本
        elif file is not None:
            row = file.readline().strip('\n')  # Offline版本
        if row != b'':
            if row != b'\r\n':
                row_split = row.split(' ')  # 用空格為分隔
                row_split = list(filter(None, row_split))  # 將空值移除
                if len(row_split) != 0:
                    all_data.append(row_split)
    return all_data

def handle_top_text(device, version, f, process, line, start_text):  # top標題列處理
    if device in ('rtbm', 'vera'):  # RTBM、Vera都是以top開頭
        if line.startswith('top -'):
            task_len = 0
            topic = ''
            for i in range(6):  # 讀取前六行
                if version == "offline":
                    topic = f.readline()  # 如果是offline version是讀檔案
                else:
                    topic = process.stdout.readline().decode('utf-8').strip('\r\n')  # 如果是online version是讀subprocess
                if topic.startswith(start_text):  # 一般開頭為Tasks: ，搜尋子程序開頭為Threads:
                    t = topic.split(',')
                    s = t[0].strip().replace(start_text, '').replace('total', '')  # 取得task數量
                    task_len = int(s)
            return [task_len, topic]
    elif device == "aosp":  # AOSP是以Tasks開頭
        if line.startswith(start_text):  # 一般開頭為Tasks: ，搜尋子程序開頭為Threads:
            t = line.split(',')
            task_len = t[0].strip().replace(start_text, '').replace('total', '')  # 取得task數量
            for i in range(4):  # 讀取前四行
                if version == "offline":
                    f.readline()  # 如果是offline version是讀檔案
                else:
                    process.stdout.readline().decode('utf-8').strip('\r\n')  # 如果是online version是讀subprocess
            return [task_len, line]

def dialog_notification(window, str_class):  # 提醒視窗
    dlg = QMessageBox(window)
    dlg.setWindowTitle("Question!")
    if str_class == 'digit':
        dlg.setText("This is not a digit.")
    elif str_class == 'over_five':
        dlg.setText("Don't select over five.\nThe analysis chart will be too complicated.")
    elif str_class == 'repeat':
        dlg.setText("Don't select repeated PID.")
    elif str_class == 'no_data':
        dlg.setText("No data!")
    elif str_class == "no checked":
        dlg.setText("Please Choose device and version!")
    elif str_class == "incorrect file":
        dlg.setText("Please Choose correct file!")
    elif str_class == "no connect devices":
        dlg.setText("Please connect device!")
    elif str_class == "can stop":
        dlg.setText("You can stop the work.")
    elif str_class == "not the same device":
        dlg.setText("Please connect the same device!")

    dlg.setIcon(QMessageBox.Information)
    button = dlg.exec()
    if button == QMessageBox.Ok:
        print("OK!")


def isConnectingDevice():  # 判斷是否有接設備
    try:
        process = subprocess.Popen(['adb', 'devices'], stdout=subprocess.PIPE)
        process.stdout.readline().decode('utf-8').strip('\r\n')
        line2 = process.stdout.readline().decode('utf-8').strip('\r\n')
        if line2 == '':  # 如果第二行為空，代表沒有接設備
            isConnect = False
        else:
            isConnect = True
        return isConnect
    except Exception as e:
        print(e)
        return False


def resource_path():  # 判斷是否是執行檔
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    screen = app.primaryScreen()
    window = StartWindow()
    window.show()
    sys.exit(app.exec_())

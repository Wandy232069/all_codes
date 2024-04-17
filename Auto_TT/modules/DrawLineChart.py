import os
import csv
import sys

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference, series


def draw_line_chart(file, system, column_num=10):
    """
    # make a xlsx file with a line chart
    Args:
        file: str : file path for the data source csv
        system: CPU / MEM or DISK
        column_num: the column number which will be used in linechart data, default 10
    """
    work_book = Workbook()
    work_sheet = work_book.active
    if not os.path.isfile(file):
        print(f"{file} does not exist!!")
    try:
        # Read data from csv, write to xlsx
        with open(file, newline="") as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                # 將每個單元格中的數據轉換為數字
                row_data = []
                for cell in row:
                    try:
                        row_data.append(float(cell))
                    except:
                        row_data.append(cell)
                work_sheet.append(row_data)

        filename = file.replace(".csv", ".xlsx")
        # Open xlsx file, get columns and rows
        with open(file, newline="") as csvfile:
            rows = csv.reader(csvfile)
            headers = next(rows)
            columns_number = min(len(headers) - 1, column_num)
            rows_number = sum(1 for row in csvfile) + 1

        # 建立折線圖
        chart = LineChart()
        chart.title = system + " used"
        chart.style = 12
        chart.y_axis.title = "Ratio %"
        chart.x_axis.title = "Time"

        # 參照值
        data = Reference(work_sheet, min_col=2, min_row=1, max_col=columns_number, max_row=rows_number)
        x_axis = Reference(work_sheet, min_col=1, min_row=2, max_row=rows_number)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(x_axis)

        # 設定第 1 條線的樣式
        s1 = chart.series[0]
        s1.graphicalProperties.line.solidFill = "3a9ef2"  # 外框線條顏色

        # 將圖形放置在 A9 儲存格位置
        work_sheet.add_chart(chart, "G1")

        # 儲存 Excel 檔案
        work_book.save(filename)
    except Exception:
        print(sys.exc_info())

import re
import threading
import time
from serial.tools import list_ports
import serial

BAUD_RATE = 115200


class QNXlogger(object):
    flag = True

    def __init__(self, sn=None):
        self.test_data = None
        for port in list_ports.comports():
            print(f"{port}, pid :{port.pid}, vid :{port.vid},  SN :{port.serial_number}, hwid :{port.hwid}")
        if sn:
            qnx_port_list = list(port.device for port in list_ports.comports() if sn in port.serial_number)
        else:
            qnx_port_list = list(
                port.device for port in list_ports.comports() if re.match("N[0-9]+[A-Z 0-9]+B", port.serial_number))
        print(qnx_port_list)
        if len(qnx_port_list) == 0:
            print("No device com port found")
            return
        elif len(qnx_port_list) > 1:
            print("Port found >1, use first port as default")
            qnx_port = qnx_port_list[0]
        else:
            qnx_port = qnx_port_list[0]

        self.serial_connection = serial.Serial(port=qnx_port, baudrate=BAUD_RATE, timeout=0.5)

    def start_log(self, timeout=None):

        print(timeout)
        qnx_log_thread = threading.Thread(target=self.read_lines, args=(self.serial_connection,))
        qnx_log_thread.start()
        if timeout:
            timer_thread = threading.Thread(target=self.timeout_controller, args=[timeout])
            timer_thread.start()

    def timeout_controller(self, timeout):
        for i in range(timeout):
            print(i)
            time.sleep(1)
        self.flag = False

    def read_lines(self, port: serial.Serial):
        port.write(bytes("\03", 'utf-8'))
        port.write(bytes("slog2info -w\n", 'utf-8'))
        self.test_data = str()
        while self.flag:
            if not self.flag:
                break
            log_data = port.readline().decode('UTF-8')
            self.test_data += log_data
        port.write(bytes("\03", 'utf-8'))
        port.close()


if __name__ == '__main__':
    qnx_logger = QNXlogger()
    qnx_logger.start_log()
    for i in range(5):
        print(i)
        time.sleep(1)
    qnx_logger.flag = False
    data = qnx_logger.test_data
    print(data)
    with open("output.log", mode='w') as file:
        file.writelines(data)

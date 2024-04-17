import time
from serial.tools import list_ports
import serial
import pyhid_usb_relay


class UsbRelay(object):
    def __init__(self, connect_type, baud_rate=9600):
        self.baud_rate = baud_rate
        self.connect_type = connect_type
        if connect_type == "COM":
            com_port_list = list_ports.comports()
            com_port = ""
            for port in com_port_list:
                if "CH340" in port.description:
                    com_port = port.device
            self.connection = serial.Serial(com_port, self.baud_rate, timeout=0.5)
        else:
            self.relay = pyhid_usb_relay.find()

    def open(self, port):
        if self.connect_type == "COM":
            if port == 1:
                self.connection.write(bytes.fromhex('A0 01 01 A2'))
            elif port == 2:
                self.connection.write(bytes.fromhex('A0 02 01 A3'))
        else:
            if not self.relay.get_state(port):
                self.relay.toggle_state(port)

    def close(self, port):
        if self.connect_type == "COM":
            if port == 1:
                self.connection.write(bytes.fromhex('A0 01 00 A1'))
            elif port == 2:
                self.connection.write(bytes.fromhex('A0 02 00 A2'))
        else:
            if self.relay.get_state(port):
                self.relay.toggle_state(port)


if __name__ == "__main__":
    relay_2 = UsbRelay("COM")
    for i in range(2):
        relay_2.open(1)
        time.sleep(0.2)
        relay_2.open(2)
        time.sleep(0.5)
        relay_2.close(1)
        time.sleep(0.2)
        relay_2.close(2)
        time.sleep(0.5)

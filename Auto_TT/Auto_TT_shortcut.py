import json
import os
import sys
import time
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow

from LDAP_Tool import ldap_authenticator

import Login_ui


def resource_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path)


FILE_NAME = resource_path() + os.sep + ".info.json"


class LoginPage(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.second_window = None
        self.ui = Login_ui.Ui_Login_Window()
        self.ui.setupUi(self)
        self.setup_button_event()

    def setup_button_event(self):
        self.ui.buttonBox.accepted.connect(self.on_confirm_button_click)
        self.ui.buttonBox.rejected.connect(self.on_cancel_button_click)

    def on_confirm_button_click(self):
        if self.ui.AOSP_Selector.isChecked():
            print("AOSP")
            self.trigger_target("AOSP")
        elif self.ui.Vera_Selector.isChecked():
            print("Vera")
            self.trigger_target("Vera")
        elif self.ui.PDU_Selector.isChecked():
            print("PDU")
            self.trigger_target("PDU")

    def on_cancel_button_click(self):
        self.destroy()
        sys.exit()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        # print(a0.key())
        if a0.key() == 16777220:
            self.on_confirm_button_click()

    def trigger_target(self, system):
        print(system)
        upper_folder_abs_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + os.sep
        print(upper_folder_abs_path)
        if system == "AOSP":
            self.close()
            from SAW_TT import SAW_TT_Qt
            SAW_TT_Qt.get_config_data()
            self.second_window = SAW_TT_Qt.SAWui()
            self.second_window.modify_tester_name(self.ui.Account_TextEdit.text())
            self.second_window.base_form.show()

        elif system == "Vera":
            self.close()
            from Vera_TT import Vera_TT_Qt
            Vera_TT_Qt.get_config_data()
            self.second_window = Vera_TT_Qt.VeraUI()
            self.second_window.modify_tester_name(self.ui.Account_TextEdit.text())
            self.second_window.base_form.show()

        elif system == "PDU":
            self.close()
            from PDU_TT import PDU_TT_Qt
            PDU_TT_Qt.get_config_data()
            self.second_window = PDU_TT_Qt.PDUui()
            self.second_window.modify_tester_name(self.ui.Account_TextEdit.text())
            self.second_window.base_form.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = LoginPage()
    if os.path.isfile(FILE_NAME):
        with open(FILE_NAME, "r") as json_file:
            account_name = json.load(json_file)["account"]
            widget.ui.Account_TextEdit.setText(account_name)
            widget.ui.Remember_me_checkbox.setChecked(True)
    widget.show()

    sys.exit(app.exec_())

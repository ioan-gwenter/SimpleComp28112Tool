import sys
import time
import im
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QPlainTextEdit, QLineEdit, QLabel, QHBoxLayout
from PyQt6.QtCore import QObject, pyqtSignal, Qt

# input your URL here
URL = ""

class ServerPollingThread(QObject):
    keys_updated = pyqtSignal(set)

    def __init__(self):
        super().__init__()
        self.server = im.IMServerProxy(URL)

        self.current_keys = set()
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            keys = self.get_keys_from_server()
            if keys != self.current_keys:
                self.current_keys = keys
                self.keys_updated.emit(keys)
            time.sleep(3)

    def stop(self):
        self._stop_event.set()

    def get_keys_from_server(self):
        raw_keys = self.server.keys()
        key_string = []
        for key in raw_keys:
            processed_key = str(key.strip().decode("utf-8"))
            if processed_key == "":
                continue
            val = str(self.server.__getitem__(processed_key).strip().decode("utf-8"))
            key_string.append(f"{processed_key}: {val} ")
        return set(key_string)

    def clear_server(self):
        self.server.clear()

    def set_key_to_server(self,key,val):
        self.server.__setitem__(key,val)

    def del_key_on_server(self,key):
        self.server.__delitem__(key)


class TestingWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Server Testing Window")
        self.setGeometry(100, 100, 600, 400)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Key setting row
        key_setting_row = QWidget()
        key_setting_layout = QHBoxLayout(key_setting_row)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter Key")
        self.key_input.setStyleSheet("font-style: italic;")
        self.key_input.textChanged.connect(self.key_input_text_changed)
        key_setting_layout.addWidget(self.key_input)

        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter Value")
        self.value_input.setStyleSheet("font-style: italic;")
        self.value_input.textChanged.connect(self.value_input_text_changed)
        key_setting_layout.addWidget(self.value_input)

        set_key_button = QPushButton("Set Key")
        set_key_button.clicked.connect(self.set_key_clicked)
        key_setting_layout.addWidget(set_key_button)

        layout.addWidget(key_setting_row)

        # Del button row
        key_del_row = QWidget()
        key_del_layout = QHBoxLayout(key_del_row)

        self.del_input = QLineEdit()
        self.del_input.setPlaceholderText("Enter Key")
        self.del_input.setStyleSheet("font-style: italic;")
        self.del_input.textChanged.connect(self.del_input_text_changed)
        key_del_layout.addWidget(self.del_input)

        del_key_button = QPushButton("Delete Key")
        del_key_button.clicked.connect(self.del_key_clicked)
        key_del_layout.addWidget(del_key_button)

        layout.addWidget(key_del_row)

         # Button row
        button_row = QWidget()
        button_layout = QVBoxLayout(button_row)
        clear_keys_button = QPushButton("Clear Keys")
        clear_keys_button.clicked.connect(self.clear_keys_clicked)
        button_layout.addWidget(clear_keys_button)
        layout.addWidget(button_row)

        # Text log
        self.text_box = QPlainTextEdit()
        layout.addWidget(self.text_box)

        # Create polling thread
        self.polling_thread = ServerPollingThread()
        self.polling_thread.keys_updated.connect(self.update_text_box)
        self.polling_thread_thread = threading.Thread(target=self.polling_thread.run)
        self.polling_thread_thread.start()

    def await_text_box(self, keys):
        # Update the text box with the new list of keys
        self.text_box.clear()
        self.text_box.appendPlainText("Fetching Values...")


    def update_text_box(self, keys):
        # Update the text box with the new list of keys
        self.text_box.clear()
        for key in keys:
            self.text_box.appendPlainText(key)

    def clear_keys_clicked(self):
        # Stub method for Clear Keys button
        self.polling_thread.clear_server()

    def closeEvent(self, event):
        # Stop the polling thread when the window is closed
        self.polling_thread.stop()
        self.polling_thread_thread.join()
        event.accept()

    def key_input_text_changed(self, text):
        if text:
            self.key_input.setStyleSheet("")
        else:
            self.key_input.setStyleSheet("font-style: italic;")

    def value_input_text_changed(self, text):
        if text:
            self.value_input.setStyleSheet("")
        else:
            self.value_input.setStyleSheet("font-style: italic;")

    def del_input_text_changed(self, text):
        if text:
            self.del_input.setStyleSheet("")
        else:
            self.del_input.setStyleSheet("font-style: italic;")

    def set_key_clicked(self):

        key = self.key_input.text()
        value = self.value_input.text()
        self.polling_thread.set_key_to_server(key,value)
         

    def del_key_clicked(self):
        
        key = self.del_input.text()
        self.polling_thread.del_key_on_server(key)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestingWindow()
    window.show()
    sys.exit(app.exec())
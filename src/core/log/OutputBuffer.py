import sys
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal

from src.global_constants import LOG_IN_FILE, LOG_IN_SIGNAL
from .print_lib import clear_text


class OutputBuffer(QObject):
    widget_print = pyqtSignal(str)

    def __init__(self):
        super(OutputBuffer, self).__init__()
        self.console = sys.stdout

    def write(self, text):
        if LOG_IN_FILE:
            f = open(f"logs/{datetime.now():%d_%m_%Y log}.txt", "a")
            log_text = clear_text(text)
            f.write(log_text)
            f.close()

        self.console.write(text)
        self.console.flush()

        if LOG_IN_SIGNAL:
            self.widget_print.emit(text)

    def flush(self):
        self.console.flush()

    def reset(self):
        sys.stdout = self.console

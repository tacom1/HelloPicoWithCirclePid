from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QmlElement
import time

QML_IMPORT_NAME = "pyTools"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class HelloSpeedScripts(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_encode = -1
        self.last_time = -1
        self.speed_list = []

    @Slot(int)
    def appendRecord(self, value: int):
        if self.last_encode != -1:
            differ_value = value - self.last_encode
            differ_time = time.perf_counter() - self.last_time
            differ_speed = round((differ_value / 2400 * 0.8) / differ_time, 2)
            self.speed_list.append(differ_speed)

        self.last_encode = value
        self.last_time = time.perf_counter()

    @Slot(result=float)
    def getSpeed(self):
        if len(self.speed_list) > 5:
            self.speed_list = self.speed_list[-5:]
        if len(self.speed_list) == 0:
            return 0.00
        return round(sum(self.speed_list) / len(self.speed_list), 2)

# https://doc.qt.io/qtforpython-6/examples/example_serialport_terminal.html#example-serialport-terminal
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from PySide6.QtCore import QObject, Signal, Slot, QIODeviceBase
from PySide6.QtCore import QTimer


# Next is for debug
import random
import sys
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton


class Ch343Serial(QObject):
    errorOccurred = Signal(str)
    dataReceived = Signal(bytearray)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.serial = QSerialPort(self)
        self.serial.errorOccurred.connect(self._handle_serial_error)
        self.serial.readyRead.connect(self._read_serial_data)

    def open_ch343_device(self, device_name: str, baud_rate: int):
        port_name = None
        for each_port in QSerialPortInfo.availablePorts():
            if each_port.description() == device_name:
                port_name = each_port.portName()
                break
        if port_name is None:
            return False  # Not Found

        return self._open_serial_port(port_name, baud_rate)

    def close_serial_port(self):
        if self.serial.isOpen():
            self.serial.close()
        return True

    def write_byte_data(self, bytes_data: bytes):
        if self.serial.isOpen():
            self.serial.write(bytes_data)
            return True
        return False

    @Slot()
    def _read_serial_data(self):
        # PySide6.QtCore.QByteArray -> bytes | bytearray | memoryview
        serial_data = self.serial.readAll().data()
        self.dataReceived.emit(serial_data)

    @Slot(QSerialPort.SerialPortError)
    def _handle_serial_error(self, error):
        if error == QSerialPort.SerialPortError.NoError:
            return
        self.errorOccurred.emit(self.serial.errorString())

    def _open_serial_port(self, port_name: str, baud_rate: int):
        self.close_serial_port()

        # PySide6.QtSerialPort.QSerialPort(DataBits, ....) Define some const
        self.serial.setPortName(port_name)
        self.serial.setBaudRate(baud_rate)
        if self.serial.open(QIODeviceBase.OpenModeFlag.ReadWrite):
            return True
        return False

class HelloSerialPortConst:
    COMMAND_R00 = bytearray(b"R00")
    COMMAND_R01 = bytearray(b"R01")
    COMMAND_R02 = bytearray(b"R02")
    COMMAND_R03 = bytearray(b"R03")
    COMMAND_W01 = bytearray(b"W01")

    ACK_BYTE = 0x01
    DATA_BYTE = 0x02
    END_BYTE = 0x0A
    R_BYTE = 0x52
    W_BYTE = 0x57


class HelloSerialPort(QObject):
    responseACK = Signal(bytes, bool)  # command, is_ok
    responseData = Signal(bytes, bool, int)  # command, is_ok, data
    helloSerialError = Signal(str)  # some error info

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ch343 = Ch343Serial(parent)
        self.ch343.dataReceived.connect(self.receive_callback)
        self.ch343.errorOccurred.connect(self.handle_error)

        # Define some var
        self.command_list = [HelloSerialPortConst.COMMAND_W01, HelloSerialPortConst.COMMAND_R03,
                             HelloSerialPortConst.COMMAND_R02, HelloSerialPortConst.COMMAND_R01,
                             HelloSerialPortConst.COMMAND_R00]

        self.now_command = HelloSerialPortConst.COMMAND_R00
        self.now_byte_data = bytearray()

        self.command_queue = []
        self.command_consume_timer = QTimer(self)
        self.command_consume_timer.setInterval(200)  # 200ms
        self.command_consume_timer.timeout.connect(self._consume_command)
        self.command_consume_timer.start()


    def send_command(self, command: bytearray):
        if command[:3] in self.command_list:
            ms = 200 if command[0] == HelloSerialPortConst.R_BYTE else 500
            self.command_queue.append([command, ms])
            return
        self.handle_error("Command Not in Defined list")

    @Slot()
    def _consume_command(self):
        def send_byte_data():
            if not self.ch343.write_byte_data(bytes(self.now_command)):
                self.handle_error("Write Data to port error")

        # has command need to be sent in queue
        if len(self.command_queue) != 0:
            now_command_instance = self.command_queue[0]
            now_command_instance[1] -= 200
            if now_command_instance[1] <= 0:
                self.now_command = now_command_instance[0]
                self.command_queue.pop(0)
                send_byte_data()

    def receive_callback(self, data: bytearray):
        self.now_byte_data = data
        if (self.now_command == HelloSerialPortConst.COMMAND_R00 or
            self.now_command == HelloSerialPortConst.COMMAND_W01):
            true_response = bytearray([HelloSerialPortConst.ACK_BYTE, HelloSerialPortConst.END_BYTE])
            if self.now_byte_data == true_response:
                print("正确接收Command R00, W01")
                self.responseACK.emit(bytes(self.now_command), True)
            else:
                self.responseACK.emit(bytes(self.now_command), False)
        elif (self.now_command == HelloSerialPortConst.COMMAND_R01 or
              self.now_command == HelloSerialPortConst.COMMAND_R02 or
              self.now_command == HelloSerialPortConst.COMMAND_R03):
            if ((self.now_byte_data[0] == HelloSerialPortConst.DATA_BYTE)
                    and (self.now_byte_data[-1] == HelloSerialPortConst.END_BYTE)
                    and len(self.now_byte_data) > 2):
                print("读取数值: ", int(self.now_byte_data[1:-1]))
                self.responseData.emit(bytes(self.now_command), True, int(self.now_byte_data[1:-1]))
            else:
                self.responseData.emit(bytes(self.now_command), False, -1)
        else:
            print("Not Define Command, Skip Data")

    @Slot(str)
    def handle_error(self, error_msg: str):
        # Print to Console and send to signal, maybe show in ui
        print(error_msg)
        self.helloSerialError.emit(error_msg)

    def open(self, device_name: str, baud_rate: int = 115200):
        return self.ch343.open_ch343_device(device_name, baud_rate)

    def close(self):
        return self.ch343.close_serial_port()


if __name__ == '__main__':
    app = QApplication()

    p = HelloSerialPort(app)
    if not p.open("USB-Enhanced-SERIAL CH343"):
        print("无法打开串口通信设备")
        p.close()
        sys.exit(-1)

    def button_action(number: int):
        if number == 0:
            p.send_command(HelloSerialPortConst.COMMAND_R00)
        if number == 1:
            p.send_command(HelloSerialPortConst.COMMAND_R01)
        if number == 2:
            p.send_command(HelloSerialPortConst.COMMAND_R02)
        if number == 3:
            p.send_command(HelloSerialPortConst.COMMAND_R03)
        if number == 4:
            b = bytearray()
            b.extend(HelloSerialPortConst.COMMAND_W01)
            val = round(random.random() * 10 + 5, 2)
            b.extend(f" {val}".encode('utf-8'))
            p.send_command(b)


    widget = QWidget()
    layout = QVBoxLayout()
    for i in range(5):
        btn = QPushButton(f"按钮 {i}")
        btn.clicked.connect(lambda checked, x=i: button_action(x))
        layout.addWidget(btn)
    widget.setLayout(layout)
    widget.show()
    sys.exit(app.exec())
    # p.close()
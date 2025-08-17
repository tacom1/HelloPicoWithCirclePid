# https://doc.qt.io/qtforpython-6/examples/example_serialport_terminal.html#example-serialport-terminal
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtCore import QTimer
#from PySide6.QtQml import QmlElement
from .Ch343Serial import Ch343Serial
from .HelloSerialPortConst import HelloSerialPortConst

# Need to be single instance

class HelloSerialPort(QObject):
    responseACK = Signal(str, bool)  # command, is_ok
    responseData = Signal(str, bool, int)  # command, is_ok, data
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
            ms = 300 if command[0] == HelloSerialPortConst.R_BYTE else 600
            self.command_queue.append([command, ms])
            return
        self.handle_error("Command Not in Defined list")

    @Slot(str)
    def qml_send_command(self, command: str):
        self.send_command(command.encode('utf-8'))

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
        command = self.now_command[:3]
        if (command == HelloSerialPortConst.COMMAND_R00 or
            command == HelloSerialPortConst.COMMAND_W01):
            true_response = bytearray([HelloSerialPortConst.ACK_BYTE, HelloSerialPortConst.END_BYTE])
            if self.now_byte_data == true_response:
                self.responseACK.emit(command.decode('utf-8'), True)
            else:
                self.responseACK.emit(command.decode('utf-8'), False)
        elif (command == HelloSerialPortConst.COMMAND_R01 or
              command == HelloSerialPortConst.COMMAND_R02 or
              command == HelloSerialPortConst.COMMAND_R03):
            if ((self.now_byte_data[0] == HelloSerialPortConst.DATA_BYTE)
                    and (self.now_byte_data[-1] == HelloSerialPortConst.END_BYTE)
                    and len(self.now_byte_data) > 2):
                self.responseData.emit(command.decode('utf-8'), True, int(self.now_byte_data[1:-1]))
            else:
                self.responseData.emit(command.decode('utf-8'), False, -1)
        else:
            self.handle_error("Not Define Command, Skip Data")

    @Slot(str)
    def handle_error(self, error_msg: str):
        # Print to Console and send to signal, maybe show in ui
        self.helloSerialError.emit(error_msg)

    @Slot(str, int, result=bool)
    def open(self, device_name: str, baud_rate: int = 115200):
        return self.ch343.open_ch343_device(device_name, baud_rate)

    @Slot(result=bool)
    def close(self):
        return self.ch343.close_serial_port()

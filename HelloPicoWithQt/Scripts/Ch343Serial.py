# https://doc.qt.io/qtforpython-6/examples/example_serialport_terminal.html#example-serialport-terminal
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from PySide6.QtCore import QObject, Signal, Slot, QIODeviceBase

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

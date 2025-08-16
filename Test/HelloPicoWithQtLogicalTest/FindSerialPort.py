from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo

USB_SERIAL_NAME = "USB-Enhanced-SERIAL CH343"

for each_port in QSerialPortInfo.availablePorts():
    print(each_port.portName(),
          each_port.manufacturer(),
          each_port.serialNumber(),
          each_port.productIdentifier(),
          each_port.description())

    if each_port.description() == USB_SERIAL_NAME:
        print("Find", each_port.portName())
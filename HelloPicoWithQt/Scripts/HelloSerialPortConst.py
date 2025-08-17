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

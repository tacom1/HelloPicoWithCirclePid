from machine import UART, Pin, Timer
import time


"""HelloUART
Maybe has some dirty data in device cache, uart(like UDP) don't care
receiver will get data, we need set clean flag when next read seq start

To make communicate simpler, we define only host can send data to device,
only defined commands can be deeled.

Next command will supports:

Self Define Read Command(3-bytes):
    1. R00: Connect(Ask is Ok) / ACK
    2. R01: Read Encode / DATA
    3. R02: Read Left / DATA
    4. R03: Read Right / DATA

Self Define Write Command:
    1. W01: (3-bytes) | Data(4-bytes)  # W01 18.8

Self Define FallBack:
    -  ACK:  0x01 0x0A(\n)
    -  DATA: 0x02 | Data 0x0A(\n)

"""

uart0 = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
rx_buffer_command = bytearray()
rx_buffer_data = bytearray()
temp_byte_buffer = bytearray()
rx_tim = Timer()

def clean_buffer(clean_command, clean_data, clean_temp):
    global rx_buffer_command
    global rx_buffer_data
    if clean_command:
        rx_buffer_command[:] = b''
    if clean_data:
        rx_buffer_data[:] = b''
    if clean_temp:
        temp_byte_buffer[:] = b''

def read_uart_freq(timer):
    global uart0
    global rx_buffer_command
    global rx_buffer_data
    
    # read
    if uart0.any() > 0:
        b = uart0.read(1)
        if len(rx_buffer_command) < 3:
            if len(rx_buffer_command) == 0:
                if b != b'R' and b != b'W':
                    return # Dirty Data Drop
            rx_buffer_command.extend(b)
        elif bytes(rx_buffer_command) == b'W01':
            if len(rx_buffer_data) < 4 and b != b' ':  # blank key
                rx_buffer_data.extend(b)
        # else drop, until command be processed
    
rx_tim.init(freq=20, mode=Timer.PERIODIC, callback=read_uart_freq)

while True:
    ### simulate main loop process data ###
    if len(rx_buffer_command) == 3:
        if bytes(rx_buffer_command) == b'R00':
            uart0.write(bytes([0x01, 0x0A]))
            clean_buffer(True, False, False)
        elif bytes(rx_buffer_command) == b'R01':
            temp_byte_buffer.append(0x02)
            temp_byte_buffer.extend(str(3.14).encode('utf-8'))
            temp_byte_buffer.append(0x0A)
            uart0.write(bytes(temp_byte_buffer))
            clean_buffer(True, False, True)
        elif bytes(rx_buffer_command) == b'R02':
            temp_byte_buffer.append(0x02)
            temp_byte_buffer.extend(str(3.1415).encode('utf-8'))
            temp_byte_buffer.append(0x0A)
            uart0.write(bytes(temp_byte_buffer))
            clean_buffer(True, False, True)
        elif bytes(rx_buffer_command) == b'R03':
            temp_byte_buffer.append(0x02)
            temp_byte_buffer.extend(str(3.222).encode('utf-8'))
            temp_byte_buffer.append(0x0A)
            uart0.write(bytes(temp_byte_buffer))
            clean_buffer(True, False, True)
        elif bytes(rx_buffer_command) == b'W01':
            if len(rx_buffer_data) == 4:
                float_distance = float(bytes(rx_buffer_data))
                uart0.write(bytes([0x01, 0x0A]))
                print(float_distance)
                clean_buffer(True, True, False)
        
    time.sleep(0.05)
        
        

from machine import UART, Pin, Timer
import time


"""HelloUART
Maybe has some dirty data in device cache, uart(like UDP) don't care
receiver will get data, we need set clean flag when next read seq start

To make communicate simpler, we define only host can send data to device,
only defined commands can be deeled.

Next command will supports:

Self Define Read Command(3-bytes):
    1. M00: Connect(Ask is Ok) / ACK
    2. M01: Read Encode / DATA
    3. M02: Read Left / DATA
    4. M03: Read Right / DATA

Self Define Write Command:
    1. G01: (3-bytes) | Data(5-bytes)  # G01 18.8

Self Define FallBack:
    -  ACK:  0x01 0x0A(\n)
    -  DATA: 0x02 | Data 0x0A(\n)

"""

uart0 = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
rx_buffer_command = bytearray()
rx_buffer_data = bytearray()
rx_tim = Timer()

def clean_buffer(clean_command, clean_data):
    global rx_buffer_command
    global rx_buffer_data
    if clean_command:
        rx_buffer_command[:] = b''
    if clean_data:
        rx_buffer_data[:] = b''

def read_uart_freq(timer):
    global uart0
    global rx_buffer_command
    global rx_buffer_data
    
    # read
    if uart0.any() > 0:
        b = uart0.read(1)
        if len(rx_buffer_command) < 3:
            if len(rx_buffer_command) == 0:
                if b != b'M' and b != b'G':
                    return # Dirty Data Drop
            rx_buffer_command.extend(b)
        elif bytes(rx_buffer_command) == b'G01':
            if len(rx_buffer_data) < 4 and b != b' ':  # blank key
                rx_buffer_data.extend(b)
            #else:
                # else drop, until command be processed
                # print("Drop", b)
    
    ### simulate main loop process data ###
    if len(rx_buffer_command) == 3:
        if bytes(rx_buffer_command) == b'M00':
            uart0.write(bytes([0x01, 0x0A]))
        

rx_tim.init(freq=20, mode=Timer.PERIODIC, callback=read_uart_freq)

while True:
    time.sleep(0.1)
        
        

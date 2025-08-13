from machine import UART, Pin
import time


"""HelloUART
Maybe has some dirty data in device cache, uart(like UDP) don't care
receiver will get data, we need set clean flag when next read seq start

To make communicate simpler, we define only host can send data to device,
only defined commands can be deeled.

Next command will supports:

Self Define Read Command(3-bytes):
    1. M00: Connect / ACK
    2. M01: Read Encode / DATA
    3. M02: Read Left / DATA
    4. M03: Read Right / DATA

Self Define Write Command:
    1. G01: (3-bytes) | Data(half-float, 15bytes)

Self Define FallBack:
    -  ACK:  0x01
    -  DATA: 0x02 | Data(half-float, 15-bytes) 

"""
def uart_rx(uart):
    while uart.any():
        print(uart.read(1))

uart0 = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

rx = bytearray()
while True:
    # read
    if uart0.any() > 0:
        rx.append(uart0.read(3))
        s_rx = bytes(rx).decode('utf-8')
        
    else:
        time.sleep(0.1)
        
        

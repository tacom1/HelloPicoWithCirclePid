from machine import Pin
import time

encode_a = Pin(3, Pin.IN, Pin.PULL_UP)
encode_b = Pin(2, Pin.IN, Pin.PULL_UP)
encode_count = 0

def read_encode():
    global encode_count
    value_a = encode_a.value()
    value_b = encode_b.value()
    print(value_a, value_b)
    if value_a == 1:
        if value_b == 0:
            encode_count -= 1
        elif value_b == 1:
            encode_count += 1
        #print(encode_count)

encode_a.irq(lambda pin: read_encode(), Pin.IRQ_RISING)

while True:
    print("Running")
    time.sleep(1)  # 1s
from machine import Pin
import time

# def global var
# encode now value
encode_value = 0
last_a = 0
last_b = 0

# def pin number for each encode AB line
encode_a = 15
encode_b = 14

p_a = Pin(encode_a, Pin.IN)
p_b = Pin(encode_b, Pin.IN)

# def encode count function
def read_encode(a_v, b_v):
    global encode_value
    global last_a
    global last_b
    
    if a_v != last_a or b_v != last_b:
        if last_a == 0 and last_b == 0:
            if a_v == 0 and b_v == 1:
                encode_value -= 1
            if a_v == 1 and b_v == 0:
                encode_value += 1
        elif last_a == 0 and last_b == 1:
            if a_v == 1 and b_v == 1:
                encode_value -= 1
            if a_v == 0 and b_v == 0:
                encode_value += 1
        elif last_a == 1 and last_b == 1:
            if a_v == 1 and b_v == 0:
                encode_value -= 1
            if a_v == 0 and b_v == 1:
                encode_value += 1
        elif last_a == 1 and last_b == 0:
            if a_v == 0 and b_v == 0:
                encode_value -= 1
            if a_v == 1 and b_v == 1:
                encode_value += 1
                
        last_a = a_v
        last_b = b_v
        
p_a.irq(lambda pin: read_encode(p_a.value(), p_b.value()))
p_b.irq(lambda pin: read_encode(p_a.value(), p_b.value()))
        
        
# main loop
while True:
    print(encode_value)
    time.sleep(0.1)
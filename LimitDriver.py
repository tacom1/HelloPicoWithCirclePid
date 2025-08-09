from machine import Pin
import time

# define limit status
left_limit = 0
right_limit = 0

# define limit pin
left_limit_pin = 12
right_limit_pin = 13

left_pin = Pin(left_limit_pin, Pin.IN)
right_pin = Pin(right_limit_pin, Pin.IN)

# def help function
def read_limit(pin, is_left):
    global left_limit
    global right_limit
    
    is_rising = (pin.irq().flags() == Pin.IRQ_RISING)
    value = 0 if is_rising else 1  # normal hight, emit low
    if is_left:
        left_limit = value
        print("Left", value)
    else:
        right_limit = value
        print("Right", value)
        
left_pin.irq(lambda pin: read_limit(pin, True))
right_pin.irq(lambda pin: read_limit(pin, False))

#while True:
#    time.sleep(0.1)
    
from machine import Pin, PWM
import time

d = Pin(2, Pin.OUT, Pin.PULL_DOWN)
pwm = PWM(Pin(3))
pwm.freq(1600)
pwm.duty_u16(int(50 * 655.36))

loop = 1
while True:
    time.sleep(4)
    d.toggle()
    loop += 1
    print(loop)
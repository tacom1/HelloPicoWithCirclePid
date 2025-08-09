from machine import Pin, PWM
import time

# need pid alg
servo_dir_pin = 2
servo_pwm_pin = 3

# def same const
servo_running_duty = int(50 * 655.36)
servo_basic_pwm = 1600

# define pin
servo_dir = Pin(servo_dir_pin, Pin.OUT, Pin.PULL_DOWN)
servo_pwm = PWM(Pin(servo_pwm_pin))

# define help tools
def set_servo_stop():
    servo_pwm.duty_u16(0)

def set_servo_running(freq):
    global servo_basic_pwm
    global servo_running_duty
    if freq != -1:
        servo_pwm.freq(freq)
    else:
        servo_pwm.freq(servo_basic_pwm)
    servo_pwm.duty_u16(servo_running_duty)

set_servo_running(1600)
loop = 1
while True:
    time.sleep(2)
    servo_dir.toggle()
    loop += 1
    if loop > 5:
        set_servo_stop()
    print(loop)

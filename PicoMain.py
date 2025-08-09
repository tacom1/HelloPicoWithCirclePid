# pid realize
# https://gitee.com/skythinker/pid-simulator-web/blob/master/scripts/pid.js
# https://pid-simulator-web.skythinker.top/
from machine import Pin, PWM
import time

"""############# define basic pin value ##################"""
### Servo
servo_dir_pin = 2
servo_pwm_pin = 3

### Limit
right_limit_pin = 12
left_limit_pin = 13

### Encode
encode_a_pin = 15
encode_b_pin = 14

"""############# global define variable ##################"""
### Servo
servo_running_duty = int(50 * 655.36)
servo_basic_pwm = 1600
# 0: stop, 1: running, maybe a good way to confirm running status with encode value
servo_status = 0  

servo_dir = Pin(servo_dir_pin, Pin.OUT, Pin.PULL_DOWN)
servo_pwm = PWM(Pin(servo_pwm_pin))

### Encode
encode_value = 0
last_a = 0
last_b = 0

### Limit
left_limit = 0
right_limit = 0

### main
main_servo_rev = 1600  # 1600 / circle
main_encode_number = 2400  # 2400 high/low | circle (encode)
main_servo_rev_max = int(600 / 60 * main_servo_rev / 2)  # max 600 circle / minute, / 2 is for safe
main_circle_distance = 0.8 # 0.8mm / circle
main_aligned_first = True
main_left_encode_number = 0
main_right_encode_number = 0
main_phycial_distance = 0.0  # (right - left) / encode * circle_distance


"""############# define help function ##################"""
### Servo
def set_servo_dir(value):
    servo_dir.value(value)
    
def set_servo_stop():
    global servo_status
    servo_status = 0
    servo_pwm.duty_u16(0)

def set_servo_running(freq):
    global servo_basic_pwm
    global servo_running_duty
    global servo_status
    
    servo_status = 1
    if freq != -1:
        if freq > main_servo_rev_max:
            freq = main_servo_rev_max
        freq = int(freq)
        servo_pwm.freq(freq)
    else:
        servo_pwm.freq(servo_basic_pwm)
    servo_pwm.duty_u16(servo_running_duty)
    
### Encode
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

### Limit
def read_limit(pin, is_left):
    global left_limit
    global right_limit
    
    #is_rising = (pin.irq().flags() == Pin.IRQ_RISING)
    #value = 0 if is_rising else 1  # normal hight, emit low
    value = 0 if pin.value() == 1 else 1
    if is_left:
        left_limit = value
        #print("Left Limit", value)
    else:
        right_limit = value
        #print("Right Limit", value)
        
def read_limit_loop():
    # bad signal design, use next to decrease some bugs
    read_limit(left_pin, True)
    read_limit(right_pin, False)
        

"""############# Basic Init Pin ##################"""
### Encode
p_a = Pin(encode_a_pin, Pin.IN)
p_b = Pin(encode_b_pin, Pin.IN)
p_a.irq(lambda pin: read_encode(p_a.value(), p_b.value()))
p_b.irq(lambda pin: read_encode(p_a.value(), p_b.value()))

### Limit
left_pin = Pin(left_limit_pin, Pin.IN)
right_pin = Pin(right_limit_pin, Pin.IN)
left_pin.irq(lambda pin: read_limit(pin, True))
right_pin.irq(lambda pin: read_limit(pin, False))


"""############# Now Define main loop ##################"""
def find_encode_align():
    global left_limit
    global right_limit
    global encode_value
    
    global main_servo_rev
    global main_aligned_first
    global main_encode_number
    global main_circle_distance
    global main_left_encode_number
    global main_right_encode_number
    global main_phycial_distance
    
    # first we need get length of the servo move range
    if main_aligned_first:
        # move right some distance, then find left limit location
        set_servo_dir(0)
        set_servo_running(main_servo_rev * 0.2)
        time.sleep(3)
        set_servo_stop()
        
        # move left until find left limit
        set_servo_dir(1)
        set_servo_running(main_servo_rev * 4)
        left_limit = 0
        while True:
            if left_limit == 1:
                set_servo_stop()
                main_left_encode_number = encode_value
                print("Find Left Limit, Value:", encode_value)
                break
            read_limit_loop()
            time.sleep(0.01)
        
        # move right until fine right limit
        set_servo_dir(0)
        set_servo_running(main_servo_rev * 4)
        right_limit = 0
        while True:
            if right_limit == 1:
                set_servo_stop()
                main_right_encode_number = encode_value
                print("Find Right Limit, Value:", encode_value)
                break
            read_limit_loop()
            time.sleep(0.01)
        
        # set status
        main_aligned_first = False
        
        # calc distance for debug
        total_number = abs(main_right_encode_number - main_left_encode_number)
        main_phycial_distance = total_number / main_encode_number * main_circle_distance
        print("About Range(mm) is:", main_phycial_distance)


### Define basic pid alg
#pid_i = {
#    "kp": 0.0,
#    "ki": 0.0,
#    "kd": 0.0,
#    "maxInt": 0.0,
#    "maxOut": 0.0,
#    "error": 0.0,
#    "lastError": 0.0,
#    "integral": 0.0,
#    "output": 0.0
#}
pid_i = {}
pid_o = {}

def init_pid_d(pid_d, p, i, d, mi, mo):
    pid_d["kp"] = p
    pid_d["ki"] = i
    pid_d["kd"] = d
    pid_d["maxInt"] = mi
    pid_d["maxOut"] = mo
    pid_d["error"] = 0.0
    pid_d["lastError"] = 0.0
    pid_d["integral"] = 0.0
    pid_d["output"] = 0.0

def pid_limit(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value
    
def pid_calc(pid_d, ref, fdb):
    pid_d["lastError"] = pid_d["error"]
    pid_d["error"] = ref - fdb
    pErr = pid_d["error"] * pid_d["kp"]
    dErr = (pid_d["error"] - pid_d["lastError"]) * pid_d["kd"]
    pid_d["integral"] += pid_d["ki"] * pid_d["error"]
    pid_d["integral"] = pid_limit(pid_d["integral"], -pid_d["maxInt"], pid_d["maxInt"])
    sumErr = pErr + pid_d["integral"] + dErr
    pid_d["output"] = pid_limit(sumErr, -pid_d["maxOut"], pid_d["maxOut"])

def pid_clear(pid_d):
    pid_d["error"] = 0.0
    pid_d["lastError"] = 0.0
    pid_d["integral"] = 0.0
    pid_d["output"] = 0.0
    
def cascade_pid_init(value_a, value_b):
    global pid_i
    global pid_o
    init_pid_d(pid_i, value_a[0], value_a[1], value_a[2], value_a[3], value_a[4])
    init_pid_d(pid_o, value_b[0], value_b[1], value_b[2], value_b[3], value_b[4])
    
def cascade_pid_calc(out_ref, out_fdb, in_fdb):
    global pid_i
    global pid_o
    pid_calc(pid_o, out_ref, out_fdb)
    pid_calc(pid_i, pid_o["output"], in_fdb)
    
    return pid_i["output"]

def cascade_pid_clear():
    global pid_i
    global pid_o
    pid_clear(pid_o)
    pid_clear(pid_i)
    
def goto_location_with_cascade_pid(location):
    global main_phycial_distance
    global main_circle_distance
    global main_encode_number
    global main_left_encode_number
    global main_servo_rev
    
    global encode_value
    global pid_i
    global pid_o
    
    # skip condition
    if location < 0 or location > main_phycial_distance:
        print("Location Out Of Range, Skip...")
        return
    
    # distance to encode value
    dst_value = location / main_circle_distance * main_encode_number
    dst_value += main_left_encode_number
    print("Servo will move to:", dst_value)
    
    # loop until goto somewhere
    now_pwm = main_servo_rev
    while True:
        new_pwm = cascade_pid_calc(encode_value, dst_value, now_pwm)
        now_pwm = new_pwm
        if new_pwm > 0:
            set_servo_dir(0)
        else:
            set_servo_dir(1)
        new_pwm = abs(new_pwm)
        set_servo_running(new_pwm)
            
        time.sleep(0.1)
        differ = dst_value - encode_value
        print(pid_i["output"], pid_o["output"], differ)
        if abs(differ) < 300 or abs(now_pwm) < 20:  # 300 / 2400 * 0.8 = 0.1 mm
            break
    
    set_servo_stop()    
    

"""
We Define Something:
    set_servo_dir(0): move right
    set_servo_dir(1): move left
    
About Cascade Pid:
    out: encode distance
    in: pwm 
"""
value_i = [1.0, 0.0, 0.0, 0.0, main_servo_rev_max // 5]
value_o = [1.0, 0.0, 3.0, 0.0, 200.0]
cascade_pid_init(value_i, value_o)
first = True
while True:
    # improve some stablity
    read_limit_loop()
    
    # init(reset first)
    find_encode_align()
    
    # test cascade pid
    if first:
        goto_location_with_cascade_pid(main_phycial_distance / 2)
        first = False
    
    # loop
    #print(encode_value)
    time.sleep(1)
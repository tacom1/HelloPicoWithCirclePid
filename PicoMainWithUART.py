# pid realize
# https://gitee.com/skythinker/pid-simulator-web/blob/master/scripts/pid.js
# https://pid-simulator-web.skythinker.top/
# Code inherited From HelloUART.py and PicoMain.py
from machine import Pin, PWM, Timer, UART
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

### UART
uart0_tx_pin = 0
uart0_rx_pin = 1
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

### uart
rx_buffer_command = bytearray()
rx_buffer_data = bytearray()
temp_byte_buffer = bytearray()
rx_tim = Timer()
uart0 = UART(0, baudrate=115200, tx=Pin(uart0_tx_pin), rx=Pin(uart0_rx_pin))

### main
main_servo_rev = 1600  # 1600 / circle
main_encode_number = 2400  # 2400 high/low | circle (encode)
main_servo_rev_max = int(600 / 60 * main_servo_rev - 5)  # max 600 circle / minute, -3 is for safe
main_circle_distance = 0.8 # 0.8mm / circle
main_aligned_first = True
main_left_encode_number = 0
main_right_encode_number = 0
main_phycial_distance = 0.0  # (right - left) / encode * circle_distance
main_need_to_move_location = False
main_need_to_move_dst_value = 0.0

### Pid
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
now_pwm = 0
pid_tim = Timer()

"""############# define help function ##################"""
###### Servo 
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
    
###### Encode
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

###### Limit
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
    
###### uart
def clean_uart_buffer(clean_command, clean_data, clean_temp):
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

###### pid
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
    
def goto_location_with_cascade_pid(timer):
    global main_phycial_distance
    global main_circle_distance
    global main_encode_number
    global main_left_encode_number
    global main_need_to_move_location
    global main_need_to_move_dst_value
    # pid 
    global encode_value
    global pid_i
    global pid_o
    global now_pwm
    # for safe
    global left_limit
    global right_limit
    
    if not main_need_to_move_location:
        return
    
    differ_pwm = cascade_pid_calc(encode_value, main_need_to_move_dst_value, now_pwm)
    now_pwm += differ_pwm
    
    if now_pwm > 0:
        set_servo_dir(1)
    else:
        set_servo_dir(0)
        
    # for safe
    read_limit_loop()
    now_dir = 0 if differ_pwm < 0 else 1
    #print(now_dir)
    if right_limit == 0 and left_limit == 0:
        pass  # Normal
    elif right_limit == 1 and now_dir == 1:
        pass  # now in right, but goto left
    elif left_limit == 1 and now_dir == 0:
        pass  # not in left, but goto right
    else:
        print("Machine Has Some Problem, manually reset it Error")
        main_need_to_move_location = False
        set_servo_stop()
        cascade_pid_clear()
        return 
    
    if int(abs(now_pwm)) < 200:
        set_servo_running(200)
    else:
        set_servo_running(int(abs(now_pwm)))
    
    differ = main_need_to_move_dst_value - encode_value
    # differ_mm = differ / main_encode_number * main_circle_distance
    # print(differ)  # Debug
    
    if abs(differ) < 300:  # 300 / 2400 * 0.8 = 0.1 mm
        main_need_to_move_location = False
        set_servo_stop()
        cascade_pid_clear()
        
        
"""############# Basic Init Pin ##################"""
### Encode
p_a = Pin(encode_a_pin, Pin.IN)
p_b = Pin(encode_b_pin, Pin.IN)
p_a.irq(lambda pin: read_encode(p_a.value(), p_b.value()))
p_b.irq(lambda pin: read_encode(p_a.value(), p_b.value()))

### Limit
left_pin = Pin(left_limit_pin, Pin.IN)
right_pin = Pin(right_limit_pin, Pin.IN)
#left_pin.irq(lambda pin: read_limit(pin, True))
#right_pin.irq(lambda pin: read_limit(pin, False))

### UART
rx_tim.init(freq=20, mode=Timer.PERIODIC, callback=read_uart_freq)

### pid
pid_tim.init(freq=50, mode=Timer.PERIODIC, callback=goto_location_with_cascade_pid)

"""################# Main Loop ############################
We Define Something:
    set_servo_dir(0): move right
    set_servo_dir(1): move left
    
About Cascade Pid:
    out: encode distance
    in: pwm
    
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
"""#############################################
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
        set_servo_running(main_servo_rev * 0.5)
        time.sleep(2)
        set_servo_stop()
        
        # move left until find left limit
        set_servo_dir(1)
        set_servo_running(main_servo_rev * 4)
        left_limit = 0
        while True:
            if left_limit == 1:
                set_servo_stop()
                main_left_encode_number = encode_value
                print("Find Left Limit, Value:", main_left_encode_number)
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
                print("Find Right Limit, Value:", main_right_encode_number)
                break
            read_limit_loop()
            time.sleep(0.01)
        
        # set status
        main_aligned_first = False
        
        # calc distance for debug
        total_number = abs(main_right_encode_number - main_left_encode_number)
        main_phycial_distance = total_number / main_encode_number * main_circle_distance
        print("About Range(mm) is:", main_phycial_distance)

def goto_location(location):
    global main_need_to_move_location
    global main_need_to_move_dst_value
    global main_servo_rev
    global now_pwm
    
    # skip condition
    if location < 0 or location > main_phycial_distance:
        print("Location Out Of Range, Skip...")
        return
    
    # distance to encode value
    dst_value = location / main_circle_distance * main_encode_number
    dst_value += main_left_encode_number
    print("Servo will move to:", dst_value)
    
    # set status
    main_need_to_move_location = True
    main_need_to_move_dst_value = dst_value
    now_pwm = main_servo_rev

value_i = [1.0, 0.0, 0.0, 0.0, 400.0]
value_o = [1.0, 0.0, 3.0, 0.0, 6400.0]
cascade_pid_init(value_i, value_o)
first = True

while True:
    find_encode_align()
        
    ### simulate main loop process data ###
    if len(rx_buffer_command) == 3:
        if bytes(rx_buffer_command) == b'R00':
            uart0.write(bytes([0x01, 0x0A]))
            clean_uart_buffer(True, False, False)
        elif bytes(rx_buffer_command) == b'R01':
            temp_byte_buffer.append(0x02)
            temp_byte_buffer.extend(str(encode_value).encode('utf-8'))
            temp_byte_buffer.append(0x0A)
            uart0.write(bytes(temp_byte_buffer))
            clean_uart_buffer(True, False, True)
        elif bytes(rx_buffer_command) == b'R02':
            temp_byte_buffer.append(0x02)
            temp_byte_buffer.extend(str(main_left_encode_number).encode('utf-8'))
            temp_byte_buffer.append(0x0A)
            uart0.write(bytes(temp_byte_buffer))
            clean_uart_buffer(True, False, True)
        elif bytes(rx_buffer_command) == b'R03':
            temp_byte_buffer.append(0x02)
            temp_byte_buffer.extend(str(main_right_encode_number).encode('utf-8'))
            temp_byte_buffer.append(0x0A)
            uart0.write(bytes(temp_byte_buffer))
            clean_uart_buffer(True, False, True)
        elif bytes(rx_buffer_command) == b'W01':
            if len(rx_buffer_data) == 4:
                uart0.write(bytes([0x01, 0x0A]))
                float_distance = float(bytes(rx_buffer_data))
                goto_location(float_distance)
                clean_uart_buffer(True, True, False)
        else:
            # Not Define Command, cleaned
            clean_uart_buffer(True, False, False)
        
    time.sleep(0.02)


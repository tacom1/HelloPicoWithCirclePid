import machine
import utime

adc = machine.ADC(26)
fac = 3.3 / (65535)

while True:
    t = adc.read_u16() * fac
    print(t)
    utime.sleep(0.1)
    
    
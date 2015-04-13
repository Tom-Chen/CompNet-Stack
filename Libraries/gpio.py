import time
import RPi.GPIO as GPIO

def blink(tuple, pin, speed=200):
    if(tuple[0] == 1):
        turn_high(pin)
    else:
        turn_low(pin)
    time.sleep((tuple[1]) / speed)

def prepare_pin_out(pin):
    GPIO.setmode(GPIO.BCM)  #use Broadcom (BCM) GPIO numbers on breakout pcb
    
    GPIO.setup(pin,GPIO.OUT) # allow pi to set 3.3v and 0v levels

def prepare_pin_in(pin):
    GPIO.setmode(GPIO.BCM)  #use Broadcom (BCM) GPIO numbers on breakout pcb
    
    GPIO.setup(pin,GPIO.IN) # allow pi to set 3.3v and 0v levels

def read_pin(pin):
    return GPIO.input(pin)  # set 3.3V level on GPIO output

def turn_high(pin):
    GPIO.output(pin,GPIO.HIGH)  # set 3.3V level on GPIO output

def turn_low(pin):
    GPIO.output(pin,GPIO.LOW)   # set ground (0) level on GPIO output

def add_event_detect(pin,cbfunc):
    GPIO.add_event_detect(pin,GPIO.BOTH,callback=cbfunc)

def cleanup():
    GPIO.cleanup()

class Safeguards:
    def __enter__(self):
        return self
    def __exit__(self,*rabc):
        GPIO.cleanup()
        print("Safe exit succeeded")
        return not any(rabc)
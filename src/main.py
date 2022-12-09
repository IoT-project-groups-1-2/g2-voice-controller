import utime
from machine import Pin

# Defining main function
def setup():
    led = Pin(2, Pin.OUT)
    piezo = Pin(0, Pin.OUT)
    speaker = Pin(0, Pin.OUT)
    shuffle_btn = Pin(1, Pin.IN)
    c_btn = Pin(16, Pin.IN)
    g_btn = Pin(22, Pin.IN)
    am_btn = Pin(27, Pin.IN)
    f_btn = Pin(28, Pin.IN)
    oct_up = Pin(18, Pin.IN)
    #wrong?
    oct_down = Pin(18, Pin.IN)
def loop():
    while True:
        pass
        


# Using the special variable
# __name__
if __name__ == "__main__":
    setup()
    loop()
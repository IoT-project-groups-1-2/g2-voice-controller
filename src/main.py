import utime
from machine import Pin, PWM
from time import sleep_ms
from rtttl import RTTTL

led = Pin(2, Pin.OUT)
shuffle_btn = Pin(1, Pin.IN)
c_btn = Pin(16, Pin.IN)
g_btn = Pin(22, Pin.IN)
am_btn = Pin(27, Pin.IN)
f_btn = Pin(28, Pin.IN)
oct_up = Pin(18, Pin.IN, Pin.PULL_DOWN)
oct_down = Pin(20, Pin.IN)
speaker = PWM(Pin(0))

NvrGonna = 'NvrGonna:d=4,o=5,b=200:8g,8a,8c6,8a,e6,8p,e6,8p,d6.,p,8p,8g,8a,8c6,8a,d6,8p,d6,8p,c6,8b,a.,8g,8a,8c6,8a,2c6,d6,b,a,g.,8p,g,2d6,2c6.,p,8g,8a,8c6,8a,e6,8p,e6,8p,d6.,p,8p,8g,8a,8c6,8a,2g6,b,c6.,8b,a,8g,8a,8c6,8a,2c6,d6,b,a,g.,8p,g,2d6,2c6.'
tom = "tom:d=16,o=6,b=95:32d,32d_,32d,32d_,32d,32d_,32d,32d_,32d,32d,32d_,32e,32f,32f_,32g,g,8p,g,8p,a_,p,c7,p,g,8p,g,8p,f,p,f_,p,g,8p,g,8p,a_,p,c7,p,g,8p,g,8p,f,p,f_,p,a_,g,2d,32p,a_,g,2c_,32p,a_,g,2c,a_5,8c,2p,32p,a_5,g5,2f_,32p,a_5,g5,2f,32p,a_5,g5,2e,d_,8d"


    
test = "PacMan:d=4,o=5,b=125:8d7,8d7,8d7,8d6,8d7,8d7,8d7,8d6,2d#7,8d7,p,32p,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,16b6,16c7,b6,8a6,8d6,8a6,8a6,8a6,8d6,8a6,8a6,8a6,8d6,8a6,8a6,8a6,16a6,16b6,a6,8g6,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,16a6,16b6,c7,e7,8d7,8d7,8d7,8d6,8c7,8c7,8c7,8f#6,2g6";
song = "20thCenFox:d=4,o=4,b=160:8f#5,8f#5,8f#5,8d5,8p,8b,8p,8e5,8p,8e5,8p,8e5,8g#5,8g#5,8a5,8b5,8a5,8a5,8a5,8e5,8p,8d5,8p,8f#5,8p,8f#5,8p,8f#5,8e5,8e5,8f#5,8e5,8f#5,8f#5,8f#5,8d5,8p,8b,8p,8e5,8p,8e5,8p,8e5,8g#5,8g#5,8a5,8b5,8a5,8a5,8a5,8e5,8p,8d5,8p,8f#5,8p,8f#5,8p,8f#5,8e5,8e5"
def play_tone(freq, msec):
    if freq > 0:
        speaker.freq(int(freq))       # Set frequency
        speaker.duty_u16(32768)       # 50% duty cycle
    sleep_ms(int(0.9 * msec))     # Play for a number of msec
    speaker.duty_u16(0)               # Stop playing for gap between notes
    sleep_ms(int(0.1 * msec))     # Pause for a number of msec

#assign tune can be placed in a loop to make it play eternally


tune = RTTTL(song)
# Defining main function
def loop():
    while True:
        led.value(1)
        for freq, msec in tune.notes():
            play_tone(freq, msec)
        



if __name__ == "__main__":
    loop()
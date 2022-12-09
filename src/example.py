# Raspberry Pi Pico RTTTL example
# scruss - 2021-02: sorry, not sorry ...
from rtttl import RTTTL
from time import sleep_ms
from machine import Pin, PWM

# nicked from https://gist.github.com/mhungerford/0af269ee46c0d44a813c
NvrGonna = 'NvrGonna:d=4,o=5,b=200:8g,8a,8c6,8a,e6,8p,e6,8p,d6.,p,8p,8g,8a,8c6,8a,d6,8p,d6,8p,c6,8b,a.,8g,8a,8c6,8a,2c6,d6,b,a,g.,8p,g,2d6,2c6.,p,8g,8a,8c6,8a,e6,8p,e6,8p,d6.,p,8p,8g,8a,8c6,8a,2g6,b,c6.,8b,a,8g,8a,8c6,8a,2c6,d6,b,a,g.,8p,g,2d6,2c6.'
tom = "tom:d=16,o=6,b=95:32d,32d_,32d,32d_,32d,32d_,32d,32d_,32d,32d,32d_,32e,32f,32f_,32g,g,8p,g,8p,a_,p,c7,p,g,8p,g,8p,f,p,f_,p,g,8p,g,8p,a_,p,c7,p,g,8p,g,8p,f,p,f_,p,a_,g,2d,32p,a_,g,2c_,32p,a_,g,2c,a_5,8c,2p,32p,a_5,g5,2f_,32p,a_5,g5,2f,32p,a_5,g5,2e,d_,8d"
# pin 26 - GP20; just the right distance from GND at pin 23
#  to use one of those PC beepers with the 4-pin headers
pwm = PWM(Pin(0))
    
test = "PacMan:d=4,o=5,b=125:8d7,8d7,8d7,8d6,8d7,8d7,8d7,8d6,2d#7,8d7,p,32p,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,16b6,16c7,b6,8a6,8d6,8a6,8a6,8a6,8d6,8a6,8a6,8a6,8d6,8a6,8a6,8a6,16a6,16b6,a6,8g6,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,16a6,16b6,c7,e7,8d7,8d7,8d7,8d6,8c7,8c7,8c7,8f#6,2g6";
song = "20thCenFox:d=16,o=5,b=140:b,8p,b,b,2b,p,c6,32p,b,32p,c6,32p,b,32p,c6,32p,b,8p,b,b,b,32p,b,32p,b,32p,b,32p,b,32p,b,32p,b,32p,g#,32p,a,32p,b,8p,b,b,2b,4p,8e,8g#,8b,1c#6,8f#,8a,8c#6,1e6,8a,8c#6,8e6,1e6,8b,8g#,8a,2b"
def play_tone(freq, msec):
    # print('freq = {:6.1f} msec = {:6.1f}'.format(freq, msec))
    if freq > 0:
        pwm.freq(int(freq))       # Set frequency
        pwm.duty_u16(32767)       # 50% duty cycle
    sleep_ms(int(0.9 * msec))     # Play for a number of msec
    pwm.duty_u16(0)               # Stop playing for gap between notes
    sleep_ms(int(0.1 * msec))     # Pause for a number of msec


tune = RTTTL(tom)
for freq, msec in tune.notes():
    play_tone(freq, msec)
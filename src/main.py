from machine import Pin, PWM, I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from time import sleep_ms
from rtttl import RTTTL
import network
import urequests
import random
import credentials as creds
from umqtt.simple import MQTTClient

def irqHandler(pin):
    speaker.deinit()


"""
Pins configs
"""
led = Pin(6, Pin.OUT)
shuffle_btn = Pin(1, Pin.IN, Pin.PULL_UP)
shuffle_btn.irq(trigger=Pin.IRQ_RISING, handler=irqHandler)

c_btn = Pin(2, Pin.IN)
g_btn = Pin(3, Pin.IN)
am_btn = Pin(4, Pin.IN)
f_btn = Pin(5, Pin.IN)
oct_up = Pin(18, Pin.IN)
oct_down = Pin(20, Pin.IN)
speaker = PWM(Pin(0))




"""
I2C LCD CONFIG
"""
I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
sdaPIN = Pin(16)
sclPIN = Pin(17)
i2c = I2C(0, sda = sdaPIN, scl = sclPIN, freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)    
lcd.putstr("Initializing...")


"""
Network config
"""
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(creds.ssid, creds.password)
print('Wifi connected', wlan.isconnected())

def fetch_playlist():
    res = urequests.get("http://192.168.121.235:3000/api/songs").json()
    return res
    

mqtt_server = 'broker.hivemq.com'
client_id = 'PicoW'
user_t = creds.mqtt_usr
password_t = creds.mqtt_password
topic_pub = 'songs'

last_message = 0
message_interval = 5
counter = 0

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    
    return client



def play_tone(freq, msec):
    if freq > 0:
        speaker.freq(int(freq))       # Set frequency
        speaker.duty_u16(32768)       # 50% duty cycle
    sleep_ms(int(0.9 * msec))     # Play for a number of msec
    speaker.duty_u16(0)               # Stop playing for gap between notes
    sleep_ms(int(0.1 * msec))     # Pause for a number of msec



# Defining main function
def loop():
    shuffle_btn.irq(trigger=Pin.IRQ_FALLING, handler=irqHandler)
    playlist = fetch_playlist()
    nr_of_songs = len(playlist)
    client = mqtt_connect()
    while True: 
        rand_index = random.choice(range(0, nr_of_songs - 1))
        lcd.clear()
        lcd.putstr(playlist[rand_index]["Name"])
        client.publish(topic_pub, "Playing " + playlist[rand_index]["Name"])
        tune = RTTTL(playlist[rand_index]["rtttl"])
        led.value(1)
        for freq, msec in tune.notes():
            play_tone(freq, msec)
        led.value(0)
        lcd.clear()
        sleep_ms(3000)



if __name__ == "__main__":
    loop()
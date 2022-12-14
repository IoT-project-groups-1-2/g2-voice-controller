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
import _thread
import json




"""
Pins configs
"""
led = Pin(6, Pin.OUT)
shuffle_btn = Pin(1, Pin.IN, Pin.PULL_UP)
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


mqtt_server = 'broker.hivemq.com'
client_id = 'PicoW'
topic_pub = 'rtttl/dtw'
topic_sub = 'rtttl/wtd'

current_track = None;

lock = _thread.allocate_lock()


def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, user=creds.mqtt_usr, password=creds.mqtt_password, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client


def mqtt_cb(topic, msg):
    print("Received {} from topic {}".format(str(msg, "UTF-8"), str(topic, "UTF-8")))
    global current_track
    current_track = json.loads(msg)




def fetch_playlist():
    res = urequests.get("http://192.168.121.69:3000/api/songs").json()
    return res





def play_tone(freq, msec):
    if freq > 0:
        speaker.freq(int(freq))       # Set frequency
        speaker.duty_u16(32768)       # 50% duty cycle
    sleep_ms(int(0.9 * msec))     # Play for a number of msec
    speaker.duty_u16(0)               # Stop playing for gap between notes
    sleep_ms(int(0.1 * msec))     # Pause for a number of msec



playlist = fetch_playlist()
nr_of_songs = len(playlist)
client = mqtt_connect()


def mqttTask():
    client.set_callback(mqtt_cb)
    client.subscribe(topic_sub)
    while True:	
        lock.acquire()
        lcd.clear()
        lcd.putstr("Play a song on me")
        client.check_msg()
        print("WAITING AGAIN :(")
        lock.release()
        
_thread.start_new_thread(mqttTask, ())
    

# Defining main function
def loop():
    while True:
        lock.acquire()
        global current_track
        if current_track is not None:
            print("HEH")
            lcd.putstr(current_track["Name"])
            playTrack(current_track)
        current_track = None;
        lock.release()
        
def playTrack(track_json):
    lcd.clear()
    lcd.putstr(track_json["Name"])
    client.publish(topic_pub, "Playing " + track_json["Name"])
    tune = RTTTL(track_json["rtttl"])
    led.value(1)
    for freq, msec in tune.notes():
        play_tone(freq, msec)
    led.value(0)



if __name__ == "__main__":
    loop()
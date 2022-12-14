from machine import Pin, PWM, I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from time import sleep_ms
from rtttl import RTTTL
import network
import urequests
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


"""
MQTT CONFIGS
"""
mqtt_server = 'broker.hivemq.com'
client_id = 'PicoW'
topic_pub = 'rtttl/dtw'
topic_sub = 'rtttl/wtd'


current_track = None;
lock = _thread.allocate_lock()


def wifi_connect():
    """
    Connect to wifi based on provided credentials, results will be shown on LCD screeen
    """
    lcd.putstr("Connecting to Wifi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(creds.ssid, creds.password)
    lcd.clear()
    lcd.putstr("Connected!!" if wlan.isconnected() else "Failed to connect to Wifi!!")



def mqtt_connect():
    """
    Connect to HiveMQ MQTT Server

    Returns:
        client (MQTTClient): MQTT Client Object
    """
    client = MQTTClient(client_id, mqtt_server, user=creds.mqtt_usr, password=creds.mqtt_password, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client


def mqtt_cb(topic, msg):
    """
    MQTT Callback function, called when a message is received from a subscribed topic

    Args:
        topic (str): Topic to which the message was sent
        msg (byte): Message in byte format. Can be converted to string: str(msg, 'UTF-8')
    """
    print("Received {} from topic {}".format(str(msg, "UTF-8"), str(topic, "UTF-8")))
    global current_track
    current_track = json.loads(msg)



def fetch_playlist():
    """
    Fetching playlist from the server

    Returns:
        res (dict): Returns a dictionary containing songs
    """
    res = urequests.get("http://192.168.121.69:3000/api/songs").json()
    return res



def play_tone(freq, msec):
    """
    Playing a single tone
    """
    if freq > 0:
        speaker.freq(int(freq))       # Set frequency
        speaker.duty_u16(32768)       # 50% duty cycle
    sleep_ms(int(0.9 * msec))     # Play for a number of msec
    speaker.duty_u16(0)               # Stop playing for gap between notes
    sleep_ms(int(0.1 * msec))     # Pause for a number of msec


wifi_connect()
playlist = fetch_playlist()
nr_of_songs = len(playlist)
client = mqtt_connect()


def mqttTask():
    """
    MQTT task, checking message from server and display necessary information to LCD
    """
    client.set_callback(mqtt_cb)
    client.subscribe(topic_sub)
    while True:	
        lock.acquire()
        lcd.clear()
        lcd.putstr("Waiting for commands")
        print("Checking message in queue")
        client.check_msg()
        lock.release()
        
#Starting MQTT task on 2nd thread
_thread.start_new_thread(mqttTask, ())
    


def loop():
    """
    Main task, checking if a track is on queue, play track and display information
    """
    while True:
        lock.acquire()
        global current_track
        if current_track is not None:
            lcd.putstr(current_track["Name"])
            client.publish(topic_pub, "Playing " + current_track["Name"])
            playTrack(current_track)
        current_track = None;
        lock.release()
        
def playTrack(track_json):
    """
    Iterate through notes of a track and play each one. Blocking function
    
    Args:
        track_json (dict): The desired track to be played, in dict format
    """
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
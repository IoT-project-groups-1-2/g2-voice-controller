from machine import Pin, PWM, I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from time import sleep_ms
from rtttl import RTTTL
import network
import urequests
import credentials as creds
from umqtt.simple import MQTTClient
import json



"""
Pins configs
"""

speaker = PWM(Pin(0))
up_btn = Pin(2, Pin.IN, Pin.PULL_DOWN)
ok_btn = Pin(3, Pin.IN, Pin.PULL_DOWN)
down_btn = Pin(4, Pin.IN, Pin.PULL_DOWN)
led = Pin(6, Pin.OUT)

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
topic_mod = 'rtttl/mod'

#current track on the queue
current_track = None;

#current song index being shown on LCD
index = 0;


def wifi_connect():
    """
    Connect to wifi based on provided credentials, results to be shown on LCD screeen
    """
    lcd.putstr("Connecting to Wifi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(creds.ssid, creds.password)
    lcd.clear()
    lcd.putstr("Connected!!" if wlan.isconnected() else "Attempt failed! Please try again")



def mqtt_connect():
    """
    Connect to HiveMQ MQTT Server

    Returns:
        client (MQTTClient): MQTT Client Object
    """
    client = MQTTClient(client_id, mqtt_server, user=creds.mqtt_usr, password=creds.mqtt_password, keepalive=0)
    client.connect()
    return client


def mqtt_cb(topic, msg):
    """
    MQTT Callback function, called when a message is received from a subscribed topic.
    If received a message from mod topic, the playlist is updated, otherwise get song from wtd topic and play it

    Args:
        topic (byte): Topic to which the message was sent
        msg (byte): Message in byte format. Can be converted to string: str(msg, 'UTF-8')
    """
    print("Received {} from {}".format(msg, topic))
    if str(topic, 'UTF-8') is topic_mod:
        global playlist
        playlist = json.loads(msg)
    else:
        global current_track
        current_track = json.loads(msg)



def fetch_playlist():
    """
    Fetching playlist from the server

    Returns:
        playlist (dict): Returns a dictionary containing songs
    """
    playlist = urequests.get("http://192.168.121.50:3000/api/songs").json()
    lcd.clear()
    lcd.putstr(str(playlist[index]["id"]) + "." + playlist[index]["Name"][0:13])
    lcd.move_to(0, 1)
    lcd.putstr("<-     OK    ->")
    return playlist



def play_tone(freq, msec):
    """
    Playing a single tone

    Args:
        freq (int): frequency to play at
        msec (int): playtime duration in milliseconds
    """
    if freq > 0:
        speaker.freq(int(freq))       # Set frequency
        speaker.duty_u16(32768)       # 50% duty cycle
    sleep_ms(int(0.9 * msec))     # Play for a number of msec
    speaker.duty_u16(0)               # Stop playing for gap between notes
    sleep_ms(int(0.1 * msec))     # Pause for a number of msec


#initializations
wifi_connect()
playlist = fetch_playlist()
nr_of_songs = len(playlist)
client = mqtt_connect()
client.set_callback(mqtt_cb)
client.subscribe(topic_sub)
client.subscribe(topic_mod)



def loop():
    """
    Main task, checking if a track is on MQTT message queue, play track, else put on LCD menu
    """
    while True:
        global playlist
        global current_track
        global index
        index_changed = False
        while current_track is None:
            
            if up_btn.value() is 1:
                index_changed = True
                if index is 0:
                    index = len(playlist) - 1
                else:
                    index -= 1
            if down_btn.value() is 1:
                index_changed = True
                if index is len(playlist) - 1:
                    index = 0
                else:
                    index += 1
            if ok_btn.value() is 1:
                current_track = playlist[index]

            #preventing repetitive printing to LCD screen
            if index_changed:
                lcd.clear()
                lcd.putstr(str(playlist[index]["id"]) + "." + playlist[index]["Name"][0:13])
                lcd.move_to(0, 1)
                lcd.putstr("<-     OK    ->")
                index_changed = False
            client.check_msg()
    
        
        lcd.putstr(current_track["Name"])
        client.publish(topic_pub, "Playing " + current_track["Name"])
        playTrack(current_track)
        lcd.clear()
        lcd.putstr(str(playlist[index]["id"]) + "." + playlist[index]["Name"][0:13])
        lcd.move_to(0, 1)
        lcd.putstr("<-     OK    ->")

        #Reset
        current_track = None;


def playTrack(track_json):
    """
    Iterate through notes of a track and play each one, toggling LED in the process. Blocking function
    
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
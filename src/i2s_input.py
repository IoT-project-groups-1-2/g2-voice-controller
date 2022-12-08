import os
import io
import utime
from machine import I2S
from machine import Pin
from machine import timer
from RAMBlockDev import RAMBlockDev
    
# ======= BOOT FILESYSTEM INTO RAM =======
bdev = RAMBlockDev(1024, 50)
os.VfsLfs2.mkfs(bdev)
os.mount(bdev, '/ramdisk')
# ======= BOOT FILESYSTEM =======

# ======= I2S CONFIGURATION =======
SCK_PIN = 16
WS_PIN = 17
SD_PIN = 18
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 20000
# ======= I2S CONFIGURATION =======

# ======= AUDIO CONFIGURATION =======
WAV_FILE = "mic.wav"
WAV_SAMPLE_SIZE_IN_BITS = 16
FORMAT = I2S.MONO
SAMPLE_RATE_IN_HZ = 44100
# ======= AUDIO CONFIGURATION =======

RECORD = 0
IDLE = 1
STOP = 2

format_to_channels = {I2S.MONO: 1, I2S.STEREO: 2}
NUM_CHANNELS = format_to_channels[FORMAT]
WAV_SAMPLE_SIZE_IN_BYTES = WAV_SAMPLE_SIZE_IN_BITS // 8

# GPIO_0 LED def here
LED = machine.Pin(0, machine.Pin.OUT)

# GPIO_1 LED def here
BUTTON = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)

def create_wav_header(sampleRate, bitsPerSample, num_channels, num_samples):
    datasize = num_samples * num_channels * bitsPerSample // 8
    o = bytes("RIFF", "ascii")  # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(
        4, "little"
    )  # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE", "ascii")  # (4byte) File type
    o += bytes("fmt ", "ascii")  # (4byte) Format Chunk Marker
    o += (16).to_bytes(4, "little")  # (4byte) Length of above format data
    o += (1).to_bytes(2, "little")  # (2byte) Format type (1 - PCM)
    o += (num_channels).to_bytes(2, "little")  # (2byte)
    o += (sampleRate).to_bytes(4, "little")  # (4byte)
    o += (sampleRate * num_channels * bitsPerSample // 8).to_bytes(4, "little")  # (4byte)
    o += (num_channels * bitsPerSample // 8).to_bytes(2, "little")  # (2byte)
    o += (bitsPerSample).to_bytes(2, "little")  # (2byte)
    o += bytes("data", "ascii")  # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4, "little")  # (4byte) Data size in bytes
    return o


def timercallback(t):
    state = STOP

def i2s_callback_rx(arg):
    global state
    global num_sample_bytes_written_to_wav
    global mic_samples_mv
    global num_read

    if state == RECORD:
        utime.sleep(0.5)
        num_bytes_written = wav.write(mic_samples_mv[:num_read])
        num_sample_bytes_written_to_wav += num_bytes_written
        # read samples from the I2S device.  This callback function
        # will be called after 'mic_samples_mv' has been completely filled
        # with audio samples
        num_read = audio_in.readinto(mic_samples_mv)
    elif state == STOP:
        print("nig")
        LED.low()
        # create header for WAV file and write file
        wav_header = create_wav_header(
            SAMPLE_RATE_IN_HZ,
            WAV_SAMPLE_SIZE_IN_BITS,
            NUM_CHANNELS,
            num_sample_bytes_written_to_wav // (WAV_SAMPLE_SIZE_IN_BYTES * NUM_CHANNELS),
        )
        _ = wav.seek(0)  # advance to first byte of Header section in WAV file
        num_bytes_written = wav.write(wav_header)
        # cleanup
        wav.close()
        print("Done closing the audio file")
        os.umount("/ramdisk")
        audio_in.deinit()
        print("Done")
    else:
        print("Not a valid state.  State ignored")


wav = open("/ramdisk/{}".format(WAV_FILE), "wb")
pos = wav.seek(44)  # advance to first byte of Data section in WAV file

audio_in = I2S(
    I2S_ID,
    sck=Pin(SCK_PIN),
    ws=Pin(WS_PIN),
    sd=Pin(SD_PIN),
    mode=I2S.RX,
    bits=WAV_SAMPLE_SIZE_IN_BITS,
    format=FORMAT,
    rate=SAMPLE_RATE_IN_HZ,
    ibuf=BUFFER_LENGTH_IN_BYTES,
)

# setting a callback function makes the
# readinto() method Non-Blocking
audio_in.irq(i2s_callback_rx)

# allocate sample arrays
# memoryview used to reduce heap allocation in while loop
mic_samples = bytearray(1000)
mic_samples_mv = memoryview(mic_samples)

num_sample_bytes_written_to_wav = 0
recording_seconds = 0

state = IDLE
# start the background activity to read the microphone.
# the callback will keep the activity continually running in the background.
num_read = audio_in.readinto(mic_samples_mv)


# === Main program code goes here ===
# changing 'state' can cause the recording to Pause, Resume, or Stop


while(True):
    if not BUTTON.value() and STATE != STOP:
        #periodic timer with 100ms interval
        tim.init(mode=Timer.ONE_SHOT, period=100000, callback=timercallback)
        LED.on()
        state = RECORD
    else:
        LED.off()


"""print("starting recording for 5s")
state = RECORD
utime.sleep(5)
print("pausing recording for 2s")
state = PAUSE
utime.sleep(2)
print("resuming recording for 5s")
state = RESUME
utime.sleep(5)
print("stopping recording and closing WAV file")
state = STOP
utime.sleep(2)"""
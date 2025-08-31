from asyncio import run, create_task, sleep
from dfplayer import DFPlayer
from machine import Pin, I2C, SoftI2C
from machine_i2c_lcd import I2cLcd
import uasyncio as asyncio
import ssd1306
import ujson
import platform
from time import sleep
import os
import random
from array import array

print("Starting Up!")
sleep(1)

# set if using the 128x64 OLED or the 2 line LCD ("oled" or "lcd)
displayType = "lcd"

# I got a Pi Pico!
# amend here to assign pins based on if it's a pico or esp32
platformString = platform.platform()
theList = platformString.split('-')
theArchitecture = theList[2]
print(theArchitecture)
if (theArchitecture == 'arm'):
    displaySCL = 15
    displaySDA = 14
    uartInstance = 0
    playbackModePin = 3
    playPausePin = 2
else:
    displaySCL = 15
    displaySDA = 14
    uartInstance = 2
    playbackModePin = 14
    playPausePin = 12
# define pin for playback mode and play/pause

# set up the OLED or LCD depending on the variable above
if (displayType == "oled"):
    i2c = I2C(1, scl=Pin(displaySCL), sda=Pin(displaySDA))
    
    def init_oled():
        global oled
        oled_width = 128
        oled_height = 64
        oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
        oled.contrast(100)
        oled.invert(0)
        oled.rotate(True)
        oled.fill(0)
        
    init_oled()
    
    oled.text('Connected', 1, 2, 1)
    oled.text('Booting', 1, 14, 1)
    oled.text('uPython', 1, 26, 1)
    oled.show()

    # have to set lcd to null
    lcd = ""

elif(displayType == "lcd"):
    # Define the LCD I2C address and dimensions
    I2C_ADDR = 0x27
    I2C_NUM_ROWS = 2
    I2C_NUM_COLS = 16

    # Initialize I2C and LCD objects
    i2c = I2C(1, sda=Pin(displaySDA), scl=Pin(displaySCL))
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    lcd.backlight_on()
    lcd.putstr("Ready...")

    # still need to define the oled var
    oled = ""


# TBD: Add Mode button - Sequential / Random
# define playMode variable, default is "sequential"
playMode = "sequential"

# define playbackStatus, default is "stopped"
playbackStatus = "stopped"

# add log to file
import os

# Function to log messages to a file
def log_to_file(message):
    try:
        with open("log.txt", 'a') as file:
            file.write(message + '\n') 
    except OSError as e:
        print(f"Error writing to file: {e}")

# TBD: Add Play/Pause button - not complete
async def button_listener_playPause(df):
    button = Pin(playPausePin, Pin.IN, Pin.PULL_UP)
    prev_state = button.value()
    while True:
        await asyncio.sleep_ms(20)  # debounce delay
        curr_state = button.value()
        if curr_state == 0:
            print("Button pressed!")
            await df.next()
        prev_state = 0

# Not in use right now...
async def repl_trigger(df):
    print("Press Enter in REPL to skip to the next track...")
    try:
        input()  # blocks REPL until Enter is pressed
        print("REPL input received")
        await df.next()
    except KeyboardInterrupt:
        print("Interrupted by user")

# LED pin mapping
# Not in use, this "seemed like a good idea at the time.."
# 1 is green, 2 is amber, 3 is red
LED_TRACK_MAP = {
    1: Pin(5, Pin.OUT),
    2: Pin(19, Pin.OUT),
    3: Pin(18, Pin.OUT)
}

# Get the track names from playlist.json on the device
try:
    f = open("playlist.json",'r')
    theTracks=f.read()
    f.close()
    theTracks = ujson.loads(theTracks)
    print('Playlist file loaded')
except:
    print('Playlist file load failed')

# shuffle track entries (mainly for future "random" playback function"
def shuffle(array):
    for i in range(len(array)-1, 0, -1):
        j = random.randrange(i+1)
        array[i], array[j] = array[j], array[i]
    return array

# displayStuff is work in progress, not used right now!
def displayStuff(displayType, stuffToShow, clearFirst):
    # clearFirst is 0 or 1
    # stuffToShow can be a dictionary with the lines eg ["1":"SongName","2":"ArtistName"]
    # can have line 3 or more if OLED
    if displayType == "lcd" and clearFirst == 1:
        lcd.clear()
    elif displayType == "oled" and clearFirst == 1:
         oled.fill(0)
    
    for line in stuffToShow:
        lineValue = stuffToShow[line]
        if displayType == "lcd":
            # lcd
            
        elif displayType == "oled":
            # oled

trackNumbers =  [int(k) for k in theTracks.keys()]
shuffleOrder = shuffle(trackNumbers)

# Scroll text on OLED (not used?)
async def scroll_text(oled, text, y=14, delay=0.1):
    oled.fill_rect(0, y, 128, 10, 0)  # Clear the text line
    width = len(text) * 8  # Approximate pixel width (assuming 8px per character)

    for offset in range(width - 128 + 1):  # Scroll range based on width
        oled.fill_rect(0, y, 128, 10, 0)  # Clear area again
        oled.text(text[offset:], 1, y)
        oled.show()
        await asyncio.sleep(delay)

# continuous scroll text on OLED
async def scroll_text_continuous(oled, text, y=14, delay=0.05):
    display_width = 128
    char_width = 8  # each character is approx 8 pixels wide
    text_width = len(text) * char_width

    # If text fits, just show it once without scrolling
    if text_width <= display_width:
        oled.fill_rect(0, y, display_width, 10, 0)
        oled.text(text, 0, y)
        oled.show()
        return  # no need to scroll

    # If text is too wide, scroll it
    scroll_text = text + "   "  # add some space before looping
    full_text = scroll_text + scroll_text  # wraparound effect
    width = len(scroll_text) * char_width

    while True:
        for i in range(width):
            oled.fill_rect(0, y, display_width, 10, 0)
            segment = full_text[i // char_width:]
            oled.text(segment, 0, y)
            oled.show()
            await asyncio.sleep(delay)


# TBD: Amend to show green for playing, amber for random, red for paused
# Not used, again this seemed like a cool thing at the time..
async def track_led_monitor(df):
    active_pin = None
    last_track = None
    scroll_task_artist = None
    scroll_task_title = None

    while True:
        await asyncio.sleep(1)
        try:
            track = await df.track_id(None)

            if str(track) != str(last_track):
                print("Track changed:", track)

                if active_pin:
                    active_pin.value(0)
                
                track_info = theTracks.get(str(track), {"artist":"Unknown","name": "Unknown Track", "rating": 0})
                thisTrackName = track_info["name"]
                thisArtistName = track_info["artist"]
                thisTrackRating = int(track_info["rating"])
                print(thisTrackName)
                print(thisTrackRating)
                ratingText = "Track: " + str(track)
                
                
                rating_pin = next(pin for cond, pin in [(thisTrackRating > 8, 1),(thisTrackRating >= 4, 2),(True, 3)] if cond)
                active_pin = LED_TRACK_MAP.get(rating_pin)
                if active_pin:
                    active_pin.value(1)
                # First cancel any existing scroll tasks, if you’ve added tracking like before
                if scroll_task_artist:
                    scroll_task_artist.cancel()
                    try:
                        await scroll_task_artist
                    except asyncio.CancelledError:
                        pass

                if scroll_task_title:
                    scroll_task_title.cancel()
                    try:
                        await scroll_task_title
                    except asyncio.CancelledError:
                        pass
                # TBD! Some sort of unified function like "displayStuff()" that will display on the selected device rather than an if/elif
                if (displayType == "oled"):
                    oled.fill(0)
                    oled.text('Now Playing:', 1, 2, 1)
                    oled.text(ratingText, 1, 38, 1)
                    oled.show()
                    # Start new ones
                    scroll_task_artist = asyncio.create_task(scroll_text_continuous(oled, thisArtistName, y=14))
                    scroll_task_title = asyncio.create_task(scroll_text_continuous(oled, thisTrackName, y=26))
                elif (displayType == "lcd"):
                    lcd.clear()
                    lcd.putstr(thisTrackName)
            
                last_track = track

        except Exception as e:
            print("Error checking track:", e)

# TBD: add modifed version of below to play in random order
# - needs to be sure to not play anything last played within n plays of last time, where n is total tracks

# Function to loop tracks
async def auto_play_loop(df):
    log_to_file("autoplay loop called")
    try:
        total_tracks = await df.num_files_device()
        current_track = 1

        while True:
            print(f"Attempting to play track {current_track}")
            log_to_file(f"Attempting to play track {current_track}")
            track_started = False

            # Keep retrying until the track starts playing
            while not track_started:
                try:
                    await df.play(None, current_track)
                    await asyncio.sleep(1)  # Give DFPlayer time to respond

                    # Confirm playback started
                    if await df.playing() == 1:
                        log_to_file(f"Track {current_track} is now playing")
                        print(f"Track {current_track} is now playing")
                        track_started = True
                    else:
                        log_to_file(f"Track {current_track} did not start, retrying...")
                        await asyncio.sleep(2)  # brief pause before retry

                except Exception as e:
                    log_to_file(f"Error starting track {current_track}: {e}")
                    await asyncio.sleep(2)  # wait before retrying

            # Wait until track finishes
            while True:
                try:
                    if await df.playing() != 1:
                        log_to_file(f"Track {current_track} finished")
                        break
                    await asyncio.sleep(1)
                except Exception as e:
                    log_to_file(f"Error checking playback status: {e}")
                    await asyncio.sleep(2)  # keep polling

            # Move to next track
            current_track += 1
            if current_track > total_tracks:
                current_track = 1

    except Exception as e:
        log_to_file(f"auto_play_loop crashed fatally:{e}")
           
async def main():
    # df = DFPlayer(uartInstance) # using UART id 2
    df = DFPlayer(1)
    print("Awaiting UART connection...")
    sleep(2)
    df.init() # initialize UART connection
    print("INIT complete..")
    print("Awaiting player ready...")
    await df.wait_available() # optional; making sure DFPlayer finished booting
    lcd.clear()
    await df.volume(25)
    print("DFPlayer reports volume:", await df.volume())
    totalFiles = await df.num_files_device()
    totalFiles = str(totalFiles)
    print(f"DFPlayer reports filecount: {totalFiles}")
    print("Playing track")
    # await df.play(None, 1) # folder 1, file 1
    # Run button listener alongside
    asyncio.create_task(butto
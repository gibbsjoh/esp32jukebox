from asyncio import run, create_task, sleep
from dfplayer import DFPlayer
from machine import Pin
import uasyncio as asyncio

BUTTON_PIN = 13

async def button_listener(df):
    button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
    prev_state = button.value()
    while True:
        await asyncio.sleep_ms(20)  # debounce delay
        curr_state = button.value()
        if prev_state == 1 and curr_state == 0:  # falling edge detected
            print("Button pressed!")
            await df.next()
        prev_state = curr_state

async def repl_trigger(df):
    print("Press Enter in REPL to skip to the next track...")
    try:
        input()  # blocks REPL until Enter is pressed
        print("REPL input received")
        await df.next()
    except KeyboardInterrupt:
        print("Interrupted by user")

# LED pin mapping
LED_TRACK_MAP = {
    1: Pin(21, Pin.OUT),
    2: Pin(19, Pin.OUT),
    3: Pin(18, Pin.OUT)
}

async def track_led_monitor(df):
    active_pin = None
    while True:
        await asyncio.sleep(1)  # Poll every 1s
        try:
            track = await df.track_id(None)
            print("Currently playing track:", track)

            # Turn off previous LED
            if active_pin:
                active_pin.value(0)

            # Turn on current LED if mapped
            active_pin = LED_TRACK_MAP.get(track)
            if active_pin:
                active_pin.value(1)

        except Exception as e:
            print("Error checking track:", e)

async def main():
    df = DFPlayer(2) # using UART id 2
    df.init() # initialize UART connection
    await df.wait_available() # optional; making sure DFPlayer finished booting

    await df.volume(25)
    print("DFPlayer reports volume:", await df.volume())
    await df.num_files_device()
    print("DFPlayer reports filecount:", await df.num_files_device())
    print("Playing track")
    await df.play(None, 1) # folder 1, file 1
    # Run button listener alongside
    asyncio.create_task(button_listener(df))
    asyncio.create_task(track_led_monitor(df))
    # Keep the main task alive
    while True:
        await sleep(1)
    #print("Player status:", await df.playing

run(main())

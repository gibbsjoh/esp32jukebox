# pi pico ukebox
I got a Pi Pico and decided to rework the code to run on that. It was relatively straightforward!

Requires dfplayer-mp: https://github.com/Muhlex/dfplayer-mp 

and also the relevant modules for either the OLED display or the 2 row LCD display:

LCD: https://github.com/RuiSantosdotme/Random-Nerd-Tutorials/tree/master/Projects/ESP-MicroPython/lcd

OLED: TBD

The whole setup can be powered from the USB port or via 5v on the relevant pin. I used a little board that came with a breadboard kit that takes 6v-9v in and outputs 5v and 3.3v to the power pins on the breadboard.

This is the MP3 player board I used (got it from Amazon):  
https://www.amazon.co.uk/dp/B0CDN6D8W8  
It uses 9600 baud for the serial comms - be aware, as some dfplayer code out there specifies 115200.

Playing folder numbers doesn't seem to work, so I pass "None" and all seems OK.

Track names come from a JSON file on the board that needs to be updated if you change tracks. Fairly straightforward.

There's a button listener to go to the next track. For some reason the GPIO In is high when the button is NOT pressed and low when it is pressed, hence the reversal of the values in that function.

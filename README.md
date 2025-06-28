# esp32jukebox
MicroPython + ESP32 + Serial MP3 module, just messing around

Requires dfplayer-mp: https://github.com/Muhlex/dfplayer-mp

I had some trouble figuring out the UART setup - dfplayer-mp uses the default pins for a given UART number (0-2 on the ESP32WROOM I have). The default pins for these UARTS are specified here:  
(UART Number/TX/RX)  
UART0	GPIO 1	GPIO 3  
UART1	GPIO 10	GPIO 9  
UART2	GPIO 17	GPIO 16  

This is the board I used (got it from Amazon):  
https://www.amazon.co.uk/dp/B0CDN6D8W8  
It uses 9600 baud for the serial comms - be aware, as some dfplayer code out there specifies 115200.

Playing folder numbers doesn't seem to work, so I pass "None" and all seems OK.

There's a button listener to go to the next track.
The LEDs light up according to track number (I wanted to do a query based on the filename but so far that eludes me!

![IMG_1646](https://github.com/user-attachments/assets/754d5567-5538-4c60-ba57-fa74bcc9ba47)

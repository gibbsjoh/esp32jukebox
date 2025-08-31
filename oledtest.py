from machine import Pin, I2C
import ssd1306

i2c = I2C(0, scl=Pin(displaySCL), sda=Pin(displaySDA))
displaySCL = 1
displaySDA = 0

print('I2C SCANNER')
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:', len(devices))

  for device in devices:
    print("I2C hexadecimal address: ", hex(device))


# def init_oled():
#     global oled
#     oled_width = 128
#     oled_height = 64
#     oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
#     oled.contrast(100)
#     oled.invert(0)
#     oled.rotate(True)
#     oled.fill(0)
    
# init_oled()

# oled.text('Connected', 1, 2, 1)
# oled.text('Booting', 1, 14, 1)
# oled.text('uPython', 1, 26, 1)
# oled.show()
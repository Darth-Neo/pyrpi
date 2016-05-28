#!/usr/bin/python
# Example using a character LCD connected to a Raspberry Pi.
import math
import time

import Adafruit_CharLCD as LCD

def test_lcd():
    # Raspberry Pi pin configuration:
    lcd_rs        = 27  # Note this might need to be changed to 21 for older revision Pi's.
    lcd_en        = 22
    lcd_d4        = 25
    lcd_d5        = 24
    lcd_d6        = 23
    lcd_d7        = 18
    lcd_backlight = 4

    # Define LCD column and row size for 16x2 LCD.
    lcd_columns = 16
    lcd_rows    = 2

    print ("Init LCD")
    # Initialize the LCD using the pins above.
    lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en,
                           lcd_d4, lcd_d5, lcd_d6, lcd_d7, 
                            lcd_columns, lcd_rows,
                            lcd_backlight)

    lcd.enable_display(True)

    print ("Message - 'Hello World")
    # Print a two line message
    lcd.message('Hello\nworld!')

    # Wait 5 seconds
    time.sleep(5.0)

    print('Show cursor')
    # Demo showing the cursor.
    lcd.clear()
    lcd.show_cursor(True)
    lcd.message('Show cursor')

    time.sleep(5.0)

    print('Blink cursor')
    # Demo showing the blinking cursor.
    lcd.clear()
    lcd.blink(True)   
    lcd.message('Blink cursor')

    time.sleep(5.0)

    print("reset")
    # Stop blinking and showing cursor.
    lcd.show_cursor(False)
    lcd.blink(False)

    time.sleep(5)

    print("Scroll...")
    # Demo scrolling message right/left.
    lcd.clear()
    message = 'Scroll'
    lcd.message(message)
    for i in range(lcd_columns-len(message)):
        time.sleep(0.5)
        lcd.move_right()
    for i in range(lcd_columns-len(message)):
        time.sleep(0.5)
        lcd.move_left()

    time.sleep(5)

    # Demo turning backlight off and on.
    print('Flash backlight\nin 5 seconds...')
    lcd.clear()
    lcd.message('Flash backlight\nin 5 seconds...')

    time.sleep(5.0)

    print("Turn backlight off")
    # Turn backlight off.
    lcd.set_backlight(0)
    
    time.sleep(5.0)
    print("Goodbye")

    # Change message.
    lcd.clear()
    lcd.message('Goodbye!')

    # Turn backlight on.
    lcd.set_backlight(1)
    time.sleep(5)

if __name__ == "__main__":
    for x in range(1,100):
        test_lcd()

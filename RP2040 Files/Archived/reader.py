from machine import Pin, SPI
from sys import implementation
from os import uname
import utime

import network							# For WLAN
import ili9341
from xglcd_font import XglcdFont

# These are my files
import standardLibrary as slib
import lcdDriver
import keypadDriver
import config as cfg

import messaging
import socketComm
# import production as prod



    

test_list = "this is a item\nand this\nand also this"

lcd = lcdDriver.display()
keypad = keypadDriver.keypad(lcd=lcd)
lcd.keypad = keypad
lcd.setBorder("FROM: Chatty Cathy\nAnother line", function="top")
lcd.setBorder("A bunch of random text on the bottom to test the function", function="bottom")

direction = lcd.out(cfg.multiLine)

print(f"exit direction: {direction}")

    


    

    
    


        
        
        

    
lcd = lcdDriver.display()
keypad = keypadDriver.keypad(lcd=lcd)


lcd.setBorder(string="FROM: Chatty Cathy\nTest")
lcd.setBorder(string="This is a string, and this is an even longer string", function="bottom", hBar=True)

# string = "1\\n2\\n3\\n4\\n5\\n6\\n7\\n8\\n9\\n10\\n11\\n12\\n13\\n14\\n15\\n16\\n17\\n18\\n19\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n\\n33\\n\\n\\n\\nEndOfString"
# lcd.print(string)
while True:
    # out(lcd, "test")
    exitDir = lcd.out(cfg.multiLine2, keypad)
    input(f"exitDir {exitDir}")
    exitDirection, stringList = reader2(cfg.multiLine, keypad)
    # exitDirection, stringList = reader("", keypad)
    print(stringList)
    lcd.clt()
    print(f"Exit Direction: {exitDirection}")
    input(":")
    

#ToDo List:
# Fix the clsLine function in the lcdDriver; it doesn't appear to do anything...

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

os_name = "MicOS"
os_author = "Micah Hurd"
os_version = "0.006"
version_date = "2022-10-19"
os_platform = ""				#To Do




def writeToOutbox(outbox_file, message, number, name, msgType):
    # writeToOutbox(cfg.outbox_file, "test Message", "+19728370200", "Micah Hurd", "signal")
    timeStamp = utime.time()
    string = f"{number},{timeStamp},{name},{message},{msgType}"
    slib.writeTempFile(data=string, filePath=outbox_file)
    lcd.out("\\nWrote message to the outbox...")
    utime.sleep(0.5)

def downloadMsgs():
    new=0
    duplicate=0
    
    sconn = socketComm.communication(lcd=lcd)
    success = sconn.initConnection()
    
    if not success:
        input("Error connecting to server!")
    else:
        print("connected to server. Getting messages")
        successFlag = sconn.get_msgs()
        sconn.close_conn()
        print("Terminated server connection!")
                
        if successFlag:
            new, duplicate = slib.parseNewMessages()
    
    lcd.out(f"Recieved {new} new msgs, {duplicate} duplicates")
    keyIn(self, text="Press Any Key to Continue...", cursorOn=1)
            
            
def phoneCall():
    print("Made a phone call")

def smsMessages():
    print("Checked SMS messages")
    msg = None
    number, name = messaging.displayInbox(lcd, keypad, cfg.mms_msg_file)
    print(number, name)
    if number != "":
        response = messaging.getMessages(lcd, keypad, number, name, cfg.mms_msg_file, cfg.temporary_msg_file)
        if response == 1:
            msg = messaging.respondMsg(lcd, keypad, number, name)

    if msg != None:
        print(f"Message to recipient: {msg}")
        writeToOutbox(cfg.outbox_file, msg, number, name, "mms")
    
def signalMessage():
    print("Check Signal messages")
    
def contactList():
    print("Viewed Contacts")

def mainMenu():
    main_menu_dict = {
    "Make a Call": phoneCall,
    "View SMS": smsMessages,
    "View Signal": signalMessage,
    "View Contacts": contactList,
    "Download Messages": downloadMsgs
    }
    
    lcd.cls()
    os_load_screen()
    lcd.horizontal_bar(text="MAIN MENU", alignment=0)
    dictLen = len(main_menu_dict)
    for index, item in enumerate(main_menu_dict):
        lcd.out(f"\\n{index}: {item}")
    
    lcd.horizontal_bar()
    lcd.out(f"\\nChoose (0 to {dictLen-1}): ", end="")
    tempInt = int(keypad.keyIn())
    
    keys_list = list(main_menu_dict)
    key = keys_list[tempInt]
    main_menu_dict[key]()
    
    
def processOutbox(file):
    
    if slib.isFileEmpty(file) == False:
        fp = open(file)
        tempBool = False
        for index, msg in enumerate(fp):
            msg = msg.strip()
            tempList = msg.split(",")
            msgType = tempList[-1]
            
            if msgType == "signal" or msgType == "discord" or msgType == "email":
                tempBool = True
                break
        if tempBool:
            # Send files destined for the server first
            sconn = socketComm.communication(lcd=lcd)
            success = sconn.initConnection()
            if success:
                sconn.sendMsgs(file)
                sconn.close_conn()
       
    print("digital done, mms left")
    if slib.isFileEmpty(file):
       return False
    else:
        print("Pretended to send MMS messages, for testing purposes")
        return True
        
lcd = lcdDriver.display()					# Init the LCD Display
lcd.out(f"{os_name} - {os_version} {version_date}\n")
os_load_screen(print_speed=0)
# os_load_screen()							# Show the OS details
# wlan = slib.wifi_connect(lcd_driver=lcd)
keypad = keypadDriver.keypad(lcd=lcd)
lcd.keypad = keypad

lcd.reader(cfg.multiLine, keypad)

lcd.cls()
# lcd.cursor(0)
lcd.dispObj.set_scroll(top=0, bottom=0)
lcd.setBorder("FROM: Hannah", side="top", hBar=True)
lcd.setBorder("Bottom", side="bottom", hBar=True)

while True:
                                                       
    print(f"x    : {lcd.xCounter}\nmax_x: {lcd.xCharMax}\ny    : {lcd.yCounter}\nmax_y: {lcd.yCharMax}\ny_remainder: {lcd.yRemainder()}")
    string = input(": ")
    lcd.out(string)
    
    
    

while True:
    # processOutbox(cfg.outbox_file)
    selected_menu = mainMenu()
           
    
    
    

    
"""
    
    

messaging.respondMsg(lcd, keypad, "+19728370200", "Micah Hurd")
messaging.getMessages(lcd, keypad, "+19728370200", "Micah Hurd", cfg.msg_file, cfg.temporary_msg_file)

# messaging.getMessages("+19728370200", cfg.msg_file)
# messaging.displayMessage(lcd, keypad, cfg.temporary_msg_file)

mainMenu()






============== This below is for once reading messages has been worked out ===================
mqtt = mqttDriver.mqtt_conn(cfg.mqtt_server_IP, cfg.mqtt_cli_name)

while True:
    msg = input("Enter a message: ")
    mqtt.sendMsg(cfg.mqtt_topic_uplink, msg)
    print("msg sent!")
=============================================================================================


lcd.out("1234567890\\n1234567890\\n1234567890\\n1234567890")
# print(lcd.dispBufferList)
# print(lcd.xCharMax)
while True:
    print(lcd.xCounter)
    lcd.print(input(": "))
    print(lcd.dispBufferList)





newLineBool = True
string = ""
while True:
    
    # print(f"\nnewLineBool: {newLineBool}")
    string = keypad.keyIn("/f to change font \n/cls to clear)\nEnter a string to display: ")
    
    print(f"Got this from the keypad: >{string}<")
    if string != None:
        lcd.printAlt(string, newLine=newLineBool)
"""




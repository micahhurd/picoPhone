# Version: 0.007
#ToDo List:
# Build function to get phone number entry
# Build phone call outbound menu
# Build config file editing menu
# Add time banner to top

# Micropython
import utime
# Mine
import lcdDriver
import keypadDriver
import config as cfg
import standardLibrary as slib
import messaging
import phonecall as vCall

os_name = "MicOS"
os_author = "Micah Hurd"
os_version = "0.017"
version_date = "2022-12-14"
os_platform = "RP2040"				

def phoneCall():
    vCall.main(lcd, kpd)

def smsMessages():
    mmsMsgs.inbox()

def signalMessages():
    pass

def contactList():
    slib.viewContacts(lcd)

def downloadMsgs():
    pass

def callMenuSelection(dictionary, index):
    keys_list = list(dictionary)
    key = keys_list[index]
    print(f"selected: {key}")
    dictionary[key]()

def composeNew():
    msgTypeList = ["MMS", "Signal", "E-Mail"]
    respIndex = slib.numericalMenu(lcd, msgTypeList, menuName="Choose Msg Type")
    if respIndex == -1:
        return 0
    msgType = msgTypeList[respIndex].lower()	# Must give the contact selection function the message type in lowercase
    address, name = slib.selectContact(lcd, contactType=msgType)
    if address == "exit":
        return 0
    msg = slib.respondMsg(lcd, address, name, msgsType=msgType)
    slib.writeToOutboxFile(address, name, msgType, msg)
    
    
main_menu_dict = {
    "Make a Call": phoneCall,
    "View SMS": smsMessages,
    "View Signal": signalMessages,
    "View Contacts": contactList,
    "Download Messages": downloadMsgs,
    "Compose New Message": composeNew
    }

# ========= Start Peripherals ===============
lcd = lcdDriver.dispDriver()
kpd = keypadDriver.keypad(lcd=lcd)
lcd.keyCtrl = kpd
slib.os_load_screen(lcd, os_name, os_author, os_version, version_date, os_platform)
# wlan = slib.wifi_connect(lcd_driver=lcd)
# ===========================================

# ========= Start Msging Services ===========
mmsMsgs = messaging.msgs("Text Messages", "mms", cfg.mms_msg_file, lcd, kpd)
# ===========================================

# ======= Start Background Services =========
backgroundTask = slib.background_task(lcdObj=lcd, interval=cfg.background_task_interval)
# ===========================================

# ============== MAIN LOOP ==================

while True:
    
    while False:
        lcd.displayOnOff(True)
        # lcd.dispObj.display_off
        # print("off")
        utime.sleep(1)
        # lcd.dispObj.display_on
        # print("on")
        lcd.displayOnOff(False)
        utime.sleep(1)
        
    selection = slib.numericalMenu(lcd, main_menu_dict, "MAIN MENU", allowCancel=False)
    callMenuSelection(main_menu_dict, selection)



input("::")

# ===========================================


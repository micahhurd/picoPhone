# Version 0.009
import config as cfg
import network,utime

class background_task:
    
    def __init__(self, lcdObj, interval=3):
        self.lcd = lcdObj
        # self.last_timestamp = 0
        self.current_timestamp = 0
        self.timer = None
        
        # Start the timer which will run the background tasks
        self.startTask(frequency=(interval*1000))
        
    def startTask(self, frequency):
        from machine import Timer
        
        try:
            frequency = int(frequency)
        except:
            frequency = 500

        # timer_two = Timer()
        # print("--- Ready to get user inputs ---")
        self.timer = Timer(-1)
        self.timer.init(period=frequency, mode=Timer.PERIODIC, callback=lambda t:self.tasks())
        utime.sleep(0.5)
        # print("started background tasks...")
        self.lcd.print("started background tasks...")
    
    def backlightCtrl(self):
        self.current_timestamp = getCurrentTS()
        delta = self.current_timestamp - self.lcd.last_key_press_ts
        # print(f"Line 18: {delta} {cfg.backlight_timer} {self.current_timestamp} {self.lcd.last_key_press_ts}")
        if delta > (cfg.backlight_timer):	# Convert seconds to milliseconds
            # print("turning off LCD")
            self.lcd.displayOnOff(False)
        self.last_timestamp = self.current_timestamp
            
    def check_modem_call(self):
        pass
    
    def check_modem_sms(self):
        pass
    
    def check_tcp_msgs(self):
        pass
    
    def send_tcp_msgs(self):
        pass    
    
    def tasks(self):
        # print("running tasks")
        self.check_modem_call()
        self.check_modem_sms()
        self.check_tcp_msgs()
        self.send_tcp_msgs()
        self.backlightCtrl()
        
def wifi_connect(lcd_driver=None):
       
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(cfg.wifi_ssid,cfg.wifi_pass)
    if lcd_driver == None:
        print("Waiting to connect to WiFi...")
    else:
        lcd_driver.print("Waiting to connect to WiFi...\\n")
    while not wlan.isconnected():  
        utime.sleep(0.1)
        if lcd_driver != None:
            lcd_driver.print(".", end="")
    if lcd_driver == None:   
        print(f"\\nConnected to Wifi SSID {cfg.wifi_ssid}")
    else:
        lcd_driver.print(f"\\n -> Connected to Wifi SSID ({cfg.wifi_ssid})")
    if cfg.debug_bool1:
        utime.sleep(1)
    return wlan

def os_load_screen(display_object, os_name, os_author, os_version, version_date, os_platform):
    string = f"#0{os_name}\n"
    string+= f"\nAuthor: {os_author}"
    string+= f"\nVersion: {os_version}"
    string+= f"\nDate: {version_date}"
    string+= f"\nPlatform: {os_platform}"
    string+= "\n\n#0"
    display_object.print(string)

def printList(lst):
    cnt = 0
    for item in lst:
        print(f"{cnt}: {item}")
        cnt+=1

def strToBytes(inputString, encoding="utf-8"):
    arr = bytes(inputString, encoding)
    return arr

def returnVarType(variable):
    tempStr = str(type(variable))
    tempStr = tempStr[8:]
    tempStr = tempStr[:-2]
    return tempStr

def numericalEntry(lcd, kpad, banner="Enter Text Below:\\n",
              allowedChar = ["1","2","3","4","5","6","7","8","9","0"],
              enterChar="D", bSpace="#", tempStr=None):
    # Allows one character to be entered at a time... Or else needs to be deprecated / removed
    if banner != None:
        lcd.print(banner)
    if tempStr == None:
        tempStr = ""
    while True:
        char = kpad.keyIn()
        if char == enterChar:
            break
        elif char == bSpace:
            lcd.print("\\d")
        elif char in allowedChar:
            tempStr+=char
            lcd.print(char, end="")
    return tempStr


def txtFileLength(file):
    fp = open(file)
    output = 0
    for index, line in enumerate(fp):
        output = index + 1
    fp.close
    return output

def isFileEmpty(file):
    import uos
    if uos.stat(cfg.outbox_file)[6] > 0:
        return False
    else:
        return True
    
def readFileAtLine(file, lineNumber):
    # should be zero-based starting value
    
    fp = open(file)
    output = ""
    for index, line in enumerate(fp):
        if index == lineNumber:
            output = line
            # print(f"Line number: {lineNumber}, index: {index}, Line: {output}")
            break
    fp.close()
    return output

def writeFileAtLine(file, lineNumber, string):
    # Can write to line -1 or greater
    import os   
        
    fpIn = open(file, 'r')
    fpOut = open("./temp.txt", "w")
    output = ""
    if lineNumber == -1:
        fpOut.write(string+"\n")
    for index, line in enumerate(fpIn):
        if index != lineNumber:
            fpOut.write(line)
        else:
            fpOut.write(string+"\n")
    fpIn.close()
    fpOut.close()
    
    os.rename("./temp.txt", file)

def stringToFile(string, filePath):
    f = open(filePath, 'a')
    f.write(string+"\n")
    f.close()

def writeTempFile(data=None, filePath="./tempFile.txt", flush=False):
    
    if flush:
        f = open(filePath, 'w')
        f.close()
    else:
        
        if data != None:
            
            data = str(data)
            data = data.strip()
            if data != "":
                # print(data)
                f = open(filePath, 'a')
                f.write(data+"\n")
                f.close()
    
def dateToTS(dateString):
    import time
    
    date_part = (dateString.split(" ")[0])
    time_part = (dateString.split(" ")[1])
    year = int(date_part.split("-")[0])
    month = int(date_part.split("-")[1])
    day = int(date_part.split("-")[2])
    hour = int(time_part.split(":")[0])
    minute = int(time_part.split(":")[1])
    second = int(time_part.split(":")[2])
    
    return time.mktime((year, month, day, hour, minute, second, 0, 0))

def findNthOccurence(string, character, nth):
    val = -1
    for i in range(0, nth):
        val = string.find(character, val + 1)
    return val

def parseNewMessages():
    fp = open(cfg.inbox_file)
    duplicateQty = 0
    newMsgQty = 0
    for index, line in enumerate(fp):
        line = line.strip()
        if line != "":
            tempList = line.split(",")
            try:
                msgType = tempList[-1]	#Msg Type MUST be the last item in the message string!
            except:
                msgType = "unk"
            
            if msgType == "mms":
                destFile = cfg.mms_msg_file
            elif msgType == "signal":
                destFile = cfg.signal_msg_file
            elif msgType == "discord":
                destFile = cfg.discord_msg_file
            elif msgType == "email":
                destFile = cfg.email_msg_file
            else:
                destFile = cfg.unknown_msg_file
            
            print(tempList)
            input(msgType)
            
            # Open the destination file
            try:
                fp2 = open(destFile)
            except:
                # In case the destination file does not yet exist, make it exist
                writeTempFile(filePath=destFile, flush=True)
                fp2 = open(destFile)
            
            # Check to make sure this is not a duplicate message    
            duplicate = False
            for index2, line2 in enumerate(fp2):
                if line2 == line:
                    duplicate = True
                    duplicateQty+=1
                    break
            if not duplicate:
                newMsgQty += 1
                writeTempFile(data=line, filePath=destFile)
    
    # Clear out the inbox file
    writeTempFile(filePath=cfg.inbox_file, flush=True)
    # Return values
    return newMsgQty, duplicateQty        
            
def qtyCharsNextSpace(index2, string):
    # continue = True
    counter = 0
    while True:
        index2+=1
        if index2 == len(string):
            break
        elif string[index2] == " ":
            break
        else:
            counter+=1
            
    return counter

def calc_lines_needed_to_print(textString, xCharMax):
    return len(convertStringToList(textString, xCharMax))

def equalizeLine(string, requiredLength):
    string = string.strip()
    if len(string) < requiredLength:
        while len(string) < requiredLength:
            # if "test" in string:
                # input(f">{string}< length: {len(string)}, max: {requiredLength} :")
            string+=" "
    elif len(string) > requiredLength:
        string = string[:-3]
        string+="..."
    
    # if "test" in string:
            # input(f"done: >{string}< length: {len(string)}, max: {requiredLength} :")
    return string

def convertStringToList(textString, xCharMax):
    
    def appendStr(string):
        buffer.append(string)
    
    # If a list is already passed in, check that each line is the correct length
    # Return the list, because its already a list
    if returnVarType(textString) == "list":
        for index, item in enumerate(textString):
            if len(item) > xCharMax:
                item = item[:(xCharMax-3)] + "..."
                textString[index] = item
            elif len(item) < xCharMax:
                item = equalizeLine(item, xCharMax)
                textString[index] = item
        return textString            
    
        
    buffer = []
    if returnVarType(textString) != "str":
        textString = str(textString)
    
    if len(textString) == 0:
        textString = " "
    
    stringLen = len(textString)
    index = 0
    xCntr = 0
    yCntr = 1
    currentLine = ""
    LF=""
    while True:
        xRemainder = xCharMax - xCntr
        currentChar = textString[index]
        # print(currentChar)
        # input(currentChar)
        if currentChar == "\\":
            try:
                LF = f"{currentChar}{textString[index+1]}"
                if ("\\n" in LF):
                    index+=1
            except:
                LF = ""
        if ("\\n" in LF) or "\n" in currentChar:
            currentLine = equalizeLine(currentLine, xCharMax)
            appendStr(currentLine)
            xCntr = 0
            currentChar = ""
            currentLine = ""
            LF =""
        elif currentChar == " ":                
            tempInt = qtyCharsNextSpace(index, textString)
            # print(f"chars remaining: {tempInt}")
            
            if (tempInt > xRemainder) and (tempInt <= xCharMax):
                # print(3)
                currentLine = equalizeLine(currentLine, xCharMax)
                # print(currentLine)
                appendStr(currentLine)
                xCntr = 0
                currentChar = ""
                currentLine = ""
            # elif tempInt > xCharMax:
                
            
        currentLine+=currentChar
        
        xCntr+=1
        index+=1
        # input(":")
        
        if index >= stringLen:
            currentLine = equalizeLine(currentLine, xCharMax)
            appendStr(currentLine)
            break
    return buffer
            
def getCurrentTS():
    return utime.time()

def writeToOutboxFile(number, name, msgsType, msgString, outboxPath=cfg.outbox_file):
    timeStamp = getCurrentTS()
    # +19728370200,1665909820,Micah Hurd,first mms message Message,mms
    tempStr = f"{number},{timeStamp},{name},{msgString},{msgsType}"
    stringToFile(tempStr, outboxPath)

def numericalMenu(lcd, dictionary, menuName="", allowCancel=True):
    # return -1 = user has chosen to cancel
    
    lcd.cls(True)
    lcd.setBorder(string=menuName, function="top", hBar=True)
    
    dictLen = len(dictionary)
    
    tempStr = ""
    for index, item in enumerate(dictionary):
        if tempStr != "":
            tempStr += "\n"
        tempStr+=f"{index}: {item}"
    
    lcd.print(tempStr)
    
    userResponse = lcd.getNumericalEntry(maximum=(dictLen-1), allowCancel=allowCancel)
    
    return userResponse

def importContactsToList(filepath, search=None, full=False):
    def sort_key(index):
        return index[0]
        
    fp = open(filepath)
    nameList = []
    for fileLine, line in enumerate(fp):
        line = line.strip()
        if not "#" in line and line != "":
            tempList = line.split(",")
            if search != None:
                search = search.lower()
                lineTemp = line.lower()
                if search in lineTemp:
                    if full:
                        nameList.append((f"{tempList[0]}", f"{tempList[1]}", f"{tempList[2]}", f"{tempList[3]}", (fileLine)))
                    else:
                        nameList.append((f"{tempList[1]} {tempList[2]}", (fileLine)))
            else:
                if full:
                    nameList.append((f"{tempList[0]}", f"{tempList[1]}", f"{tempList[2]}", f"{tempList[3]}", (fileLine)))
                else:
                    nameList.append((f"{tempList[1]} {tempList[2]}", (fileLine)))
        
    fp.close()    
    nameList.sort(key=sort_key) # sort list by first name
    return nameList

def searchContactList(searchValue, searchParameter=None, returnParameter=None, contactsFile=cfg.contacts_file):
    searchValue = searchValue.lower()
    parameterIndex = -1
    if searchParameter != None:
        if searchParameter == "email":
            parameterIndex = 3
        elif searchParameter == "number":
            parameterIndex = 0
        elif searchParameter == "fName":
            parameterIndex = 1
        elif searchParameter == "lfName":
            parameterIndex = 2
        
    contactList = importContactsToList(contactsFile, full=True)
    
    for item in contactList:
        if parameterIndex >= 0:
            parameterValue = item[parameterIndex].lower()
        else:
            parameterValue = f"{item[0]} {item[1]} {item[2]} {item[3]}"
            parameterValue = parameterValue.lower()
            
        if searchValue in parameterValue:
            parameterIndex = -1
            if returnParameter != None:
                if returnParameter == "email":
                    return item[3]
                elif returnParameter == "number":
                    return item[0]
                elif returnParameter == "fName":
                    return item[1]
                elif returnParameter == "lfName":
                    return item[2]
                elif returnParameter == "name":
                    return f"{item[1]} {item[2]}"
            else:
                return item	# returns a tuple of the matching line
            
    return searchValue

def addNewContact(lcd):
    lcd.cls(True)
    
    lcd.setBorder(string=
                          f"Done Composing   [{cfg.alphaNumeric_enter_char}]\n"+
                          f"Backspace        [{cfg.alphaNumeric_backspace_char}]\n"+
                          f"Select Character [{cfg.alphaNumeric_select_char}]\n"+
                          f"Shift key        [{cfg.alphaNumeric_case_select_char}]", function="bottom")
    
    lcd.setBorder(string="Enter Contact Number", function="top")
    number = lcd.textEditor(True, numericalEntry=True)
    
    lcd.setBorder(string="Enter Contact First Name", function="top")
    first = lcd.textEditor(True)
    
    lcd.setBorder(string="Enter Contact Last Name", function="top")
    Last = lcd.textEditor(True)
    
    lcd.setBorder(string="Enter Contact Email Address", function="top")
    email = lcd.textEditor(True)
    
    tempStr = f"{number},{first},{Last},{email}\n"
    stringToFile(tempStr, cfg.contacts_file)
    
    return number, f"{first} {Last}"

def selectContact(lcd, contactType="mms"):
    contactList = []
    while True:
        lcd.cls(True)
        lcd.setBorder(string="Select Contact", function="top")
        lcd.setBorder(string=f"[{lcd.upKey}]: Up,   [{lcd.downKey}]: Down\n[{lcd.escKey}]: Exit, [{lcd.returnKey}]: Select\n[#]: Search", function="bottom")
        
        if len(contactList) == 0:
            contactList = importContactsToList(cfg.contacts_file, search=None)
            
        nameList = ["[ADD NEW CONTACT]"]
        for item in contactList:
            nameList.append(item[0])
        
        indexSelected = lcd.printList(nameList)
        # print(indexSelected)
        
        if indexSelected == 0:
            # number, name = addNewContact(lcd)
            number, name = addNewContact(lcd)
            break
        elif indexSelected >= 1:
            indexSelected-=1
            # print(contactList)
            fileLine = contactList[indexSelected][1]
            tempStr = readFileAtLine(cfg.contacts_file, fileLine)
            tempStr = tempStr.strip()
            tempList = tempStr.split(",")
            if contactType == "mms" or contactType == "signal":
                number = tempList[0]
            elif contactType == "email" or contactType == "e-mail":
                number = tempList[3]
            name = f"{tempList[1]} {tempList[2]}"
            break
        elif indexSelected == -4: # User selected to search for a contact
            contactList = []
            lcd.cls(True)
            lcd.setBorder(string="ENTER CONTACTS SEARCH STRING", function="top")
            lcd.setBorder(string=
                                  f"Search           [{cfg.alphaNumeric_enter_char}]\n"+
                                  f"Backspace        [{cfg.alphaNumeric_backspace_char}]\n"+
                                  f"Select Character [{cfg.alphaNumeric_select_char}]\n"+
                                  f"Shift key        [{cfg.alphaNumeric_case_select_char}]", function="bottom")
            
            searchString = lcd.textEditor(True)
            contactList = importContactsToList(cfg.contacts_file, search=searchString)
        
        else:
            number = "exit"
            name = "exit"
            break
    
    return (number, name)

def viewContacts(lcd):
    contactList = []
    while True:
        lcd.cls(True)
        lcd.setBorder(string="Contacts List", function="top")
        lcd.setBorder(string=f"[{lcd.upKey }]: Up      [{lcd.downKey}]: Down\n"+
                             f"[{lcd.escKey}]: Exit    [{lcd.returnKey}]: Edit\n"+
                             f"[#]: Search", function="bottom")
        
        if len(contactList) == 0:
            contactList = importContactsToList(cfg.contacts_file, search=None)
            lcd.print("Loading contacts...")
            
        nameList = ["[ADD NEW CONTACT]"]
        for item in contactList:
            nameList.append(item[0])
        
        indexSelected = lcd.printList(nameList)
        
        # print(indexSelected)
        
        if indexSelected == 0:
            
            number, name = addNewContact(lcd)
            break
        elif indexSelected >= 1:
            indexSelected-=1	# Subtract 1 because I placed "Add New Contact" to the top of the list...
            # print(contactList)
            fileLine = contactList[indexSelected][1]
            editContact(lcd, fileLine)
            contactList = []
            # tempList = tempStr.split(",")
            # number = tempList[0]
            # name = f"{tempList[1]} {tempList[2]}"
        elif indexSelected == -4: # User selected to search for a contact
            contactList = []
            lcd.cls(True)
            lcd.setBorder(string="ENTER CONTACTS SEARCH STRING", function="top")
            lcd.setBorder(string=
                                  f"Search           [{cfg.alphaNumeric_enter_char}]\n"+
                                  f"Backspace        [{cfg.alphaNumeric_backspace_char}]\n"+
                                  f"Select Character [{cfg.alphaNumeric_select_char}]\n"+
                                  f"Shift key        [{cfg.alphaNumeric_case_select_char}]", function="bottom")
            
            searchString = lcd.textEditor(True)
            contactList = importContactsToList(cfg.contacts_file, search=searchString)
        elif indexSelected == -5: # Unused
            pass
        elif indexSelected == -1:
            # User chose to exit
            return 0
   
def editContact(lcd, fileLine, contactsFile=cfg.contacts_file):
    def edit(parameter, OriginalValue):
        lcd.cls(clsA=True)
        lcd.setBorder(string=f"Edit {parameter}", function="top")
        lcd.setBorder(string=
                          f"Done             [{cfg.alphaNumeric_enter_char}]\n"+
                          f"Backspace        [{cfg.alphaNumeric_backspace_char}]\n"+
                          f"Select Character [{cfg.alphaNumeric_select_char}]\n"+
                          f"Shift key        [{cfg.alphaNumeric_case_select_char}]", function="bottom")
        newValue = lcd.textEditor()
        
        tempStr = f"Confirm Change?\n\nOld: {OriginalValue}\nNew: {newValue}"
        response = lcd.yesNoOther(message=tempStr, yes="Yes", no="No")
        if response == "D":
            return newValue
        else:
            return OriginalValue
        
    tempStr = readFileAtLine(contactsFile, fileLine)
    tempList = tempStr.split(",")
    valuesList = [tempList[0], tempList[1], tempList[2], tempList[3]]
    paramsList = ["Number", "First Name", "Last Name", "Email"]
    
    while True:
        number = valuesList[0]
        fName = valuesList[1]
        lName = valuesList[2]
        email = valuesList[3]
        dispList = [f"Number: {number}", f"First: {fName}", f"Last: {lName}", f"Email: {email}"]
        
        lcd.cls(clsA=True)
        lcd.setBorder(string=f"Edit {fName} {lName}", function="top")
        lcd.setBorder(string=f"[{lcd.upKey }]: Up     [{lcd.downKey}]: Down\n"+
                             f"[{lcd.escKey}]: Exit   [{lcd.returnKey}]: Edit\n"+
                             f"[#]: Delete Contact Entry",
                             function="bottom")
        
        indexSelected = lcd.printList(dispList, autoScroll=True, abbreviateScroll=False)
        if indexSelected >= 0:
            newValue = edit(paramsList[indexSelected], valuesList[indexSelected])
            valuesList[indexSelected] = newValue
        elif indexSelected == -4: # User selected to delete contact
            tempStr = f"Confirm Deletion?\n\n{number}\n{fName}\n{lName}\n{email}"
            response = lcd.yesNoOther(message=tempStr, yes="Yes", no="No")
            if response == "D":
                writeFileAtLine(contactsFile, fileLine, "")	# Replace contact with a blank line
                return 0
            else:
                pass
        elif indexSelected == -1:
            # User chose to exit (need to update file with new contact information)
            tempStr = f"{number},{fName},{lName},{email}"
            writeFileAtLine(contactsFile, fileLine, tempStr)
            return 0
        
def respondMsg(lcd, contact_number, contact_name, msgsType=""):
        
    compose = True
    while compose:
        lcd.cls(clsA=True)
        lcd.setBorder(string=f"{msgsType} COMPOSE TO\n {contact_name}\n{contact_number}", function="top", hBar=True)
        alphaNumeric_newline_char = "B"

        lcd.setBorder(string=
                      f"Done Composing   [{cfg.alphaNumeric_enter_char}]\n"+
                      f"Backspace        [{cfg.alphaNumeric_backspace_char}]\n"+
                      f"Select Character [{cfg.alphaNumeric_select_char}]\n"+
                      f"Shift key        [{cfg.alphaNumeric_case_select_char}]", function="bottom", hBar=True)
        
        msg = lcd.textEditor(True)
        
        response = lcd.yesNoOther(message="SEND MESSAGE?", other="Compose New")

        if response == lcd.returnKey:
            compose=False
        elif response == lcd.escKey:
            compose = False
            msg = ""
        elif response == lcd.upKey:
            msg = ""
    
    return msg

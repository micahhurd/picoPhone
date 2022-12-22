# Keypad Driver Version 0.002
import config as cfg
import standardLibrary as slib

def generateRecents(lcd):
    fp = open("./recentCallsLog.txt")
    numberList = [0, 0]
    nameList = ["[ENTER NUMBER]", "[CONTACTS]"]
    for fileLine, line in enumerate(fp):
        line = line.strip()
        if not "#" in line and line != "":
            tempList = line.split(",")
            name = f"{tempList[1]} {tempList[2]}"
            name = name.strip()
            if name == "":
                name = f"{tempList[0]}"
            
            # Apply inbound / outbound call indicator
            if tempList[3] == ">":
                tempList[3] = " ->"
            else:
                tempList[3] = " <- "
            
            if len(name) <= (lcd.xCharMax - len(tempList[3])):
                while len(name) < (lcd.xCharMax - len(tempList[3])):
                    name+=" "
            else:
                tempList[3] = "... " + tempList[3]
                while len(name) > (lcd.xCharMax - len(tempList[3])):
                    name = name[:1]
            name+=f"{tempList[3]}"
                
            nameList.append(name)
            numberList.append(f"{tempList[0]}")
    
    return (nameList, numberList)

def logCall(number):
    contact = slib.searchContactList(number)
    
    fName = ""
    lName = ""
    
    if slib.returnVarType(contact) == "tuple":
        fName = contact[1]
        lName = contact[2]
    
    toLog = f"{number},{fName},{lName},>"
    slib.writeFileAtLine("./recentCallsLog.txt", -1, toLog)
    # slib.stringToFile(toLog, "./recentCallsLog")
    
    
def placeCall(number):
    pass

def main(lcd, kpad):
    nameList, numberList = generateRecents(lcd)
    
    # Display the menu
    lcd.cls(clsA=True)
    lcd.setBorder(string=f"PHONE CALL", function="top")
    lcd.setBorder(string=f"[{lcd.upKey}]: Up,   [{lcd.downKey}]: Down\n[{lcd.escKey}]: Exit, [{lcd.returnKey}]: Select", function="bottom")
    
    # Display the nameList so the user can select
    indexSelected = -2
    while indexSelected < -1:
        indexSelected = lcd.printList(nameList)
        # print(indexSelected)
        
    if indexSelected == -1:
        return 0
    elif indexSelected == 0:
        numberToCall = lcd.phoneNumberEntry(kpad)
        
    elif indexSelected == 1:
        numberToCall, name = slib.selectContact(lcd)
    else:
        numberToCall = numberList[indexSelected]
    
    logCall(numberToCall)	# Put the call into the recent calls log
    placeCall(numberToCall)	# Initiate the call
    
            
    
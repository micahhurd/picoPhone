import lcdDriver
import keypadDriver
import config as cfg


def numericalEntry(lcd, kpad, banner="Enter Text Below:\\n",
              allowedChar = ["1","2","3","4","5","6","7","8","9","0"],
              enterChar="D", bSpace="#"):
    
    if banner != None:
        lcd.print(banner)
    tempStr = ""
    while True:
        char = kpad.keyIn()
        if char == enterChar:
            break
        elif char == bSpace:
            lcd.print("\\d")
        elif char in allowedChar:
            tempStr+=char
            lcd.print(char)
    return tempStr

def alphaEntry(lcd, kpad, banner="Enter Text Below:\\n",
                      collectedStr = ""):
    pip = lcd.dispWriteLowestLevel # pip stands for "Print In Place"
    if banner != None:
        lcd.print(banner)
        
    dictionary = {
        "": " ",
        "1": ".",
        "11": ",",
        "111": "'",
        "2": "A",
        "22": "B",
        "222": "C",
        "3": "D",
        "33": "E",
        "333": "F",
        "4": "G",
        "44": "H",
        "444": "I",
        "5": "J",
        "55": "K",
        "555": "L",
        "6": "M",
        "66": "N",
        "666": "O",
        "7": "P",
        "77": "Q",
        "777": "R",
        "7777": "S",
        "8": "T",
        "88": "U",
        "888": "V",
        "9": "W",
        "99": "X",
        "999": "Y",
        "9999": "Z",
        "A": "A",
        "B": "B",
        "C": "C",
        "D": "D",
        "*": "*",
        "#": "#",
        }
    
    collect = True
    while collect == True:
    
        tempStr = ""
        pendingQue =""
        char = ""
        gotSelectedChar = False
        gotEnterChar = False
        gotBspaceChar = False
        
        while True:
               
            if tempStr == "":
                char = kpad.keyIn()
                lcd.cursor(0)
            else:
                char = kpad.keyIn(cursorOn=0)
            lcd.cursor(0)               
            
            if char == "*":
                if tempStr == "":
                    pendingQue = dictionary[tempStr]
                collectedStr += pendingQue
                lcd.print(f"\\r{collectedStr}")
                tempStr = ""
                pendingQue = ""
                break
            elif char == "#" and (len(collectedStr) > 0):
                if pendingQue == "":
                    collectedStr = collectedStr[:-1]
                    tempStr = ""
                    pip(" ")
                    lcd.print(f"\\r{collectedStr}")
                else:
                    tempStr = ""
                    pendingQue = ""
                    pip(" ")
                    lcd.cursor(1)
            elif char == "D":
                if pendingQue != "":
                    collectedStr+=pendingQue
                
                return collectedStr
            else:
            
                if (not char in tempStr) and (len(tempStr) > 0):
                    tempStr = char
                else:
                    tempStr+=char
                    
                if (not tempStr in dictionary):
                    if tempStr[-1] in dictionary:
                        tempStr = tempStr[-1]
                    else:
                        tempStr = ""
                
                pendingQue = dictionary[tempStr]
                if pendingQue == " ":
                    pip("_>")
                else:
                    pip(pendingQue)
            
   
           
                
            
            
        
def cursorOnOff(lcd):
    while True:
        lcd.print("test")
        tempStr = int(input("cursor on(1) or off(0)? "))
        if tempStr == 1:
            lcd.cursor(1)
        else:
            lcd.cursor(0)
                    
    
        
    
    
    


# lcd = lcdDriver.display()
# keypad = keypadDriver.keypad(lcd=lcd)
# cursorOnOff(lcd)

# string = alphaNumericEntry(lcd, keypad)
# print(f"\\aUser Entered String: {string}")
# lcd.print(f"\\aUser Entered String: {string}") 
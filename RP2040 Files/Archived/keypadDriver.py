# Keypad Driver Version 1.03
# keyIn function is broken
from machine import Pin, Timer
import utime
import config as cfg
import standardLibrary as slib
    
class keypad:

    def __init__(self, lcd=None):
        self.lcd = lcd
        self.lowerCase = False

        # define PINs according to cabling

        self.row_list = [4, 5, 8, 9]
        self.col_list = [3, 2, 1, 0]
        self.keyCaptured = None
        # self.lcdCursorFunction = lcd.cursor
        
        self.dictionaryNumerical = {
            "": " ",
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "9": "9",
            "0": "0",
            "00": "+",
        }
        self.dictionaryUpper = {
            "": " ",
            "1": ".",
            "11": ",",
            "111": "'",
            "1111": "1",
            "2": "A",
            "22": "B",
            "222": "C",
            "2222": "2",
            "3": "D",
            "33": "E",
            "333": "F",
            "3333": "3",
            "4": "G",
            "44": "H",
            "444": "I",
            "4444": "4",
            "5": "J",
            "55": "K",
            "555": "L",
            "5555": "5",
            "6": "M",
            "66": "N",
            "666": "O",
            "6666": "6",
            "7": "P",
            "77": "Q",
            "777": "R",
            "7777": "S",
            "77777": "7",
            "8": "T",
            "88": "U",
            "888": "V",
            "8888": "8",
            "9": "W",
            "99": "X",
            "999": "Y",
            "9999": "Z",
            "99999": "9",
            "0": "0",
            "00": "@",
            "000": "+",
            "0000": "-",
            "00000": "%",
            "000000": "$",
            "A": "A",
            "B": "B",
            "C": "C",
            "D": "D",
            "*": "*",
            "#": "#",
            }
        

        # set row pins to output and change array elements from
        #    int to Pin objects, all set to high
        for x in range(0,4):
            self.row_list[x]=Pin(self.row_list[x], Pin.OUT)
            self.row_list[x].value(1)

        # set columns pins to input and change array elements 
        #   from int to Pin objects. We'll read user input here
        for x in range(0,4):
            self.col_list[x] = Pin(self.col_list[x], Pin.IN, Pin.PULL_UP)

        # Create a map between keypad buttons and chars
        self.key_map=[["D","#","0","*"],\
                 ["C","9","8","7"],\
                 ["B","6","5","4"],\
                 ["A","3","2","1"]]
        
        self.startPolling()
        
        
    def pollKeypad(self):
        def Keypad4x4Read(cols,rows):
            for r in rows:
                r.value(0)
                result=[cols[0].value(),cols[1].value(),cols[2].value(),cols[3].value()]
                if min(result)==0:
                    key=self.key_map[int(rows.index(r))][int(result.index(0))]
                    r.value(1) # manages key keept pressed
                    return(key)
                r.value(1)       
       
        self.keyCaptured=Keypad4x4Read(self.col_list, self.row_list)
        
        if self.keyCaptured != None:
            if self.lcd != None:
                if self.lcd.ledPin.value() == 0:
                    self.keyCaptured = None
                    self.lcd.displayOnOff(True)
                self.lcd.last_key_press_ts = slib.getCurrentTS()
          # print("You pressed: "+self.keyCaptured)
          
            utime.sleep(0.2) # gives user enough time to release without having double inputs

    
    def startPolling(self):
        # timer_two = Timer()
        # print("--- Ready to get user inputs ---")
        timer = Timer(-1)
        timer.init(freq=1, mode=Timer.PERIODIC, callback=lambda t:self.pollKeypad())        
        
    def keyIn(self):
        # print(text)
        while True:
            # print(f"keyCaptured >{self.keyCaptured}<")
            self.pollKeypad()
            # print(f"keyCaptured >{self.keyCaptured}<")
            if self.keyCaptured != None:
                returnKey = self.keyCaptured
                self.keyCaptured = None
                # self.keyCaptured = None
                break
        
        return returnKey
    
    def numericalEntry(self, banner="Enter Text Below:\\n",
              allowedChar = ["1","2","3","4","5","6","7","8","9","0","A","B","C"],
              enterChar="D", bSpace="#"):
    
        if banner != None:
            self.lcd.print(banner)
        tempStr = ""
        while True:
            char = self.keyIn()
            if char == enterChar:
                break
            elif char == bSpace:
                if len(tempStr) > 0:
                    self.lcd.print("\\d")
                    tempStr = tempStr[:-1]
            elif char in allowedChar:
                tempStr+=char
                self.lcd.print(char)
        return tempStr
    
    
    def alphaNumericInput(self, lcd, numerical=False):
        #if self.lowerCase:
        #    dictionary = self.dictionaryLower
        #else:
        if numerical:
            dictionary = self.dictionaryNumerical
        else:
            dictionary = self.dictionaryUpper
            
        tempStr = ""
        returnChar = ""
        tempCursorEnabledBool = lcd.cursorEnable
        while True:
            try:
                string = dictionary[tempStr]
            except:
                tempStr = lastChar
                try:
                    string = dictionary[tempStr]
                except:
                    pass
            
            if tempCursorEnabledBool:
                lcd.cursorEnable = False
            if self.lowerCase:    
                string = string.lower()
            lcd.printLowLevel(string, x=lcd.cursorX, y=lcd.cursorY)
            if tempCursorEnabledBool:
                lcd.cursorEnable = True
            
            if tempStr == "":
                lcd.cursorType = 0
            else:
                lcd.cursorType = 1
            char = self.keyIn()
            if char == cfg.alphaNumeric_select_char:
                returnChar = dictionary[tempStr]
                if self.lowerCase:
                    returnChar = returnChar.lower()
                break
            elif char == cfg.alphaNumeric_newline_char:
                returnChar = "\n"
                break
            elif char == cfg.alphaNumeric_case_select_char:
                self.lowerCase = not self.lowerCase
                # returnChar = "\c"
                # break
            elif char == cfg.alphaNumeric_backspace_char:
                returnChar = "\b"
                break
            elif char == cfg.alphaNumeric_enter_char:
                returnChar = "\n\r"
                break
            else:
                tempStr += char
                lastChar = char
        return returnChar
            
    
    def alphaEntryLCD(self, banner="Enter Text Below:\\n",
                          collectedStr = ""):
        
        self.lcd.cursorType = 1 # Apply a non-standard cursor type
        pip = self.lcd.dispWriteLowestLevel # pip stands for "Print In Place"
        if banner != None:
            self.lcd.print(banner)
        
        
        collect = True
        while collect == True:
        
            tempStr = ""
            pendingQue =""
            char = ""
            gotSelectedChar = False
            gotEnterChar = False
            gotBspaceChar = False
            
            while True:
                   
                char = self.keyIn()
                                
                if char == "*":
                    if tempStr == "":
                        pendingQue = self.dictionaryUpper[tempStr]
                    collectedStr += pendingQue
                    # self.lcd.print(f"\\r{collectedStr}")
                    self.lcd.print(pendingQue)
                    tempStr = ""
                    pendingQue = ""
                    break
                elif char == "#" and (len(collectedStr) > 0):
                    if pendingQue == "":
                        collectedStr = collectedStr[:-1]
                        tempStr = ""
                        self.lcd.print("\\d")
                    else:
                        tempStr = ""
                        pendingQue = ""
                        pip(" ")
                        # self.lcd.cursor(1)
                elif char == "D":
                    if pendingQue != "":
                        collectedStr+=pendingQue
                    
                    collect = False
                    break
                else:
                
                    if (not char in tempStr) and (len(tempStr) > 0):
                        tempStr = char
                    else:
                        tempStr+=char
                        
                    if (not tempStr in self.dictionaryUpper):
                        if tempStr[-1] in self.dictionaryUpper:
                            tempStr = tempStr[-1]
                        else:
                            tempStr = ""
                    
                    pendingQue = self.dictionaryUpper[tempStr]
                    if pendingQue == " ":
                        pip("_>")
                    else:
                        pip(pendingQue)
                
        self.lcd.cursorType = 0
        return collectedStr
      
        

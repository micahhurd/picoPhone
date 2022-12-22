# lcdDriver add-on, Version 0.004

# ToDo:
# Load in a multipage string, and have the user pick-up editing anywhere in it
# he desires

import lcdDriver
import standardLibrary as slib
import config as cfg
import keypadDriver
import utime



def textEditor(cursorOn=True):
    self=lcd
    def handleNewChar(newChar, currentLineStr, xPos, cursorOn):
        print(f"newChar >{newChar}<")
        printLastLine = False
        printNextLine = False
        
        if newChar == "\c":
            if self.keyCtrl != None:
                self.keyCtrl.lowerCase = not self.keyCtrl.lowerCase
        elif "\n" in newChar:
                                        
            if self.yCounter == end: # yCharMax is not zero based
                
                self.getFromWriteToDispBuffer(self.yCounter, string=currentLineStr) # Insert current line into display buffer
                currentLineStr = ""
                self.scrollDisplay(1) # Make space for a new line
                self.printLowLevel(self.blankLine, x=0, y=self.yCounter) # clear the line of text
            else:
                
                self.getFromWriteToDispBuffer(self.yCounter, string=currentLineStr) # Insert current line into display buffer
                currentLineStr = ""
                self.yCounter+=1
                xPos = 0
                    
        elif newChar == "\b":
            # print("bspace")
            # ToDo: handle situation where the user backspaces to a previous line
            xPos-=1
            # print(f"xPos1: {xPos}")
            if xPos < 0: # handle situations where x needs to go to the previous line
                if self.yCounter > start:
                    # print("going back one line")
                    self.printLowLevel(self.blankLine, x=0, y=self.yCounter) # clear the line of text
                    self.yCounter-=1
                    # print(f"yCounter: {self.yCounter}")
                    currentLineStr = self.getFromWriteToDispBuffer(self.yCounter)
                    self.cls(key=self.yCounter)
                    # print(f"currentLineStr: {currentLineStr}")
                    xPos = self.xCharMax-1 # xCharMax is not zero based; set cursor position to end of line
                    # print(f"xPos2: {xPos}")
                else:
                    self.yCounter = start
                    xPos = 0
                    currentLineStr = ""
            else:
                currentLineStr = currentLineStr[:-1] # Delete the last character
                # print(currentLineStr)
        else:
            if len(currentLineStr) >= self.xCharMax:  # Situation where there is no more room on the screen to append a character
                
                if self.yCounter == end: # yCharMax is not zero based
                    
                    self.getFromWriteToDispBuffer(self.yCounter, string=currentLineStr) # Insert current line into display buffer
                    currentLineStr = ""
                    self.scrollDisplay(1) # Make space for a new line
                    self.printLowLevel(self.blankLine, x=0, y=self.yCounter) # clear the line of text
                    xPos = 1
                    currentLineStr+=newChar
                    
                else:
                    print(f"currentLineStr >{currentLineStr}<, yCounter: {self.yCounter}")
                    
                    self.getFromWriteToDispBuffer(self.yCounter, string=currentLineStr) # Insert current line into display buffer
                    currentLineStr = ""
                    self.yCounter+=1
                    xPos = 0
                    currentLineStr+=newChar
            
            else:   # Situation where the character can be added to the currentLine without issue
                currentLineStr+=newChar
                xPos = len(currentLineStr) - 1
        
        print(f"currentLineStr {currentLineStr}")
        # self.printLineLowLevel(self.blankLine, self.yCounter)
        # self.printLineLowLevel(currentLineStr, self.yCounter) # Update display
        self.printLowLevel(self.blankLine, x=0, y=self.yCounter)
        self.printLowLevel(currentLineStr, x=0, y=self.yCounter) # Update display
        
        
        # print(f"self.yCounter {self.yCounter}, self.cursorY {self.cursorY}, self.yCharMax {self.yCharMax}")
        
        if cursorOn:
            # increment to ensure the cursor stays in the window:
            if len(currentLineStr) >= self.xCharMax and self.yCounter == end:
                self.getFromWriteToDispBuffer(self.yCounter, string=currentLineStr) # Insert current line into display buffer
                currentLineStr = ""
                self.scrollDisplay(1) # Make space for a new line
                self.printLowLevel(self.blankLine, x=0, y=self.yCounter) # clear the line of text
                xPos = 1
        
        self.cursorX = len(currentLineStr)
        self.cursorY = self.yCounter
        
        return currentLineStr, xPos
    
    if cursorOn:
        self.initCursor()
        self.enableCursor()
    
    start, end, qtyAvailable = self.unlockedBufferLines()
    self.yCounter = start
    edit = True
    currentLineStr = ""
    self.cursorY = start
    self.cursorX = 0
    xPos = 0
    self.initCursor()
    
    while edit:
        if cursorOn:
            self.enableCursor(True)
        
        # print(f"x, y - {self.cursorX}, {self.cursorY}")
        char = self.getInputAZ()	# Get the keyboard/Keypad input
        if cursorOn:
            self.enableCursor(False)
            
        if char == "\n\r":
            edit = False
            break
        
        currentLineStr, xPos = handleNewChar(char, currentLineStr, xPos, cursorOn)
        
    
    # ToDo: Put in logic to capture all characters from:
    completeList = []
    if len(self.bufferTxtAbove) > 0 :
        completeList+=self.bufferTxtAbove
    
    for key in range(start, self.cursorY):
        completeList.append(self.dispBuffer[key][6])
    
    if len(currentLineStr) > 0:
        completeList.append(currentLineStr)
    
    if len(self.bufferTxtBelow) > 0 :
        completeList+=self.bufferTxtBelow
    
    outputStr = ""
    for line in completeList:
        outputStr+= f"{line}"
    
    return outputStr
    
    
    
lcd = lcdDriver.dispDriver()        
kpd = keypadDriver.keypad()
lcd.keyCtrl = kpd


#while True:
#    tempStr = kpd.alphaNumericInput(lcd)
#    print(f"Char >{tempStr}<")
        
    
# lcd.setBorder(string="FROM: Chatty Kathy\nTest", function="top")
# lcd.setBorder(string="This is some text\nTo test the bottom", function="bottom")

# lcd.print(cfg.multiLine2)

while True:
    str = lcd.getInput16()
    print(str)


    
        
        
        
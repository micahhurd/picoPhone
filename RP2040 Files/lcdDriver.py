# LCD Driver Version 1.14
# ToDo
# Fix textEditor() to include the last character when completing the sentence, even when it was
# not applied using the select key (I believe this is done)
# Fix printList() to scroll all the way to top / bottom when abbreciate scroll is True
# Add screen on / off control (Done)

from machine import Pin, SPI, Timer
import utime

import ili9341
from ili9341 import color565

import standardLibrary as slib
import config as cfg
# class dispDriver
# displayOnOff(self, state)
# calc_maxLines()
# yRemainder()
# incrementY()
# clsLine(fontWidth=None)
# printLBL(self, string, startLine=0, lock=False)
# printLineLowLevel(string, lineIndex, ignoreWriteLock=False)
# horizontal_bar(self, text=None, alignment=0, lock=False)
# cls(clsA=False)
# clsBuffer(clsA=False)
# getInput16()
# getInputAZ()
# setBorder(string=None, function="top", hBar=True, qtyLinesPadding=None)
# printLowLevel(string, fontRGB=None, backRGB=None)
# buildDispBuffer()
# getFromWriteToDispBuffer(lineIndex, string=None, returnNull=True)
# scrollDisplay(self, direction)
# printBuffer(self, string=None, indexToPrint=None, printOverLockedLines=False)
# writtenBufferLines(self)
# unlockedBufferLines(self, filterByUnwritten=False)
# getOrSetSelectedBufferLine(self, setLine=None)
# getListItem(self, list_to_check, index)
# insertIntoBuffer(self, displayList, overwrite=True)
# writeUnwrittenBufferLines(self, overWriteLocked=False)
# manageMsgBuffer(self, strList, abbreviateScroll)
# printMsgs(self, string, autoScroll=True, abbreviateScroll=False)
# manageListBuffer(self, strList)
# printList(self, string, autoScroll=True, abbreviateScroll=False)
# print(self, string, end="\n", pause=False, autoScrollInterval=0.1, autoCLS=False)
# textEditor(self, cursorOn=True)
# yesNoOther(self, message="", yes="Yes", no="No", other=None)
# phoneNumberEntry(self, kpad...
# initCursor(self)
# blinkCursor(self, timer)
# cursorFill(self, background)
# 


TFT_CLK_PIN = const(6)
TFT_MOSI_PIN = const(7)
TFT_MISO_PIN = const(4)

TFT_CS_PIN = const(13)
TFT_RST_PIN = const(14)
TFT_DC_PIN = const(15)

LED_ENABLE_PIN = const(22) # GPIO Pin number, not physical pin number

class dispDriver:
    
    def __init__(self):
        
        self.xCounter = 0
        self.yCounter = 0
        self.xCharMax = 0
        self.yCharMax = 0
        self.dispBuffer = {}
        self.fontColorR = cfg.fontColors[cfg.font_color][0]
        self.fontColorG = cfg.fontColors[cfg.font_color][1]
        self.fontColorB = cfg.fontColors[cfg.font_color][2]
        self.backGroundR = cfg.fontColors[cfg.background][0]
        self.backGroundG = cfg.fontColors[cfg.background][1]
        self.backGroundB = cfg.fontColors[cfg.background][2]
        self.fontBitWidth = 8
        self.fontBitHeight = 8
        self.selectedFont = None
        self.keyCtrl = None
        self.upKey = "A"
        self.downKey = "B"
        self.escKey = "C"
        self.returnKey = "D"
        self.ctrlCharList = ["#0"]
        self.cursorEnable = False
        self.cursorToggle = False
        self.cursorRunning = False
        self.bufferTxtAbove = []
        self.bufferTxtBelow = []
        self.cursorX = 0
        self.cursorY = 0
        self.cursorType = 0
        self.ledPin=Pin(LED_ENABLE_PIN, Pin.OUT)
        self.last_key_press_ts = slib.getCurrentTS()
        self.backlight_current_ts = 0
        
        
        
        # ===============================================================================================
        spi = SPI(0, baudrate=40000000, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
        self.dispObj = ili9341.Display(spi, dc=Pin(TFT_DC_PIN), cs=Pin(TFT_CS_PIN), rst=Pin(TFT_RST_PIN),
                                  width=cfg.display_sizeX, height=cfg.display_sizeY)
        self.dispObj.clear(color=color565(self.backGroundR, self.backGroundG, self.backGroundB))
        self.xCharMax = int(cfg.display_sizeX / self.fontBitWidth)
        # self.xCharMax = (30)
        self.yCharMax = int(cfg.display_sizeY / self.fontBitHeight)
        self.blankLine = slib.equalizeLine(" ", self.xCharMax)
        self.buildDispBuffer()
        self.ledPin.value(1)
                
    def displayOnOff(self, state):
        
        if state == True:
            self.ledPin.value(1)
        elif state == False:
            self.ledPin.value(0)
    
    def calc_maxLines(self):
        # print("in calc_maxLines")
        temp = int(self.dispObj.height / self.fontBitHeight)
        # print(f"temp {temp}")
        return temp
    
    def yRemainder(self):
        return self.yCharMax - self.yCounter + 1
    
    def incrementY(self):
        self.xCounter = 0
        if self.yRemainder() > 0:
            self.yCounter += 1
        else:
            self.clsLine()
    
    def clsLine(self, fontWidth=None):
        if fontWidth == None:
            fontWidth = self.fontBitWidth
        
        textString = " " * self.xCharMax
        self.dispObj.draw_text8x8(0, self.yCounter, textString,
              color565(self.backGroundR, self.backGroundG, self.backGroundB))
    
    def printLBL(self, string, startLine=0, lock=False):
        self.yCounter = startLine
        strList = slib.convertStringToList(string, self.xCharMax)
        for item in strList:
            if lock:
                self.dispBuffer[self.yCounter][0] = True	# Lock the line for writing
            self.printLowLevel(item)
            self.incrementY()
    
    def printLineLowLevel(self, string, lineIndex, ignoreWriteLock=False):
        if self.dispBuffer[lineIndex][0] == False or ignoreWriteLock:
            tempY = self.yCounter
            tempX = self.xCounter
            self.yCounter = lineIndex
            if len(string) != self.xCharMax:
                string = slib.equalizeLine(string, self.xCharMax)
            self.printLowLevel(string, x=0)
            self.yCounter = tempY
            self.xCounter = tempX
            
    def horizontal_bar(self, text=None, alignment=0, lock=False):
        if not text == None:
            text = text.strip()
            # input(f">{text}<")
            if text == "":
                text = None
                
        self.xCounter=0            
        startY = (self.yCounter*self.fontBitHeight) + 2
        height = self.fontBitHeight - 4
        
        self.dispObj.fill_hrect(0, startY, self.dispObj.width, height,
                               color565(self.fontColorR, self.fontColorG, self.fontColorB))
        if lock:
            self.dispBuffer[self.yCounter][0] = True	# Lock the line for writing
        if text is not None:
            
            if alignment == 1:	# Center Justified
                                   
                text = f" {text} "
                tempInt = (self.xCharMax - (self.xCharMax % 2)) / 2 # Get half of one full line
                
                textLen = len(text)
                textLen = (textLen - (textLen % 2)) / 2 # Get half of of the string to be written
                pad = int(tempInt - textLen)
                                
            elif alignment == 0: # Left justified
                text = f"{text} "
                pad = 0
                
            temp_int = self.xCounter
            self.xCounter = pad
            
            self.printLowLevel(text)
            self.xCounter = temp_int
        
        self.incrementY()
    
    def cls(self, clsA=False, key=None):
        self.clsBuffer(clsA=clsA, key=key)
    
    def clsBuffer(self, clsA=False, key=None):
        # clears text and highlighting of unlocked lines; does not touch other unless clsA = True
        
        if key == None:
            for key in self.dispBuffer:
                if clsA:
                   self.dispBuffer[key][0] = False 
                
                self.yCounter = key
                if self.dispBuffer[key][0] == False:
                    self.dispBuffer[key][1] = False
                    self.dispBuffer[key][2] = False
                    self.dispBuffer[key][3] = False
                    self.dispBuffer[key][7] = False
                    
                    fontRGB = self.dispBuffer[key][4]
                    backgrounRGB = self.dispBuffer[key][5]
                    
                    self.dispBuffer[key][6] = self.blankLine
                    self.printLowLevel(self.blankLine, fontRGB, backgrounRGB)
        else:
            if clsA:
               self.dispBuffer[key][0] = False 
            
            self.yCounter = key
            if self.dispBuffer[key][0] == False:
                self.dispBuffer[key][1] = False
                self.dispBuffer[key][2] = False
                self.dispBuffer[key][3] = False
                
                fontRGB = self.dispBuffer[key][4]
                backgrounRGB = self.dispBuffer[key][5]
                
                self.dispBuffer[key][6] = self.blankLine
                self.printLowLevel(self.blankLine, fontRGB, backgrounRGB)
    
    def getInput16(self):
        # This can only get the base keys from the 4x4 keypad
        if self.keyCtrl == None:
            key = input(f"Input: ") # replace with keypad input
        else:
            key = self.keyCtrl.keyIn()
        return key
    
    def getInputAZ(self, numericalOnly=False):
        # This gets alphanumeric entry from the keypad (hence AZ: A to Z...)
        if self.keyCtrl == None:
            key = input(f"Input: ") # replace with keypad input
        else:
            key = self.keyCtrl.alphaNumericInput(self, numerical=numericalOnly)
        return key
    
    def setBorder(self, string=None, function="top", hBar=True, qtyLinesPadding=None):
       
        # Determine the number of lines needed to incorporate the given string
        if string!= None:
            qtyLinesNeeded = slib.calc_lines_needed_to_print(string, self.xCharMax)
            
            if qtyLinesPadding != None:
                if qtyLinesPadding > qtyLinesNeeded:
                    qtyLinesNeeded = qtyLinesPadding
        # ===================================================================
        
        # self.xCounter = 0 # Print characters at the str
        if function == "clsTop":
            key = 0
            while True:
                if self.dispBuffer[key][0] == True:
                    tempStr = self.blankLine
                    self.dispBuffer[key][0] = False
                    self.dispBuffer[key][6] = tempStr
                    self.printBuffer(indexToPrint=key)
                    key+=1
                else:
                    break
                
        elif function == "clsBottom":
            key = list(self.dispBuffer)[-1]
            while True:
                if self.dispBuffer[key][0] == True:
                    tempStr = self.blankLine
                    self.dispBuffer[key][0] = False
                    self.dispBuffer[key][6] = tempStr
                    self.printBuffer(indexToPrint=key)
                    key-=1
                else:
                    break
            
        elif function == "top":
            self.yCounter = 0
            self.borderTop = 0
            self.printLBL(string, lock=True)
            if hBar:
                self.horizontal_bar(lock=True)
            if self.xCounter > 0:
                self.incrementY()
            self.borderTop = self.yCounter
            
            
        elif function == "bottom":
            self.borderBottom = 0            
            
            self.yCounter = (self.calc_maxLines()) - qtyLinesNeeded
            if hBar:
                self.yCounter-=1
                qtyLinesNeeded+=1
                self.horizontal_bar(lock=True)
                
            self.printLBL(string, self.yCounter, lock=True)
            self.borderBottom = qtyLinesNeeded
        # self.resetY()
        # self.setYCharMax()

    # def printLowLevel(self, string, fontR=self.fontColorR, fontG=self.fontColorG, fontB=self.fontColorB, backR=self.backGroundR, backG=self.backGroundG, backB=self.backGroundB):
    def printLowLevel(self, string, fontRGB=None, backRGB=None, x=None, y=None):
        if x != None:
            xLoc = x
        else:
            xLoc = self.xCounter
        
        if y != None:
            yLoc = y
        else:
            yLoc = self.yCounter
        
        if fontRGB == None:
            fontR = self.fontColorR
            fontG = self.fontColorG
            fontB = self.fontColorB
        else:
            fontR = fontRGB[0]
            fontG = fontRGB[1]
            fontB = fontRGB[2]
            
        if backRGB == None:
            backR = self.backGroundR
            backG = self.backGroundG
            backB = self.backGroundB
        else:
            backR = backRGB[0]
            backG = backRGB[1]
            backB = backRGB[2]           
       
        if self.selectedFont == None:
            # Uses the built-in Micropython 8x8 font
            self.dispObj.draw_text8x8((xLoc * self.fontBitWidth), (yLoc * self.fontBitHeight), string,
                  color565(fontR, fontG, fontB),
                                      background=color565(backR, backG, backB))
        else:
            self.dispObj.draw_text((xLoc * self.fontBitWidth), (yLoc * self.fontBitHeight), string,
                                      self.selectedFont,
                  color565(fontR, fontG, fontB))
            
    def buildDispBuffer(self):
        # Format of buffer diction key value pair:
        # Key = line number of the display
        # Value = list of elements:
        # Index 0: [bool if the line is write-locked]
        # Index 1: [bool if line is not null; false =  Null, true=Not Null]
        # Index 2: [bool if the line is selected]
        # Index 3: [bool Invert the line color]
        # Index 4: [tupple csv font color]
        # Index 5: [tupple csv background color]
        # Index 6: [string of text to print]
        # Index 7: [bool if line has been written to display]
        
        # nullString = slib.equalizeLine(" ", self.xCharMax-2)
        nullString = slib.equalizeLine(" ", self.xCharMax)
        for i in range(self.yCharMax):
            self.dispBuffer.update( {i : [False, False, False, False, (self.fontColorR, self.fontColorG, self.fontColorB), (self.backGroundR, self.backGroundG, self.backGroundB), f"{nullString}", False]} )
         
    def getFromWriteToDispBuffer(self, lineIndex, string=None, returnNull=True):
        # if index = None then it will return the string from the selected line
        # DOES NOT UPDATE DISPLAY OUTPUT WITH NEW LINES. Call writeUnwrittenBufferLines()
        if string == None:
            if lineIndex >= 0 and lineIndex < self.yCharMax:
                # print(f">{lineIndex} {self.dispBuffer[lineIndex]}<")
                if self.dispBuffer[lineIndex][1] == True or returnNull:
                    # print(f">{self.dispBuffer[lineIndex][6]}<")
                    return self.dispBuffer[lineIndex][6]
                else:
                    return ""
            else:
                return ""
        else:
            if lineIndex >= 0 and lineIndex < self.yCharMax and self.dispBuffer[lineIndex][0] == False:
                string = slib.equalizeLine(string, self.xCharMax)
                self.dispBuffer[lineIndex][1] = True
                self.dispBuffer[lineIndex][6] = string
                self.dispBuffer[lineIndex][7] = False
    
    def scrollDisplay(self, direction):
    
        start, end, qtyAvailable = self.unlockedBufferLines()
        
        if direction > 0:
            for i in range(direction):
                key = start + i
                self.bufferTxtAbove.append(self.getFromWriteToDispBuffer(key))

            for i in range(start, (end+1)):   # This will shift lines upward

                keySource = i+direction   # The index of the source line
                keyDest = keySource - direction          # The index of the destination line
                # keyDest = keySource + direction          # The index of the destination line
                if keySource > end:
                    break   # Make sure not to go beyond the dispBuffer bounderies
                
                
                tempStr = self.getFromWriteToDispBuffer(keySource)
                nullFlag = self.dispBuffer[keySource][1]
                self.dispBuffer[keySource][1] = False
                self.dispBuffer[keySource][6] = self.blankLine
                self.dispBuffer[keySource][7] = False
                
                self.dispBuffer[keyDest][1] = nullFlag
                self.dispBuffer[keyDest][6] = tempStr
                self.dispBuffer[keyDest][7] = False
            
            for i in range(direction):   # Get lines from the off display buffer
                key = (end+1) - direction + i
                try:
                    tempStr = self.bufferTxtBelow[0]
                    del self.bufferTxtBelow[0]
                    notNull = True
                except:
                    notNull = False
                    tempStr = self.blankLine
                    self.dispBuffer[key][1] = False
                    self.dispBuffer[key][7] = False
                
                self.dispBuffer[key][1] = notNull
                self.dispBuffer[key][6] = tempStr
                
        else:
            
            absDir = abs(direction)
            for i in range(absDir):            
                key = end - i
                if self.dispBuffer[key][1]:
                    self.bufferTxtBelow.insert(0, self.dispBuffer[key][6])
                     
            for i in range((end+1) - start):   # Will be used to shift all lines downward
                
                keySource = end - absDir -  i
                keyDest = keySource+absDir
                if keySource < 0:   # Ensure boundaries of the dispBuffer are not exceeded
                    break
                
                tempStr = self.getFromWriteToDispBuffer(keySource)
                nullFlag = self.dispBuffer[keySource][1]
                self.dispBuffer[keySource][1] = False
                self.dispBuffer[keySource][6] = self.blankLine
                self.dispBuffer[keySource][7] = False
            
                self.dispBuffer[keyDest][1] = nullFlag
                self.dispBuffer[keyDest][6] = tempStr
                self.dispBuffer[keyDest][7] = False
            
            for i in range(absDir):
                try:
                    tempStr = self.bufferTxtAbove[-1]
                    del self.bufferTxtAbove[-1]
                    notNull = True
                except:
                    notNull = False
                    tempStr = self.blankLine
                    
                key = start + (absDir-1) - i
                self.dispBuffer[key][1] = notNull
                self.dispBuffer[key][6] = tempStr
                self.dispBuffer[key][7] = False
                
        # send all lines that were changed to the display
        self.writeUnwrittenBufferLines(overWriteLocked=False)
    
    def printBuffer(self, string=None, indexToPrint=None, printOverLockedLines=False):
        # Handles writing to the buffer. If indexToPrint is none then all lines in the
        # buffer are written to the display, otherwise if a value is passed to indexToPrint
        # then only that line is written.
        # In the case a value is passed to indexToPrint, if string is passed a value then
        # that line is updated with the contents of string, otherwise it will pull the value
        # already existing at that line and re-print it.
        def handleDisplay(currString):
            foundCrtlChar = ""
            for ctrlChar in self.ctrlCharList:
                if ctrlChar in currString:
                    foundCrtlChar = ctrlChar
                    break
            if foundCrtlChar != "":
                if foundCrtlChar == "#0":
                    currString = currString.strip(foundCrtlChar)
                    currString = currString.strip()
                    self.horizontal_bar(text=currString, alignment=1, lock=False)
            else:
                # print(f"right before writing: {currString}")
                self.printLowLevel(currString, fontRGB, backgrounRGB)
            
        # input(f"{self.xCharMax}")
        if indexToPrint == None:
            for key in self.dispBuffer:
                self.yCounter = key
                if self.dispBuffer[key][0] == False:
                    # isNotNull = self.dispBuffer[key][1]
                    isSelected = self.dispBuffer[key][2]
                    invertColor = self.dispBuffer[key][3]
                    if not invertColor:
                        fontRGB = self.dispBuffer[key][4]
                        backgrounRGB = self.dispBuffer[key][5]
                    else:
                        fontRGB = self.dispBuffer[key][5]
                        backgrounRGB = self.dispBuffer[key][4]
                    string = self.dispBuffer[key][6]
                    # input(f">{string}<")
                    handleDisplay(string)
                    self.dispBuffer[key][7] = True	# Flag that the line went to the display
        else:
            key = indexToPrint
            if self.dispBuffer[key][0] == False or printOverLockedLines == True:
                
                self.yCounter = key
                # isNotNull = self.dispBuffer[key][1]
                isSelected = self.dispBuffer[key][2]
                invertColor = self.dispBuffer[key][3]
                if not invertColor:
                    fontRGB = self.dispBuffer[key][4]
                    backgrounRGB = self.dispBuffer[key][5]
                else:
                    fontRGB = self.dispBuffer[key][5]
                    backgrounRGB = self.dispBuffer[key][4]
                if string == None:
                    string = self.dispBuffer[key][6]
                else:
                    
                    string = slib.equalizeLine(string, self.xCharMax)
                    self.dispBuffer[key][6] = string
                handleDisplay(string)
                self.dispBuffer[key][7] = True	# Flag that the line went to the display
    
    def writtenBufferLines(self):
        # Returns a list of bools which correspond to each line of the display buffer
        # A True in dicates the line is not null, a False indicates the line is null
        # (NUll or no is in terms of whether the line has text written for the display)
        writtenList = []
        for key in self.dispBuffer:  # yCharMax is non-zero-based
            writtenList.append(self.dispBuffer[key][1])
        return writtenList
    
    def unlockedBufferLines(self, filterByUnwritten=False):
        start = 0
        end = 0
        qtyAvailable = 0
        startFound = False
        for key in self.dispBuffer:
            if self.dispBuffer[key][0] == False and startFound == False: # Look for the first unlocked key
                start = key
                startFound = True
            
            if startFound and self.dispBuffer[key][0] == True:
                break
            else:
                end = key
        # end+=1
        qtyAvailable = end - start + 1 
        
        if filterByUnwritten:
            foundUnlocked = False
            newStart = start
            for key in range(start, (end+1)):
                
                
                if self.dispBuffer[key][1] == False and foundUnlocked == False:
                    foundUnlocked = True
                    newStart = key
                    # print(f"new Start: {newStart}")
                if foundUnlocked and self.dispBuffer[key][1] == True:
                    break
                else:
                    end = key
                # print(f"key {key}, start {start}, end {end}, unlocked: {self.dispBuffer[key]}")
                
            start = newStart
            qtyAvailable = end - start + 1
            
        return start, end, qtyAvailable
    
    def getOrSetSelectedBufferLine(self, setLine=None):
        
        # Gets or sets the selection of a line in the display buffer (this is a bool of the
        # display buffer). leaving setLine=None
        # causes the function to return the currently set line. Passing-in an integer
        # to setLine causes the function to set the indicated line as selected.
        # Passing-in -1 causes the function to set all lines to unselected
        
        if setLine == None: # Function will return the line which is currently selected
            setLine = -1	# will return -1 if no line is selected
            
            for key in range(0, (self.yCharMax)): 	# self.yCharMax is not zero based...
                selectBool = self.dispBuffer[key][2]
                #setLine = self.dispBuffer[key]
                if selectBool == True:
                    setLine = key
                    break
                
        else:
            if setLine == -1: 	# Will set all selection bools to false
                for key in range(0, (self.yCharMax)): 	# self.yCharMax is not zero based...
                    self.dispBuffer[key][2] = False
            else:
                if setLine < 0 or setLine > (self.yCharMax-1):	# yCharMax is non-zero-based
                    # reject the index to value to be applied, if it falls outside
                    # the boundaries of the display buffer
                    setLine = -1	# Indicate failure to set the line by returning -1
                else:
                    self.dispBuffer[setLine][2] = True
                                    
        return setLine
        
    def getListItem(self, list_to_check, index):
        if index < 0:
            return "bol"
        elif index >= len(list_to_check):
            return "eol"
        else:
            return list_to_check[index]

    def insertIntoBuffer(self, displayList, overwrite=True):
        # list into buffer and print
        # for index, item in enumerate(displayList):
        #     print(f"{index} {item}")
        # input(":::")
        
        start, end, qtyAvailable = self.unlockedBufferLines(filterByUnwritten=(not overwrite))
        # print(f"start  {start} end {end} qtyAvailable {qtyAvailable}")
        tempListIndex = 0
        for key in range(start, (end+1)): # Range goes to the end value, minus 1; it needs to go all the way to the end in this case
            # print(f"{key} {self.dispBuffer[key]}")
            # input(f"tempListIndex {tempListIndex}, len(displayList) {len(displayList)}")
            if tempListIndex == len(displayList):
                break
            if self.dispBuffer[key][0] == False:
                self.dispBuffer[key][1] = True	# Indicate the line isn't empty
                self.dispBuffer[key][6] = displayList[tempListIndex]
                self.dispBuffer[key][7] = False # Indicate it has not yet gone to the display
            tempListIndex+=1
        
        self.printBuffer()
        
    def writeUnwrittenBufferLines(self, overWriteLocked=False):
        # iterates through the display buffer, finding any line which is flagged as
        # not yet having been written to the display (7th index location is False)
        # and writes it to the display (and updated 7th index to True)
        for key in self.dispBuffer:
            if self.dispBuffer[key][7] == False:
                self.printBuffer(indexToPrint=key, printOverLockedLines=overWriteLocked)
                self.dispBuffer[key][7] == True
                    
    def manageMsgBuffer(self, strList, abbreviateScroll):
        
        def buildOutput(tempList, strList, lineIndex, indexDelta, multiPage):
            # Check which lines are available for writing (not write-locked)
            start, end, qtyAvailable = self.unlockedBufferLines()
            
            # Build the output list
            bol = False
            eol = False
            lineIndex = -1
            for key in range(start, end):
                lineIndex+=1

                tempStr = self.getListItem(strList, (lineIndex + indexDelta)) # use the index delta to decide where to start building the list
                if tempStr == "bol":
                    bol = True	# Beginning of list
                    indexDelta+=1
                    tempList.append(slib.equalizeLine("[BOL]", self.xCharMax))
                    tempStr = self.getListItem(strList, (lineIndex + indexDelta))
                    tempList.append(tempStr)
                elif tempStr == "eol":
                    eol = True		# End of list
                    break
                else:
                    tempList.append(tempStr) # use the index delta to decide where to start building the list

            if eol and (len(tempList) == qtyAvailable):
                del tempList[-1]
                lineIndex -= 1
                tempList.append(slib.equalizeLine("[...]", self.xCharMax))
            elif eol:
               tempList.append(slib.equalizeLine("[EOL]", self.xCharMax))     
            else:
                try:
                    del tempList[-1]
                except:
                    pass
                lineIndex -= 1
                tempList.append(slib.equalizeLine("[...]", self.xCharMax))
                
            return tempList, bol, eol, lineIndex
            
        def manageHighlighting(highlightIndex, abbreviateScroll):
            start, end, qtyAvailable = self.unlockedBufferLines()
            
            foundHighlight = False
            highlighIndex = -1
            for key in range(start, end):
                isHighlighted = self.dispBuffer[key][3]
                if isHighlighted:
                    foundHighlight = True
                    highlightIndex = key
                    break
            # print(f"start {start}")
            if not foundHighlight:
                highlightIndex = start
                self.dispBuffer[highlightIndex][3] = True
                self.printBuffer(indexToPrint=highlightIndex)
                
            while True:
                previousHighlight = highlightIndex # Store the most recent highlight, so it can be cleared later
                
                # Apply the current highlight
                self.dispBuffer[highlightIndex][3] = True
                self.printBuffer(indexToPrint=highlightIndex)
                
                key = self.getInput16()	# Get input from the user
                        
                if key == self.downKey:
                    highlightIndex+=1
                    if abbreviateScroll:	# So the user doesn't have to scroll all the way down, one line at a time
                        if highlightIndex == (start + 2):
                            highlightIndex = end - 2
                elif key == self.upKey:
                    highlightIndex-=1
                    if abbreviateScroll:	# So the user doesn't have to scroll all the way up, one line at a time
                        if highlightIndex == end - 3:
                            highlightIndex = start + 1                            
                elif key == self.returnKey:
                    # indicate the user has pressed the return key 
                    return 2, highlightIndex
                elif key == self.escKey:
                    # indicate the user has chosen to exit
                    return 3, highlightIndex
                        
                # Detect
                if highlightIndex < start:
                    highlightIndex+=1
                    return -1, highlightIndex
                elif highlightIndex > (end - 1):
                    highlightIndex-=1
                    return 1, highlightIndex
                
                # Turn off the hightlight in preperation for the next line to be highlighted
                self.dispBuffer[previousHighlight][3] = False
                self.printBuffer(indexToPrint=previousHighlight)
        
            
        # ===========================================================================       
        # Check to see if the input text is going to be longer than the screen buffer
        start, end, qtyAvailable = self.unlockedBufferLines()
        if len(strList) > qtyAvailable:
            multiPage = True
        else:
            multiPage = False
        lineIndex = 0
        tempList = []
        indexDelta = 0
        highlightIndex = None
        while True:
            tempList = []
            tempList, bol, eol, lineIndex = buildOutput(tempList, strList, lineIndex, indexDelta, multiPage)
                                           
            self.insertIntoBuffer(tempList)
            # printList(tempList)
            # tempStr = input(": ")
            scrollDirection, highlightIndex = manageHighlighting(highlightIndex, abbreviateScroll)
            if scrollDirection == 1:
                indexDelta+=1
            elif scrollDirection == -1:
                indexDelta-=1
            elif scrollDirection == 2:
                return 2 # The user has pressed the return key
            elif scrollDirection == 3:
                return 3 # indicate the user has chosen to exit
            
            if bol and scrollDirection == -1:
                return -1	# Go to the previous message
                
            if eol and scrollDirection == 1:
                return 1	# Go to the next message
            
        # ===========================================================================
            
    def printMsgs(self, string, autoScroll=True, abbreviateScroll=False):
        # This function is for displaying messages which are read by the user
        # You feed it one message at a time, and it returns the user's scroll direction
        # or if the user wants to reply to a message, or if he wants to exit
        stringList = slib.convertStringToList(string, self.xCharMax)
        scrollDirection = self.manageMsgBuffer(stringList, abbreviateScroll)
        return scrollDirection
    
    def manageListBuffer(self, strList):
        
        def buildOutput(tempList, strList, lineIndex, indexDelta):
            # Check which lines are available for writing (not write-locked)
            start, end, qtyAvailable = self.unlockedBufferLines()
            
            # Ensure the built list will never exceed the end of the strList 
            while (lineIndex + indexDelta) >= len(strList):
                indexDelta-=1
            
            # Build the output list
            bol = False
            eol = False
            lineIndex = -1
            for key in range(qtyAvailable):
                lineIndex+=1

                tempStr = self.getListItem(strList, (lineIndex + indexDelta)) # use the index delta to decide where to start building the list
                # print(f"tempStr {tempStr}, lineIndex {lineIndex}, index Delta {indexDelta}, sum {(lineIndex + indexDelta)}")
                if tempStr == "bol":
                    lineIndex -= 1 # Turn the cntr back one iteration, to make sure we get this first item in the list
                    indexDelta = 0
                elif tempStr == "eol":
                    break
                else:
                    tempList.append(tempStr) # use the index delta to decide where to start building the list
                    
            return tempList, bol, eol, lineIndex, indexDelta
            
        def manageHighlighting(highlightIndex, compelteListToBeDisplayed):
            start, end, qtyAvailable = self.unlockedBufferLines()
            end+=1 # Because zero-based functions stop BEFORE the end
            
            foundHighlight = False
            highlighIndex = -1
            for key in range(start, end):
                isHighlighted = self.dispBuffer[key][3]
                if isHighlighted:
                    foundHighlight = True
                    highlightIndex = key
                    break
            # print(f"start {start}")
            if not foundHighlight:
                highlightIndex = start
                self.dispBuffer[highlightIndex][3] = True
                self.printBuffer(indexToPrint=highlightIndex)
                
            while True:
                previousHighlight = highlightIndex # Store the most recent highlight, so it can be cleared later
                
                # Apply the current highlight
                self.dispBuffer[highlightIndex][3] = True
                self.printBuffer(indexToPrint=highlightIndex)
                
                key = self.getInput16()	# Get input from the user
                        
                if key == self.downKey:
                    highlightIndex+=1
                    
                elif key == self.upKey:
                    highlightIndex-=1
                    
                elif key == self.returnKey:
                    # indicate the user has chosen the selected line
                    return 2, highlightIndex
                elif key == self.escKey:
                    # indicate the user has chosen to exit without selecting
                    return 3, highlightIndex
                elif key == "#":
                    # indicate the user has chosen another option (# sign)
                    return 4, highlightIndex
                elif key == "*":
                    # indicate the user has chosen another option (# sign)
                    return 5, highlightIndex
                                           
                                           
                # Prevent the highlight from going beyond the bounds of the list
                if highlightIndex >= (len(compelteListToBeDisplayed) + start):
                    highlightIndex-=1
                elif highlightIndex < start:
                    highlightIndex+=1
                    return -1, highlightIndex
                elif highlightIndex > (end - 1):
                    highlightIndex-=1
                    return 1, highlightIndex
                
                # Turn off the hightlight in preperation for the next line to be highlighted
                self.dispBuffer[previousHighlight][3] = False
                self.printBuffer(indexToPrint=previousHighlight)
        
            
        # ===========================================================================       
        # Check to see if the input text is going to be longer than the screen buffer
        
        lineIndex = 0
        tempList = []
        indexDelta = 0
        highlightIndex = None
        while True:
            tempList = []
            tempList, bol, eol, lineIndex, indexDelta = buildOutput(tempList, strList, lineIndex, indexDelta)
            # slib.printList(tempList)                              
            self.insertIntoBuffer(tempList)
            # printList(tempList)
            # tempStr = input(": ")
            scrollDirection, highlightIndex = manageHighlighting(highlightIndex, strList)
            if scrollDirection == 1:
                indexDelta+=1
            elif scrollDirection == -1:
                indexDelta-=1
            elif scrollDirection == 2:	# 2 was chosen as the flag to indicate the user selected an item in the list
                start, end, qtyAvailable = self.unlockedBufferLines()
                # The highlightIndex is the location on screen. This needs to be adjusted to reflect the
                # true location within the displayed list, which is impacted by the quanity of top of
                # screen border (subtracted by variable "start") and the fact that the displayed list
                # may be longer than the screen, and so the start of the screen may not correlate to
                # the start of the list (compensated for by adding the "indexDelta" variable)
                return highlightIndex + indexDelta - start
            elif scrollDirection == 3:	# User chose to exit without selection, corresponds to C key
                return -1
            elif scrollDirection == 4:	# Corresponds to # key
                return -4
            elif scrollDirection == 5:	# Corresponds to * Key
                return -5
       
    def printList(self, stringOrList, autoScroll=True, abbreviateScroll=False):
        # This function is for displaying a selectable list for the user to choose from
        # You can input a string OR a list
        # Keypad A: Scroll Up
        # Keypad B: Scroll Down
        # Keypad C: Returns -1 
        # Keypad D: Returns index of selected list item
        # Keypad #: Returns -4
        # Keypad *: Returns -5
        stringList = slib.convertStringToList(stringOrList, self.xCharMax)
        indexOfSelection = self.manageListBuffer(stringList)
        return indexOfSelection
                    
    def print(self, string, end="\n", pause=False, autoScrollInterval=0.1, autoCLS=False):
        if autoCLS == False:   # Keep existing lines already written to the display
            # Find lines in the display which have been written already
            start, end, bufferLinesAvailable = self.unlockedBufferLines()
            dispLinesAlreadyWrittenList = []
            for key in range(start, (end+1)):
                if self.dispBuffer[key][1] == True:
                    dispLinesAlreadyWrittenList.append(self.dispBuffer[key][6])
                    self.dispBuffer[key][1] = False # We want to include this line to be written over, because it is being
                                                    # incorporated into the new data to be written. Otherwise we would have
                                                    # to CLS the whole display, which is noticably less efficient
                            
            # Merge lines already written with lines to be written
            stringList = slib.convertStringToList(string, self.xCharMax)
            stringList = dispLinesAlreadyWrittenList + stringList
            
            start, end, bufferLinesAvailable = self.unlockedBufferLines(filterByUnwritten=True)
        
        else:   # Already written lines will be discarded
            stringList = slib.convertStringToList(string, self.xCharMax)
            start, end, bufferLinesAvailable = self.unlockedBufferLines(filterByUnwritten=False)
                
        # print(f"buffAva: {bufferLinesAvailable}")
        # print(f"start {start} end {end}")
               
        if bufferLinesAvailable == 0:
            bufferLinesAvailable = 1
        indexDelta = -1
        stringFullyWritten = False
        while stringFullyWritten == False:
            eol = False
            tempDispBuffer = []
            indexDelta+=1
            lineIndex = -1
            index=0
            
            for integer in range(bufferLinesAvailable):
                lineIndex+=1
                tempStr = self.getListItem(stringList, (lineIndex + indexDelta)) # Get the elements of the list to be printed
                if tempStr == "eol":
                    # print(1)
                    stringFullyWritten = True
                    # self.insertIntoBuffer(tempDispBuffer, overwrite=autoCLS)
                    break
                else:
                   tempDispBuffer.append(tempStr)
            
            if (lineIndex + indexDelta) < len(stringList) - 1:                
                del tempDispBuffer[-1]
                tempDispBuffer.append(slib.equalizeLine("[...]", self.xCharMax))
            # slib.printList(tempDispBuffer)
            self.insertIntoBuffer(tempDispBuffer, overwrite=autoCLS)
            
            # print(f"lineIndex: {(lineIndex + indexDelta)}, len List: {len(stringList)}")
            if (lineIndex + indexDelta) == (len(stringList)):
                break
            else:
                if pause:
                    if self.keyCtrl == None:
                        input(":")
                    else:
                        tempChar = ""
                        while tempChar != self.returnKey:
                            tempChar = self.keyCtrl.keyIn()
                        
                else:
                    utime.sleep(autoScrollInterval)
                
    
    def textEditor(self, cursorOn=True, numericalEntry=False):
    
        def handleNewChar(newChar, currentLineStr, xPos, cursorOn):
            # print(f"newChar >{newChar}<")
            printLastLine = False
            printNextLine = False
            
            if "\n" in newChar:
                                            
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
                        # print(f"currentLineStr >{currentLineStr}<, yCounter: {self.yCounter}")
                        
                        self.getFromWriteToDispBuffer(self.yCounter, string=currentLineStr) # Insert current line into display buffer
                        currentLineStr = ""
                        self.yCounter+=1
                        xPos = 0
                        currentLineStr+=newChar
                
                else:   # Situation where the character can be added to the currentLine without issue
                    currentLineStr+=newChar
                    xPos = len(currentLineStr) - 1
            
            # print(f"currentLineStr {currentLineStr}")
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
        self.printLineLowLevel(self.blankLine, self.cursorY) # Clear the first line
        self.cursorY = start
        self.cursorX = 0
        xPos = 0
        self.initCursor()
        
        while edit:
            if cursorOn:
                self.enableCursor(True)
            
            # print(f"x, y - {self.cursorX}, {self.cursorY}")
            char = self.getInputAZ(numericalEntry)	# Get the keyboard/Keypad input
            
            if cursorOn:
                self.enableCursor(False)
                
            if char == "\n\r":
                edit = False
                break
            
            currentLineStr, xPos = handleNewChar(char, currentLineStr, xPos, cursorOn)
            
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
            if line[-1] == " ":
                line = line.strip() + " "
            else:
                line = line.strip()
            outputStr+= f"{line}"
        self.enableCursor(False)
        return outputStr
    
    def yesNoOther(self, message="", yes="Yes", no="No", other=None):
        tempStr = f"{message}\n\n" + f"Yes   [{self.returnKey}]\n"+ f"No    [{self.escKey}]\n"
        
        if other!= None:
            tempStr += f"{other} [{self.upKey}]"
            
        self.setBorder(string=tempStr, function="bottom", hBar=True)
        
        response = ""
        if other == None:
            while response != self.returnKey and response != self.escKey:
                response = self.getInput16()
        else:
            while response != self.returnKey and response != self.escKey and response != self.upKey:
                response = self.getInput16()
                # print(f"response: {response}")
                
        return response
    
    def getNumericalEntry(self, minimum=0, maximum=9, allowCancel=True):
        # Returns numerical result 0 to 9; return -1 indicates cancel / back
        outsideRange = False
        tempInt = 0
        while True:
            tempStr = f"Choose Item [{minimum} to {maximum}]"
            if allowCancel:
                tempStr+="\n[#]: Back"
            if outsideRange:
                tempStr = f"Invalid selection! [{tempInt}]\n" + tempStr
            self.setBorder(string=tempStr, function="bottom", hBar=True)
            tempInt = self.getInput16()
            
            if allowCancel:
                if tempInt == "#":
                    return -1
            
            try:
                # print(f"User input: {tempInt}, {minimum} to {maximum}")
                tempInt = int(tempInt)
                if tempInt >= minimum and tempInt <= maximum:
                    break
                else:
                    outsideRange = True
            except:
                outsideRange = True
                
        return tempInt
    
    def phoneNumberEntry(self, kpad, banner="ENTER NUMBER",
              allowedChar = ["1","2","3","4","5","6","7","8","9","0"],
              enterChar="D", bSpace="#"):
        def insertIntoFormat(numbers):
            fList = ["", "", "", "", "", "", "", "", "", "", "", ""]
            
            while len(numbers) > len(fList):
                numbers = numbers[:-1]
            
            for index, char in enumerate(numbers):
                fList[index] = char
            
            fList.insert(2, " (")
            fList.insert(6, ") ")
            fList.insert(10, " ")
            
            for index, item in enumerate(fList):
                if item == "":
                    fList[index] = "-"
            # print(fList)
            
            outStr = ""
            for item in fList:
                outStr+=item
            return outStr
        
        # Display the menu
        self.cls(clsA=True)
        self.setBorder(string=banner, function="top")
        self.setBorder(string="[D]: Enter, [#]: Backspace", function="bottom")
        
        number = "-- (---) --- ----"
        tempStr = "+1"
        formattedNumber = insertIntoFormat(tempStr)
        start, end, bufferLinesAvailable = self.unlockedBufferLines(filterByUnwritten=True)
        self.printLineLowLevel(formattedNumber, start, ignoreWriteLock=False)
        
        while True:
            char = kpad.keyIn()
            
            if char == enterChar:
                if len(tempStr) == 12:
                    break
            elif char == bSpace:
                # lcd.print("\\d")
                tempStr = tempStr[:-1]
            elif char in allowedChar:
                tempStr+=char
                # lcd.print(tempStr)
            
            while len(tempStr) > 12:
                tempStr = tempStr[:-1]
            
            if tempStr == "":
                tempStr = "+"
            print(len(tempStr))

            formattedNumber = insertIntoFormat(tempStr)
            self.printLineLowLevel(formattedNumber, start, ignoreWriteLock=False)
        return tempStr
    
    # =================================================================
    #                          Cursor Stuff
    # =================================================================
    def initCursor(self, deInit=False):
        
        timer1 = Timer(-1)
        # print("Trying to start the cursor timer")
        # For whatever reason the cursor timer doesn't like to start on the first try.
        # The loop below combines with self.blinkCursor() to confirm that the timer callback
        # is working. If it is not then the timer is de-initialized and re-started.
        while True and self.cursorRunning == False:
            timer1.init(freq=cfg.cursor_interval, mode=Timer.PERIODIC, callback=self.blinkCursor)
            utime.sleep((1 / cfg.cursor_interval) + 0.1)
            if self.cursorRunning:
                break
            else:
                timer1.deinit()
        # print("Success starting cursor timer")
                             
    
    def enableCursor(self, enable=True):
        self.cursorEnable = enable
    
    # def blinkCursor(self, timer1):
    def blinkCursor(self, t):
        if not self.cursorRunning:
            self.cursorRunning = True
        #print(f"self.cursorEnable: {self.cursorEnable}")
        if self.cursorEnable:
            self.cursorFill(self.cursorToggle)
            self.cursorToggle = not self.cursorToggle
            
    def cursorFill(self, background):
        if background==True:
            r=self.backGroundR
            g=self.backGroundG
            b=self.backGroundB
        else:
            r=self.fontColorR
            g=self.fontColorG
            b=self.fontColorB
            
        if (self.cursorX*self.fontBitWidth) >= self.dispObj.width:
                # Make sure it doesn't blink beyond the confines of the screen
            x_loc = 0
            y_loc = (self.cursorY*self.fontBitHeight) + self.fontBitHeight
            self.cursorX = x_loc
            self.cursorY = int(y_loc / self.fontBitHeight)
        else:
            x_loc = self.cursorX*self.fontBitWidth
            y_loc = self.cursorY*self.fontBitHeight
        
        if x_loc < cfg.display_sizeX and y_loc < cfg.display_sizeY: # Don't print out of bounds
        
            if self.cursorType == 0:
                self.dispObj.fill_hrect(x_loc, y_loc, self.fontBitWidth, (self.fontBitHeight),
                                                   color565(r, g, b))
            else:
                y_loc += (self.fontBitHeight)
                y_loc -= 1
                self.dispObj.fill_hrect(x_loc, y_loc, self.fontBitWidth, 1,
                                                   color565(r, g, b))
                
        
        
        
        
        
            
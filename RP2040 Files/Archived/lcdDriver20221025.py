from ili9341 import Display
from machine import Pin, SPI, Timer
import utime
import config as cfg
import ili9341
from ili9341 import color565
from xglcd_font import XglcdFont
import standardLibrary as slib

# LCD Driver Version 1.01

"""
This dictionary allows for the loading of all available fonts
The first item is the filename of the font file, the second
is the font width, the third is the font height, and the fourth
is a place-holder for the initialized font object (once it is 
initialized, during the createMyDisplay() function)
"""
fontPack = {
    
    #"arcade": ["ArcadePix9x11.c", 9, 11, None],
    #"bally": ["Bally5x8.c", 5, 8, None],
    #"bally2": ["Bally7x9.c", 7, 9, None],
    #"broadway": ["Broadway17x15.c", 17, 15, None],
    #"espresso": ["EspressoDolce18x24.c", 18, 24, None],
    # "fixed": ["FixedFont5x8.c", 5, 8],
    # "ibm": ["IBMPlexMono12x24.c", 12, 24, None],
    # "neato": ["Neato5x7.c", 5, 7, None],
    # "neato2": ["NeatoReduced5x7.c", 5, 7, None],
    #"robotron": ["Robotron13x21.c", 13, 21, None],
    #"robotron2": ["Robotron7x11.c", 7, 11, None],
    # "ubuntu": ["UbuntuMono12x24.c", 12, 24, None],
    # "unispace": ["Unispace12x24.c", 12, 24, None],
    # "unispace2": ["UnispaceExt12x24.c", 12, 24, None],
    # "wendy": ["Wendy7x8.c", 7, 8, None]
    }

fontColors = {
    # https://superuser.com/questions/361297/what-colour-is-the-dark-green-on-old-fashioned-green-screen-computer-displays
    "white": (255,255,255),
    "red": (255,0,0),
    "green": (0,255,0),
    "blue": (0,0,255),
    "yellow": (255,255,0),
    "purple": (230,230,250),
    "thistle": (216,191,216),
    "plum": (221,160,221),
    "orange": (255,165,0),
    "black": (0,0,0),
    "amber": (255, 176, 0),
    "light amber": (255,204,0),
    "green 1": (51,255,0),
    "apple II": (51,255,51),
    "green 2": (0,255,51),
    "apple IIc": (102,255,102),
    "green 3": (0,255,102),
    "background0": (0,0,0),
    "background1": (255,255,255),
    "background2": (40,40,40)
    }

TFT_CLK_PIN = const(6)
TFT_MOSI_PIN = const(7)
TFT_MISO_PIN = const(4)

TFT_CS_PIN = const(13)
TFT_RST_PIN = const(14)
TFT_DC_PIN = const(15)
# tim = Timer(1, mode=Timer.PERIODIC, width=32)

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

def equalizeLine(string, xCharMax):
    string = string.strip()
    while len(string) != xCharMax:
        string+=" "
    return string

def convertStringToList(textString, xCharMax):
    
    def appendStr(string):
        buffer.append(string)
        
    
    if len(textString) == 0:
        textString = " "
    xCharMax+=1
    buffer = []
    
    if slib.returnVarType(textString) != "str":
        textString = str(textString)
    
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

class display:
    
    
    def __init__(self):
        
        self.xCounter = 0
        self.yCounter = 0
        self.xCharMax = 0
        self.yCharMax = 0
        self.yStartPos = 0
        self.borderTop = 0 # This is in character height units
        self.borderBottom = 0 # This is in character height units
        self.cursorPosCharUnits = [0, 0]
        self.firstLineWritten = False     
        self.cursorType = 0
        self.bufferSizeOffset = -1
        self.dispBufferList = []
        self.maxBufferLength = 0
        
        self.fontColorR = fontColors[cfg.font_color][0]
        self.fontColorG = fontColors[cfg.font_color][1]
        self.fontColorB = fontColors[cfg.font_color][2]
        self.backGroundR = fontColors[cfg.background][0]
        self.backGroundG = fontColors[cfg.background][1]
        self.backGroundB = fontColors[cfg.background][2]
        self.fontBitWidth = 0
        self.fontBitHeight = 0
        self.selectedFont = None
        self.initializedFontDict = {"fontName":["microPython"],"object":[None], "bitWidth":[8], "bitHeight":[8]}
        
        # Run the following initializing functions
        # baudrate=51200000
        spi = SPI(0, baudrate=40000000, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
        self.dispObj = Display(spi, dc=Pin(TFT_DC_PIN), cs=Pin(TFT_CS_PIN), rst=Pin(TFT_RST_PIN),
                                  width=cfg.display_sizeX, height=cfg.display_sizeY)
        self.dispObj.clear(color=color565(self.backGroundR, self.backGroundG, self.backGroundB))
        self.initializeFonts()
        self.setFontByInt(fontInt=0)
        
        # Setup the cursor timer
        timer1 = Timer()
        timer1.init(freq=cfg.cursor_interval, mode=Timer.PERIODIC, callback=self.blinkCursor)
        self.cursorEnable = False
        self.cursorToggle = False
        utime.sleep(1)  
    
    def disp(self, string="", action="append", line=None, autoPrint=True, end="\n"):
        def trim(side="start"):
            while len(self.dispBufferList) > self.maxBufferLength:
                if side == "start":
                    del self.dispBufferList[0]
                elif side == "end":
                    del self.dispBufferList[-1]
                    
        def convert(string):
            if slib.returnVarType(string) != "list":
                string = str(string)
                output = convertStringToList(string, self.xCharMax)
            else:
                output = string
            return output
            
        
        # Creates a clean buffer according to the size limit dictated by the top and bottom borders
        if action == "init" or action == "*":
            self.dispBufferList = []
            for i in range((self.yCharMax+self.bufferSizeOffset)):
                # print(i)
                tempStr = equalizeLine(f"", self.xCharMax)
                tempStr = (0, tempStr)
                self.dispBufferList.append(tempStr)
                self.maxBufferLength = len(self.dispBufferList)
        
        elif action == "getMaxLines":
            return self.yCharMax+self.bufferSizeOffset
        
        # Inserts a string into the buffer
        elif (action == "append" or action == "+") and line==None:
            
            if len(self.dispBufferList) == 0:
                self.disp(action="init")   
            
            tempList = convert(string)
            qtyLinesRequired = len(tempList)
            # input(tempList)
            for i in range(qtyLinesRequired):
                appended = False
                
                # Manage end= commands
                if end == "\n":
                    written = 1
                else:
                    written = 0
                
                toBuffer = (written, tempList[i])
                for index, item in enumerate(self.dispBufferList):
                    isEmpty = item[0]
                    if isEmpty == 0:
                        self.dispBufferList[index] = toBuffer
                        appended = True
                        break
                if appended == False:
                    self.dispBufferList.append(toBuffer)
            
            # Trim the beginning of the buffer to make it fit
            trim()
        
        elif (line != None) and (string != ""):
            # These vars needed for cases where line < 0 and line < maxBufferLength (
            if line < self.maxBufferLength:
                tempList = convert(string)
                qtyLinesRequired = len(tempList)
                
            if line < 0:
                
                temp = []
                for i in tempList:
                    temp.append((1, i))
                    if end == "":
                        del self.dispBufferList[0]
                self.dispBufferList = temp + self.dispBufferList
                trim(side="end")
            elif line < self.maxBufferLength:
                for index, string in enumerate(tempList):
                    index+=line
                    self.dispBufferList.insert(index, (1, string))
                    if end == "":
                        del self.dispBufferList[index+1]
                trim(side="end")
            else:
                self.disp(string)
            
        elif action == "print" or action == ">>":
            self.printBuffer(self.dispBufferList)
        
        if autoPrint:
            self.printBuffer(self.dispBufferList)
                
    def printBuffer(self, stringList):
        for index, item in enumerate(stringList):
            string = item[1]
            self.yCounter = self.borderTop + index
            self.dispWriteLowestLevel(string)
            #self.incrementY()       
            
        
    
    def initializeFonts(self):
        # Initialize an object for each font
        print('Loading fonts...')
        initializedFontDict = {"fontName":[],"object":[]}
        for item in fontPack:
            filePath = f"./fonts/{fontPack[item][0]}"
            self.fontBitWidth = fontPack[item][1]
            self.fontBitHeight = fontPack[item][2]
            print(f"Attempting to initialize {item} font")
            try:
                fontObject = XglcdFont(filePath, self.fontBitWidth, self.fontBitHeight) 
                # fontPack[item][3] = fontObject
                self.initializedFontDict["fontName"].append(item)
                self.initializedFontDict["object"].append(fontObject)
                self.initializedFontDict["bitWidth"].append(self.fontBitWidth)
                self.initializedFontDict["bitHeight"].append(self.fontBitHeight)
                print("'-> Success!")
                
            except Exception as err:
                print(f"\'-> Failed... error: {err}")
        
    def setFontByInt(self, fontInt=0):
        self.selectedFont = self.initializedFontDict["object"][fontInt]
        self.fontBitWidth = self.initializedFontDict["bitWidth"][fontInt]
        self.fontBitHeight = self.initializedFontDict["bitHeight"][fontInt]
        self.xCharMax = int((self.dispObj.width / self.fontBitWidth) - 1)	# Need one character's worth padding, because
        self.yCharMax = self.calc_maxLines() - self.borderBottom
        self.maxBufferLength = self.xCharMax * self.yCharMax
        self.cls()
    
    
    def dispWriteLowestLevel(self, string):
        
        if self.selectedFont == None:
            # Uses the built-in Micropython 8x8 font
            self.dispObj.draw_text8x8((self.xCounter * self.fontBitWidth), (self.yCounter * self.fontBitHeight), string,
                  color565(self.fontColorR, self.fontColorG, self.fontColorB))
        else:
            self.dispObj.draw_text((self.xCounter * self.fontBitWidth), (self.yCounter * self.fontBitHeight), string,
                                      self.selectedFont,
                  color565(self.fontColorR, self.fontColorG, self.fontColorB))
            
    def handleCtrlChar(self, string):
        if string == "\\n":			# Create new line
            
            self.dispBufferList.append(string)
            self.incrementY()
        elif string == "\\r":		# Return home
            # del self.dispBufferList[-self.xCounter]
            # self.dispBufferList = self.dispBufferList[:-self.xCounter]
            self.xCounter = 0
        elif string == "\\c":		# Return home and clear the line
            # self.dispBufferList = self.dispBufferList[:-self.xCounter]
            self.clsLine()
            self.xCounter = 0
        elif string == "\\a":		# Clear all
            self.cls(clearBuff=False)
        elif string == "\\f":		# Clear all and flush the buffer
            # self.dispBufferList = []
            self.cls()
        elif string == "\\b":		# reload the buffer
            if len(self.dispBufferList) > 0:
                tempStr = ""
                # print(self.dispBufferList)
                for item in self.dispBufferList:
                    tempStr+=item
                # print(tempStr)
                # input(":")
                self.cls()
                self.print(tempStr)
        elif string == "\\d":
            self.decrementX()                
            self.dispWriteLowestLevel(" ")
            
    def xRemainder(self):
        tempInt = self.xCharMax - self.xCounter
        return int(tempInt)

    def yRemainder(self):
        return self.yCharMax - self.yCounter + 1
    
    def incrementY(self):
        self.xCounter = 0
        if self.yRemainder() > 0:
            self.yCounter += 1
        else:
            
            # self.yCounter = self.yCharMax - 1
            self.clsLine()    
    
    def decrementY(self):
        input(": This function is under construction!")
        # for item in 
        if self.yRemainder() > self.borderTop:
            self.xCounter = 0
            self.yCounter += 1
        else:
            del self.dispBufferList[:self.xCharMax]
            self.xCounter = 0
    
    def resetY(self):
        self.yCounter = self.borderTop

    def incrementX(self):
        if self.xRemainder() >= 0:
            self.xCounter += 1
        else:
            self.incrementY()
            
    def decrementX(self):
        self.xCounter-=1
                            
        if self.xCounter < 0:
            
            if self.yCounter > self.borderTop:
                self.xCounter = self.xCharMax 
                self.yCounter -= 1
            else:
                self.xCounter = 0
            
    
    def bufferOut(self, character):
                
        # print(f"xRemainder: {xRemainder()}")
        if character != "":
            if self.xRemainder() > -1 and self.yRemainder() > 0:
                
                self.dispWriteLowestLevel(character)
                self.incrementX()
            else:
                self.incrementY()
                self.dispWriteLowestLevel(character)
                self.incrementX()
            
        # print(f"Char: {character}, xCounter: {self.xCounter}")
        
    def print(self, textString, end="\\n", pause=None, autoLF=True):
                            
        tempBool = self.cursorEnable
        if tempBool:		# Disable the cursor, so it doesn't "Artifact" 
            self.cursor(0)
        
        textString += end # Add the default terminating character
        
        ctrlChars = ["\\n","\\r","\\c","\\a","\\f","\\b", "\\d"]
        if slib.returnVarType(textString) != "str":
            textString = str(textString)
        stringLen = len(textString)
        index = 0
        while True:
            if index >= len(textString):
                break
            
            if pause != None:
                utime.sleep(pause)
                
            ctrlCharString = ""
            currentChar = textString[index]
            
            try:
                ctrlCharString = f"{currentChar}{textString[index+1]}"
            except:
                pass
            
            if ctrlCharString in ctrlChars:
                # print(f"Found control character: {ctrlCharString}")
                self.handleCtrlChar(ctrlCharString)
                index+=1
            else:
                if autoLF and currentChar == " ":
                # will automatically linefeed if the remaining characters
                    tempInt = qtyCharsNextSpace(index, textString)
                    # input(f"{tempInt} {self.xRemainder} {self.xCharMax}")
                    if (tempInt > self.xRemainder()) and (tempInt <= self.xCharMax):
                        self.incrementY()
                        currentChar = ""
                
                self.bufferOut(currentChar)

            index+=1
            
        
        if tempBool:		# If cursor was on previously, turn it back on
            self.cursor(1)
    
    def printLBL(self, string, startLine=0):
        self.yCounter = startLine
        strList = convertStringToList(string, self.xCharMax)
        for item in strList:
            self.dispWriteLowestLevel(item)
            self.incrementY()
    
    def reader(self, string, kPadDriver=None):
        
        def toLCD(currentLine, end="\n"):
            # utime.sleep(0.01)
            self.dispWriteLowestLevel(currentLine)
            if end == "\n":
                self.incrementY()
        
        stringList = convertStringToList(string, self.xCharMax)
               
        index = 0
        buffer = []
        bufferStartIndex = 0
        
        startIndex = 0
        endIndex = startIndex + self.yCharMax - 1
        self.clt() # Clear anything that might already be on the screen
        
        indexDelta = 0
        endCntr = 0
        while True:
            self.resetY()
            self.xCounter = 0
            startIndex+=indexDelta
            endIndex+=indexDelta
            endFlag = 0
            
            for index in range(startIndex, (endIndex-1)): # Need -1 to account for elipses at the end, etc.
                if index<-1 or (index > len(stringList)):
                    return endFlag
                
                if index < 0:
                    self.clearLine(end="")
                    toLCD("(PREVIOUS MSG...)")
                    endText = ""
                    
                else: # index < (len(stringList)):
                    if index == len(stringList):
                        return endFlag
                    
                    if startIndex >=0 and endIndex <= len(stringList):
                        endText = "..."
                         
                    toLCD(stringList[index])
                    
                    if index >= len(stringList) - 1:
                        self.clearLine(end="") # Fills out blanks
                        endText = "(NEXT MSG...)"
                        endCntr+=1
                        endFlag = 1
                    else:
                         endCntr=0
                         
            self.clearLine(end="")
            toLCD(endText, end="")
            self.xCounter = len(endText)
            cmd = kPadDriver.keyIn(cursorOn=1)
            cmd = cmd.lower()
            
            if cmd == "a":
                indexDelta = -1
            if cmd == "b":
                indexDelta = 1
                if endCntr == 1 and endFlag == 1:
                    return endFlag
                
        return endFlag
                
    
    def calc_maxLines(self):
        # print("in calc_maxLines")
        temp = int(self.dispObj.height / self.fontBitHeight)
        # print(f"temp {temp}")
        return temp
    
    def setYCharMax(self):               
        self.yCharMax = self.calc_yCharMax()
    
    def calc_yCharMax(self):
        return int(self.dispObj.height / self.fontBitHeight) - self.borderBottom - self.borderTop + 1
    
    def setBorder(self, string=None, function="top", hBar=True, qtyLinesPadding=None):
        # self=lcd
        
        
        # Determine the number of lines needed to incorporate the given string
        if string!= None:
            qtyLinesNeeded = calc_lines_needed_to_print(string, self.xCharMax)
            # print(f"qtyLines Needed based on input string: {qtyLinesNeeded}")
            if qtyLinesPadding != None:
                if qtyLinesPadding > qtyLinesNeeded:
                    qtyLinesNeeded = qtyLinesPadding
        # ===================================================================
        
        # self.xCounter = 0 # Print characters at the str
        if function == "clsTop":
            tempY = self.yCounter
            tempX = self.xCounter
            self.yCounter = 0
            for index in range(0, self.borderTop):
                self.clearLine()
            self.borderTop = 0
            self.yCounter = tempY
            self.xCounter = tempX
        elif function == "clsBottom":
            tempY = self.yCounter
            tempX = self.xCounter
            self.yCounter = self.calc_maxLines() - self.borderBottom
            temp = self.yCounter
            for index in range(temp, self.calc_maxLines()):
                # print(f"yCounter: {self.yCounter}")
                self.clearLine()
            self.borderBottom = 0
            self.yCounter = tempY
            self.xCounter = tempX
        elif function == "top":
            self.yCounter = 0
            self.borderTop = 0
            self.printLBL(string)
            if hBar:
                self.horizontal_bar()
            if self.xCounter > 0:
                self.incrementY()
            self.borderTop = self.yCounter
            # print(f"yCharMax {self.yCharMax}, yCharMax: {self.calc_yCharMax()}")
        elif function == "bottom":
            self.borderBottom = 0            
            # print(f"qtyLinesN = {qtyLinesNeeded}")
            
            self.yCounter = (self.calc_maxLines()) - qtyLinesNeeded
            if hBar:
                self.yCounter-=1
                qtyLinesNeeded+=1
                self.horizontal_bar()
                
            # print("about to print")
            self.printLBL(string, self.yCounter)
            # print(f"self.yCounter = {self.yCounter}")        
            
            self.borderBottom = qtyLinesNeeded
            
            # print(f"yCharMax {self.yCharMax}, yCharMax: {self.calc_yCharMax()}, qtyLineNeeded {qtyLinesNeeded}")
        self.resetY()
        self.setYCharMax()      
    
        
    def selectFont(self):
        temp_int = len(self.initializedFontDict["fontName"]) - 1
        print("Loaded Fonts:")
        print(self.initializedFontDict["fontName"])
        selected = input(f"Choose a font number from 0 to {temp_int}: ")
        selected = int(selected)
        self.setFontByInt(selected)
        print(f"Change font to: {self.initializedFontDict["fontName"][selected]}")
    
    def clearLine(self, end="\n"):
        self.dispWriteLowestLevel(" " * (self.xCharMax+1))
        if end == "\n":
            self.yCounter+=1

    def clsLine(self, fontWidth=None):
        if fontWidth == None:
            fontWidth = self.fontBitWidth
        
        textString = " " * self.xCharMax
        self.dispObj.draw_text8x8(0, self.yCounter, textString,
              color565(self.backGroundR, self.backGroundG, self.backGroundB))
        
    def clt(self):
        self.yCounter = self.borderTop
        startIndex = 0
        endIndex = startIndex + self.yCharMax - 1
        for index in range(startIndex, (endIndex)):
            self.clearLine()
             
    
    def cls(self, fontWidth=8, fontHeight=8, clearBuff=True):
        # This function operates using the built-in MicroPython font
        # It does not need to be setup to use any of the custom font variables
        if clearBuff:
            self.dispBufferList = []
        
        self.dispObj.clear(color=color565(self.backGroundR, self.backGroundG, self.backGroundB))
        
        self.yCounter = self.borderTop
        self.xCounter = 0
        self.borderBottom = 0
        self.borderTop = 0
        self.setYCharMax()
        
    def cls_from_bottom(self, to_line):
        
        remaining_character_lines = self.yCharMax - to_line
        
        self.dispObj.fill_hrect(0, (to_line*self.fontBitHeight), self.dispObj.width, (self.fontBitHeight * remaining_character_lines),
                               color565(self.backGroundR, self.backGroundG, self.backGroundB))
        self.yCounter = to_line
        self.xCounter = 0
        
    def horizontal_bar(self, text=None, alignment=0):
        if self.xCounter > 0:
            self.incrementY()
            
        startY = (self.yCounter*self.fontBitHeight) + 2
        height = self.fontBitHeight - 4
        self.dispObj.fill_hrect(0, startY, self.dispObj.width, height,
                               color565(self.fontColorR, self.fontColorG, self.fontColorB))
        if text is not None:
            
            if alignment == 1:	# Center Justified
                text = f" {text} "
                textLen = len(text)
                pad = (self.xCharMax - textLen) % 3
                while pad > 0:
                    text+=" "
                    textLen = len(text)
                    pad = (self.xCharMax - textLen) % 3
                pad = int((self.xCharMax - textLen) / 3)
                
            elif alignment == 0: # Left justified
                text = f"{text} "
                pad = 0
                
            temp_int = self.xCounter
            self.xCounter = pad
            self.dispWriteLowestLevel(text)
            self.xCounter = temp_int
        
        self.incrementY()
        
    def setFontColor(self, color="white"):
               
        self.fontColorR = fontColors[color][0]
        self.fontColorG = fontColors[color][1]
        self.fontColorB = fontColors[color][2]
        
    def cursorFill(self, background):
        use_primary = True
        if background==True:
            r=self.backGroundR
            g=self.backGroundG
            b=self.backGroundB
        else:
            r=self.fontColorR
            g=self.fontColorG
            b=self.fontColorB
            
        if (self.xCounter*self.fontBitWidth) >= self.dispObj.width:
                # Make sure it doesn't blink beyond the confines of the screen
            x_loc = 0
            y_loc = (self.yCounter*self.fontBitHeight) + self.fontBitHeight
        else:
            x_loc = self.xCounter*self.fontBitWidth
            y_loc = self.yCounter*self.fontBitHeight
        
        # print(f"{y_loc} {self.dispObj.height} :")    
        # Prevent y_loc from falling off screen
        while y_loc > (self.dispObj.height - 1):
            x_loc = self.xCharMax * self.fontBitWidth - 1 
            y_loc = self.dispObj.height - self.fontBitHeight
            use_primary = False
            
        if self.cursorType == 0 and use_primary:
            self.dispObj.fill_hrect(x_loc, y_loc, self.fontBitWidth, self.fontBitHeight,
                                               color565(r, g, b))
        else:
            if use_primary:
                y_loc += (self.fontBitHeight)
            self.dispObj.fill_hrect(x_loc, y_loc, self.fontBitWidth, 1,
                                               color565(r, g, b))
            
            
    def cursor(self, int):
        if int == 1:
            self.cursorEnable = True
        else:
            # When the cursor is turned off, we need to make sure the block it presently resides at is set back to
            # the background color, otherwise the cursor block will just sit there until text overlays it
            self.cursorFill(True)
            self.cursorEnable = False
           
        
    def blinkCursor(self, timer):
        if self.cursorEnable:
            self.cursorFill(self.cursorToggle)
            self.cursorToggle = not self.cursorToggle
            
        
"""
    def incrementYcounter(self, incrementQty=None):
        if incrementQty == None:
            incrementQty=self.fontBitHeight
        if not ((self.yCounter + incrementQty) > (self.dispObj.height)):
            self.yCounter+=incrementQty
        else:
            self.yCounter = self.borderTop
            self.cls()
"""
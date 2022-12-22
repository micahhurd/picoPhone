from ili9341 import Display
from machine import Pin, SPI, Timer
import utime
import config as cfg
import ili9341
from ili9341 import color565
from xglcd_font import XglcdFont
import standardLibrary as slib


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
        self.dispBufferList = []
        self.maxBufferLength = 0
        self.firstLineWritten = False     
        self.cursorType = 0
        
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
        spi = SPI(0, baudrate=51200000, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
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
        self.yCharMax = int(self.dispObj.height / self.fontBitHeight)
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
            self.dispBufferList = self.dispBufferList[:-self.xCounter]
            self.xCounter = 0
        elif string == "\\c":		# Return home and clear the line
            self.dispBufferList = self.dispBufferList[:-self.xCounter]
            self.clsLine()
            self.xCounter = 0
        elif string == "\\a":		# Clear all
            self.cls(clearBuff=False)
        elif string == "\\f":		# Clear all and flush the buffer
            self.dispBufferList = []
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
            if len(self.dispBufferList) > 0:
                    del self.dispBufferList[-1]                
            self.dispWriteLowestLevel(" ")
            
    def xRemainder(self):
        tempInt = self.xCharMax - self.xCounter
        return int(tempInt)

    def yRemainder(self):
        return self.yCharMax - self.yCounter
    
    def incrementY(self):
        if self.yRemainder() > 0:
            self.xCounter = 0
            self.yCounter += 1
        else:
            del self.dispBufferList[:self.xCharMax]
            self.xCounter = 0
    
    def decrementY(self):
        input(": This function is under construction!")
        # for item in 
        if self.yRemainder() > 0:
            self.xCounter = 0
            self.yCounter += 1
        else:
            del self.dispBufferList[:self.xCharMax]
            self.xCounter = 0

    def incrementX(self):
        if self.xRemainder() >= 0:
            self.xCounter += 1
        else:
            self.incrementY()
            
    def decrementX(self):
        self.xCounter-=1
                            
        if self.xCounter < 0:
            
            if self.yCounter > 0:
                self.xCounter = self.xCharMax 
                self.yCounter -= 1
            else:
                self.xCounter = 0
            
    
    def bufferOut(self, character):
                
        # print(f"xRemainder: {xRemainder()}")
        if character != "":
            if self.xRemainder() >= 0:
                self.dispBufferList.append(character)
                self.dispWriteLowestLevel(character)
                self.incrementX()
            else:
                self.incrementX()
                self.dispBufferList.append(character)
                self.dispWriteLowestLevel(character)
                self.incrementX()
            
        # print(f"Char: {character}, xCounter: {self.xCounter}")
        
    

    def print(self, textString, end="\\n", pause=None, autoLF=True):
        
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
                    
        tempBool = self.cursorEnable
        if tempBool:		# Disable the cursor, so it doesn't "Artifact" 
            self.cursor(0)
        
        textString += end # Add the default terminating character
        
        ctrlChars = ["\\n","\\r","\\c","\\a","\\f","\\b", "\\d"]
        if slib.returnVarType(textString) != "str":
            textString = str(textString)
        stringLen = len(textString)
        done = False
        index = 0
        while not done:
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
            if index >= stringLen:
                break
        
        if tempBool:		# If cursor was on previously, turn it back on
            self.cursor(1)
        

        
    def selectFont(self):
        temp_int = len(self.initializedFontDict["fontName"]) - 1
        print("Loaded Fonts:")
        print(self.initializedFontDict["fontName"])
        selected = input(f"Choose a font number from 0 to {temp_int}: ")
        selected = int(selected)
        self.setFontByInt(selected)
        print(f"Change font to: {self.initializedFontDict["fontName"][selected]}")

    def incrementYcounter(self, incrementQty=None):
        if incrementQty == None:
            incrementQty=self.fontBitHeight
        if not ((self.yCounter + incrementQty) > (self.dispObj.height)):
            self.yCounter+=incrementQty
        else:
            self.yCounter = 0
            self.cls()
            
    def clsLine(self, fontWidth=None):
        if fontWidth == None:
            fontWidth = self.fontBitWidth
        if len(self.dispBufferList) > 0:
            del self.dispBufferList[-1]
        qtyColumns = int(self.dispObj.width / fontWidth)
        textString = " " * qtyColumns
        self.dispObj.draw_text8x8(0, self.yCounter, textString,
              color565(self.backGroundR, self.backGroundG, self.backGroundB))
    
    def cls(self, fontWidth=8, fontHeight=8, clearBuff=True):
        # This function operates using the built-in MicroPython font
        # It does not need to be setup to use any of the custom font variables
        if clearBuff:
            self.dispBufferList = []
        
        self.dispObj.clear(color=color565(self.backGroundR, self.backGroundG, self.backGroundB))
        
        self.yCounter = 0
        self.xCounter = 0
        
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
                pad = (self.yCharMax - textLen) % 3
                while pad > 0:
                    text+=" "
                    textLen = len(text)
                    pad = (self.yCharMax - textLen) % 3
                pad = int((self.yCharMax - textLen) / 3)
                
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
            
        if self.cursorType == 0:
            self.dispObj.fill_hrect(x_loc, y_loc, self.fontBitWidth, self.fontBitHeight,
                                               color565(r, g, b))
        else:
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
            
        
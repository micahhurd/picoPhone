from ili9341 import Display
from machine import Pin, SPI

import ili9341
from xglcd_font import XglcdFont


"""
This dictionary allows for the loading of all available fonts
The first item is that filename of the font file, the second
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
    "fixed": ["FixedFont5x8.c", 5, 8],
    # "ibm": ["IBMPlexMono12x24.c", 12, 24, None],
    # "neato": ["Neato5x7.c", 5, 7, None],
    # "neato2": ["NeatoReduced5x7.c", 5, 7, None],
    #"robotron": ["Robotron13x21.c", 13, 21, None],
    #"robotron2": ["Robotron7x11.c", 7, 11, None],
    # "ubuntu": ["UbuntuMono12x24.c", 12, 24, None],
    "unispace": ["Unispace12x24.c", 12, 24, None],
    # "unispace2": ["UnispaceExt12x24.c", 12, 24, None],
    "wendy": ["Wendy7x8.c", 7, 8, None]
    }


TFT_CLK_PIN = const(6)
TFT_MOSI_PIN = const(7)
TFT_MISO_PIN = const(4)

TFT_CS_PIN = const(13)
TFT_RST_PIN = const(14)
TFT_DC_PIN = const(15)



class display:
    
    def __init__(self):
        self.dispSizeX = 240
        self.dispSizeY = 320
        self.xCounter = 0
        self.yCounter = 0
        self.yStartPos = 0
        self.dispBufferList = []
        self.maxBufferLength = 0
        self.firstLineWritten = False
        self.displayObj = self.createMyDisplay()
        
        self.fontColorR = 255
        self.fontColorG = 255
        self.fontColorB = 255
        self.fontBitWidth = 0
        self.fontBitHeight = 0
        self.selectedFont = None
        self.initializedFontDict = {"fontName":["microPython"],"object":[None], "bitWidth":[8], "bitHeight":[8]}
        self.initializeFonts()
        self.setFontByInt(fontInt=0)
        
        
        
    def createMyDisplay(self):
        #spi = SPI(0, baudrate=40000000, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
        spiTFT = SPI(0, baudrate=51200000,
                     sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
        display = Display(spiTFT,
                          dc=Pin(TFT_DC_PIN), cs=Pin(TFT_CS_PIN), rst=Pin(TFT_RST_PIN),
                          width=self.dispSizeX, height=self.dispSizeY)
        
        
                
        return display
    
    def initializeFonts(self):
        # Initialize an object for each font
        print('Loading fonts...')
        initializedFontDict = {"fontName":[],"object":[]}
        for item in fontPack:
            filePath = f"./fonts/{fontPack[item][0]}"
            fontWidth = fontPack[item][1]
            fontHeight = fontPack[item][2]
            print(f"Attempting to initialize {item} font")
            try:
                fontObject = XglcdFont(filePath, fontWidth, fontHeight) 
                # fontPack[item][3] = fontObject
                self.initializedFontDict["fontName"].append(item)
                self.initializedFontDict["object"].append(fontObject)
                self.initializedFontDict["bitWidth"].append(fontWidth)
                self.initializedFontDict["bitHeight"].append(fontHeight)
                print("'-> Success!")
                
            except Exception as err:
                print(f"\'-> Failed... error: {err}")
                
        print(self.initializedFontDict["fontName"])
    
    def printInLine(self, textString):
        self.displayObj.draw_text(0, 0, textString, self.selectedFont,
                  ili9341.color565(self.fontColorR, self.fontColorG, self.fontColorB))
        self.displayObj.draw_text(0, 0, textString, self.selectedFont,
                  ili9341.color565(self.fontColorR, self.fontColorG, self.fontColorB))
    
    def dispWriteLowestLevel(self, string):
        if self.selectedFont == None:
            # Uses the built-in Micropython 8x8 font
            self.displayObj.draw_text8x8(0, self.yCounter, string,
                  ili9341.color565(self.fontColorR, self.fontColorG, self.fontColorB))
        else:
            self.displayObj.draw_text(0, self.yCounter, string, self.selectedFont,
                  ili9341.color565(self.fontColorR, self.fontColorG, self.fontColorB))
    
   
    def fontSize(self):
        fontWidth=self.fontBitWidth
        fontHeight=self.fontBitHeight
        print(f"fontWidth: {fontWidth}, fontHeight: {fontHeight}")
    
    def printAlt(self, textString, newLine=True):
        fontWidth=self.fontBitWidth
        fontHeight=self.fontBitHeight        
        
        def sendToDisp(textString, newLine, buffered=True):
            def sendDispBuffered(textString, newLine):
                self.dispBufferList.append(textString)
                if len(self.dispBufferList) > self.maxBufferLength:
                   del self.dispBufferList[0]
                
                self.cls(clearBuff=False)
                for bufferTextString in self.dispBufferList:
                    
                    self.dispWriteLowestLevel(bufferTextString)
                    self.incrementYcounter()
                    
            def sendDispNormal(textString, newLine):  
                newLine2 = newLine
                if self.firstLineWritten == False and self.yCounter == 0:
                    newLine2 = False
                    self.firstLineWritten = True
                
                if newLine2:
                    self.incrementYcounter()
                else:
                    self.clsLine()
                    
                self.dispWriteLowestLevel(textString)
            
            if buffered:
                sendDispBuffered(textString, newLine)
            else:
                sendDispNormal(textString, newLine)
            
                  
        self.maxBufferLength = int(self.dispSizeY / fontHeight)
        maxChar = int(self.dispSizeX / fontWidth)
        
        
        stringList = textString.split(" ")
        for index, item in enumerate(stringList):
            item+=" "
            stringList[index] = item

        stringListLength = len(stringList)


        index = 0
        outputString = ""
        while True:
            currentWord = stringList[index]

            if len(currentWord) > maxChar:
                if len(outputString) > 0:
                    sendToDisp(outputString, newLine)
                    outputString = ""

                remainder = ""
                for i, char in enumerate(currentWord):
                    if len(outputString) < maxChar:
                        outputString+=char
                    else:
                        remainder += char
                stringList[index] = remainder
                sendToDisp(outputString, newLine)
                outputString = ""
                index-=1
            elif len(currentWord)== maxChar:
                if len(outputString) > 0:
                    printLine(outputString)
                    outputString = ""
                outputString = currentWord
                sendToDisp(outputString, newLine)
                outputString = ""
            else:
                currentLength = len(outputString) + len(currentWord)
                if currentLength <= maxChar:
                    outputString += currentWord

                else:
                    sendToDisp(outputString, newLine)
                    outputString = ""
                    index-=1

            index+=1
            if index >= (stringListLength):
                sendToDisp(outputString, newLine)
                break

        
    def selectFont(self):
        temp_int = len(self.initializedFontDict["fontName"]) - 1
        print("Loaded Fonts:")
        print(self.initializedFontDict["fontName"])
        selected = input(f"Choose a font number from 0 to {temp_int}: ")
        selected = int(selected)
        self.setFontByInt(selected)
        print(f"Change font to: {self.initializedFontDict["fontName"][selected]}")
        
    def setFontByInt(self, fontInt=0):
        self.selectedFont = self.initializedFontDict["object"][fontInt]
        self.fontBitWidth = self.initializedFontDict["bitWidth"][fontInt]
        self.fontBitHeight = self.initializedFontDict["bitHeight"][fontInt]
        self.cls()

    def incrementYcounter(self, incrementQty=None):
        if incrementQty == None:
            incrementQty=self.fontBitHeight
        if not ((self.yCounter + incrementQty) > (self.dispSizeY)):
            self.yCounter+=incrementQty
        else:
            self.yCounter = 0
            self.cls()
            
    def clsLine(self, fontWidth=None):
        if fontWidth == None:
            fontWidth = self.fontBitWidth
        if len(self.dispBufferList) > 0:
            del self.dispBufferList[-1]
        qtyColumns = int(self.dispSizeX / fontWidth)
        textString = " " * qtyColumns
        self.displayObj.draw_text8x8(0, self.yCounter, textString,
              ili9341.color565(self.fontColorR, self.fontColorG, self.fontColorB))
    
    def cls(self, fontWidth=8, fontHeight=8, clearBuff=True):
        # This function operates using the built-in MicroPython font
        # It does not need to be setup to use any of the custom font variables
        if clearBuff:
            self.dispBufferList = []
        self.yCounter = 0
        self.firstLineWritten = False
        qtyLines = int(self.dispSizeY / fontHeight)
        qtyColumns = int(self.dispSizeX / fontWidth)
        textString = " " * qtyColumns
        
        for line in range(qtyLines):
            self.displayObj.draw_text8x8(0, self.yCounter, textString,
                  ili9341.color565(self.fontColorR, self.fontColorG, self.fontColorB))
            self.yCounter+=fontHeight
        self.yCounter = 0
    
    
        
    def setFontColor(self, color="white"):
        colorDict = {
            "white": (255,255,255),
            "red": (255,0,0),
            "green": (0,255,0),
            "blue": (0,0,255),
            "yellow": (255,255,0),
            "purple": (230,230,250),
            "thistle": (216,191,216),
            "plum": (221,160,221),
            "orange": (255,165,0),
            "black": (0,0,0)
            }
        
        self.fontColorR = colorDict[color][0]
        self.fontColorG = colorDict[color][1]
        self.fontColorB = colorDict[color][2]
        
        


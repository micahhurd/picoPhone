
import standardLibrary as slib

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
    
    # self.yCharMax = self.calc_yCharMax() - self.borderBottom - self.borderTop + 1

def alphaEntrySingle(self, banner=None, collectedStr = ""):
    
    # self=keypad
    self.lcd.cursorType = 1 # Apply a non-standard cursor type
    pip = self.lcd.dispWriteLowestLevel # pip stands for "Print In Place"
    if banner != None:
        self.lcd.print(banner)   
    
    collect = True
    
    
    tempStr = ""
    pendingQue =""
    char = ""
    while True:
           
        char = self.keyIn()
                        
        if char == "*":
            print("*")
            if tempStr == "":
                pendingQue = self.dictionary[tempStr]
            collectedStr += pendingQue
            # self.lcd.print(f"\\r{collectedStr}")
            return collectedStr
        elif char == "#":
            return "ctrl#"
        elif char == "A":
            return "ctrlA"
        elif char == "B":
            return "ctrlB"
        elif char == "C":
            return "ctrlC"
        elif char == "D":
            return "ctrlD"
            
        else:
        
            if (not char in tempStr) and (len(tempStr) > 0):
                tempStr = char
            else:
                tempStr+=char
                
            if (not tempStr in self.dictionary):
                if tempStr[-1] in self.dictionary:
                    tempStr = tempStr[-1]
                else:
                    tempStr = ""
            
    self.lcd.cursorType = 0
    return collectedStr

def reader(self, string, kPadDriver=None, editor=True, bottomMsg="(NEXT MSG...)", inPrompt=""):
    # self=lcd
    def toLCD(currentLine, end="\n"):
        # utime.sleep(0.01)
        # print(f"len CurrentLine: {len(currentLine)}, length xCharMax: {self.xCharMax}")
        if len(currentLine) < (self.xCharMax):
            # print("equalizing string")
            currentLine = equalizeLine(currentLine, self.xCharMax)
        tempInt = self.xCounter
        self.xCounter=0
        self.dispWriteLowestLevel(currentLine)
        if end == "\n":
            self.incrementY()
        self.xCounter = tempInt
        
    
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
                
                return endFlag, stringList
            
            if index < 0:
                self.clearLine(end="")
                toLCD("(PREVIOUS MSG...)")
                endText = ""
                
            else: # index < (len(stringList)):
                if index == len(stringList) and len(stringList) > self.yCharMax:
                    print(1234)
                    return endFlag, stringList
                
                if startIndex >=0 and endIndex <= len(stringList):
                    endText = "..."
                     
                toLCD(stringList[index])
                
                if index >= len(stringList) - 1:
                    self.clearLine(end="") # Fills out blanks
                    endText = bottomMsg
                    endCntr+=1
                    endFlag = 1
                else:
                     endCntr=0
                     
        self.clearLine(end="")
        
        if endText == bottomMsg and editor:
            
            # Check if the user can edit the final line in the list (if it's short enough)
            # If yes, the load it into colleted, and delete it from the end of the stringList
            # otherwise collected is empty
            if len(stringList[-1]) < (self.yCharMax - len(inPrompt)):
                collected = stringList[-1].strip()
                del stringList[-1]
                tempStr = f"{inPrompt}{collected}"
                print(f"tempStr to LCD >{tempStr}<")
                self.yCounter-=1
                self.clearLine()
                toLCD(tempStr, end="")
                self.xCounter = len(tempStr)
            else:
                collected = ""
                self.xCounter = len(inPrompt)
                toLCD(inPrompt, end="")
            
            cnt=0
            
            while True:
                xCntrDelta = 0
                print(f"Text Collec {cnt}")
                cnt+=1
                char = alphaEntrySingle(banner=None, collectedStr = "")
                if char == "ctrl#":
                    collected = collected[:-1]
                    xCntrDelta = -1
                elif char == "ctrlA" or char == "ctrlB":
                    if "A" in char:
                        cmd = "a"
                    else:
                        cmd = "b"
                    if len(collected) > 0:
                        collected = equalizeLine(collected, self.xCharMax)
                        stringList.append(collected)
                    endCntr = 0
                    break
                elif char == "ctrlC":
                    pass
                elif char == "ctrlD":
                    pass
                else:
                    print(f"char: {char}")
                    xCntrDelta = 1
                    collected += char
                
                tempStr = f"{inPrompt}{collected}"
                print(f"tempStr: {tempStr}")
                toLCD(tempStr, end="")
                self.xCounter+=xCntrDelta
                
                if len(collected) == (self.xCharMax - len(inPrompt)):
                    stringList.append(collected)
                    cmd = "b"
                    break
                
            if cmd == "a":
                indexDelta = -1
            if cmd == "b":
                indexDelta = 1            
                
        else:
            toLCD(endText, end="")
            self.xCounter = len(endText)
            cmd = kPadDriver.keyIn(cursorOn=1)
            cmd = cmd.lower()
            print(1)
            if cmd == "a":
                indexDelta = -1
            if cmd == "b":
                indexDelta = 1
                if endCntr == 1 and endFlag == 1:
                    break
    
    return (endFlag, stringList)

def reader2(self, string, kPadDriver=None, editor=True, bottomMsg="(NEXT MSG...)", inPrompt=""):
    #self=lcd
    def incrementY():
        if not (self.yCounter > self.yCharMax):
            self.yCounter+=1    
        
    def toLCD(currentLine, end="\n"):
        # utime.sleep(0.01)
        # print(f"len CurrentLine: {len(currentLine)}, length xCharMax: {self.xCharMax}")
        if len(currentLine) < (self.xCharMax):
            # print("equalizing string")
            currentLine = equalizeLine(currentLine, self.xCharMax)
        tempInt = self.xCounter
        self.xCounter=0
        self.dispWriteLowestLevel(currentLine)
        if end == "\n":
            incrementY()
        self.xCounter = tempInt
    
    def parseInput(indexDelta):
        char = alphaEntrySingle(banner=None, collectedStr = "")
        
        if char == "ctrlA":
            if indexDelta == -1:
                exitFlag = -1
                return "exit", indexDelta
            else:
                indexDelta-=1
            return "", indexDelta
        if char == "ctrlB":
            if (self.yCharMax + indexDelta) == (len(stringList) + 1):
                exitFlag = 1
                return "exit", indexDelta
            else:
                indexDelta+=1
            return "", indexDelta
        if char == "ctrlC":
            pass
        if char == "ctrlD":
            pass
        
    
    def printText(textList, indexDelta, cmd):
        status = ""
        startIndex = indexDelta
        self.yCounter = self.borderTop
        # print(self.yCharMax)
        endIndex = self.yCharMax + indexDelta - 1
        if endIndex >= len(textList):
            endIndex = len(textList)
        if endIndex == len(textList) and indexDelta == 0:
            status = "BOF EOF"
        elif endIndex == len(textList):
            status = "EOF"
        else:
            status = "REMAINING"
        # print(f"{len(textList)} {endIndex}")
        
        # If the end of the text list is reached
        if (self.yCharMax + indexDelta) == (len(stringList) + 1):
                exitFlag = 1
        
        if cmd == "before":
            toLCD("(Prev)", end="\n")
        for index in range(startIndex, endIndex):
            # print(f"len stringList {len(textList)}, index {index}")
            string = textList[index]
            toLCD(string, end="\n")
            # print(self.yCounter)
        
        return status, indexDelta
        
    
    stringList = convertStringToList(string, self.xCharMax)
    
    exitFlag = 0
    indexDelta = 0
    startIndex = 0
    endIndex = startIndex + self.yCharMax
    while True:
        status, indexDelta = printText(stringList, indexDelta)
        cmd, indexDelta = parseInput(indexDelta)
        print(f":: status {cmd} delta {indexDelta}")
        if cmd == "exit":
            input(":::")
            return (exitFlag, stringList)
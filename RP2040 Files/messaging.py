# Version 0.008
import config as cfg
import standardLibrary as slib
import utime

def extractMessageFromCSV(string):
    index = slib.findNthOccurence(string, ",", 5) # The message portion of the string should be the fifth CSV index
    tempStr = f"{string[index:]}"
    tempStr = tempStr[1:] # Get rid of the leading comma
    tempStr = tempStr.strip()
    return tempStr

class msgs:
    
    def __init__(self, msgsName, msgsType, msgsLogFile, display, keypad, outbox=cfg.outbox_file):
        self.msgsName = msgsName
        self.msgsType = msgsType
        self.msgsLogFile = msgsLogFile
        self.lcd = display
        self.kpd = keypad
        self.outbox = outbox
        self.temp_msg_file = cfg.temporary_msg_file
        
    def inbox(self):
        number, name = self.displayInbox()			# User chooses message channel
        if number == "exit":
            return 0
        elif number == "compose new":
            userResponse = 2
            number, name = slib.selectContact(self.lcd)
        else:
            userResponse = self.readMsgs(number, name)	# User reads through messages in the channel
        # userResponse value 2 = he pressed the return key
        # userResponse value 3 = he pressed the enter key
        if userResponse == 2:
            msgToSend = slib.respondMsg(self.lcd, number, name)	# User optionally responds to the channel
            
        if msgToSend != "":
            slib.writeToOutboxFile(number, name, self.msgsType, msgToSend)	# New message is placed in the outbox file
            # Write the message to the outbox file
        
    def displayInbox(self):
        lcd=self.lcd
        kpd=self.kpd
        message_file=self.msgsLogFile
        
        def getNewestTimestamp(searchNumber):
            fp = open(message_file)
            newestTimestamp = 0
            for index, line in enumerate(fp):
                tempList = line.split(",")
                cellNumber = tempList[0]
                
                if cellNumber == searchNumber:
                    date = tempList[1]
                    timestamp = int(slib.dateToTS(date))
                    if timestamp > newestTimestamp:
                        newestTimestamp += timestamp
            fp.close()
            return newestTimestamp
                    
        def sort_key(index):
            return index[3]
        
        message_groups = []
        number_list = []
        fp = open(message_file)
        for index, line in enumerate(fp):
            
            tempList = line.split(",")
            cellNumber = tempList[0]
                            
            if cellNumber not in number_list:
                number_list.append(cellNumber)
                
                if cellNumber in cfg.contact_list.keys():
                    first = cfg.contact_list[cellNumber][0]
                    last = cfg.contact_list[cellNumber][1]
                else:
                    first = "Unknown"
                    last = ""
                
                timestamp = getNewestTimestamp(cellNumber)
                message_groups.append((cellNumber, first, last, timestamp))
        fp.close()
        
        message_groups.sort(key=sort_key, reverse=True)	# Sort from newest to oldest
        
        # ====== Setup to display to the user ===========
        lcd.cls(clsA=True)
        lcd.setBorder(string=f"{self.msgsName} Inbox", function="top")
        lcd.setBorder(string=f"[{lcd.upKey}]: Up,   [{lcd.downKey}]: Down\n[{lcd.escKey}]: Exit, [{lcd.returnKey}]: Select\n[#]: Compose New", function="bottom")
        
        # Generate a list of messages from the message history file
        tempList = []
        for index, item in enumerate(message_groups):
            tempList.append(f"{index}: {item[1]} {item[2]}")
            # lcd.print(f"{index}: {item[1]} {item[2]}")
        
        # Display the message to the user, so he can select a message
        indexSelected = lcd.printList(tempList)
        
        if indexSelected >= 0:	# Pound sign indicates user has chosen compose a new message
            number = message_groups[indexSelected][0]
            name = f"{message_groups[indexSelected][1]} {message_groups[indexSelected][2]}"
        elif indexSelected == -4:
            number = "compose new"
            name = "compose new"
        else:
            number = "exit"
            name = "exit"
        return (number, name)
        

    

    def readMsgs(self, contact_number, contact_name):
        lcd =self.lcd
        keypad = self.kpd
        message_file = self.msgsLogFile
        temp_msg_file = self.temp_msg_file
        
        def sort_key(index):
            return index[0]
        
        def initializeMsgs(contact_number, message_file):
            
            sortList = []
            fp = open(message_file)
            for index, line in enumerate(fp):
                number = line.split(",")[0]
                if number == contact_number:
                    
                    date = line.split(",")[1]
                    timestamp = slib.dateToTS(date)
                    #input(f"{date} {timestamp}")
                    sortList.append((timestamp, index))        
            fp.close()
            
            # print(sortList)
            
            sortList.sort(key=sort_key, reverse=True)
            # print(sortList)
            slib.writeTempFile(filePath=cfg.temporary_msg_file, flush=True)
            # input(":")
            for index, item in enumerate(sortList):
                
                lineNumer = item[1]
                
                messageLine = slib.readFileAtLine(message_file, lineNumer).strip()
                # print(messageLine)
                
                slib.writeTempFile(data=messageLine, filePath=cfg.temporary_msg_file)
                # input(item)
        
        # Get messages from the history file, and put them into a temp
        # file for viewing (this saves from possibility of overloading
        # ram with too many messages)
        initializeMsgs(contact_number, message_file)
        
        # Get the number of messages available
        qtyMessages = slib.txtFileLength(temp_msg_file)
        
        # Get the display going
        lcd.cls(clsA=True)
        lcd.setBorder(string=f"[{lcd.upKey}]: Up,   [{lcd.downKey}]: Down\n[{lcd.escKey}]: Exit, [{lcd.returnKey}]: Reply", function="bottom")
        
        # Go through the messages
        index = 0
        while True:
            cnt=index+1	# For the GUI, to indicate which message number is displayed
    
            lcd.cls()          
            currentMsgCSVlist = slib.readFileAtLine(temp_msg_file, index).strip()
            tempList = currentMsgCSVlist.split(",")
            message = extractMessageFromCSV(currentMsgCSVlist)
            date_time = tempList[1].split(" ")
            date = date_time[0]
            time = date_time[1][:-3] # The slice at the end is to get rid of the seconds
            
            # Print time, date, and message number of total, to the second from top line (screen line index 1)
            #tempStr = f"{date} {time} [{cnt}/{qtyMessages}]"
            lcd.printBuffer(string=f"{date} {time} [MSG {cnt}/{qtyMessages}]", indexToPrint=1, printOverLockedLines=True)
            
            # Must be updated eventually to supper group chats
            # Must look up the sender in the address book
            sender = tempList[4]
            contact_name = contact_name.replace("\n", "")
            if sender == contact_number:
                
                sender = f"Rcvd From: {contact_name}\n"
                
            else:
                sender = slib.searchContactList(sender, returnParameter="name")
                sender = f"Sent by {sender}\n"
            
            tempStr = f"{contact_name} Inbox\n"+sender+f"{date} {time} [MSG {cnt}/{qtyMessages}]"
            
            lcd.setBorder(string=tempStr, function="top")
            
            # Display the current message for the user to view
            scrollDirection = lcd.printMsgs(message, autoScroll=True, abbreviateScroll=True)
            
            # Manage the users control response
            if scrollDirection >= -1 and scrollDirection <= 1:		# Capture just scroll direction commands
                index+=scrollDirection
            elif scrollDirection == 2:	# 2 corresponds to the return key
                break
            elif scrollDirection == 3:	# 3 corresponds to the escape key
                break
                              
            # Prevent error from scrolling beyond message quantity limits            
            if index >= qtyMessages:
                index = qtyMessages - 1
            
            if index < 0:
                index = 0
    
        
        # return value 2 corresponds to the return key
        # return value 3 correspons to the escape key
        return scrollDirection

    
            
    
    

# year = 2022
# month = 7
# mday = 1
# hour = 6
# minute = 30
# second = 30
# weekday = None
# yearday = None



# temp = dateToTS("2022-07-02 06:02:15")
# input(f"temp: {temp}")
# getMessages("+19728370200", cfg.msg_file)
# displayMessage(None, None, cfg.temporary_msg_file)


import config as cfg
import standardLibrary as slib
import time



number = +19728370200

       

def getMessages(contact_number, message_file):
    def sort_key(index):
        return index[0]

    sortList = []
    fp = open(message_file)
    for index, line in enumerate(fp):
        number = line.split(",")[0]
        if number == contact_number:
            
            date = line.split(",")[1]
            timestamp = slib.dateToTS(date)
            sortList.append((timestamp, index))        
    fp.close()
    
    sortList.sort(key=sort_key, reverse=True)
    
    for item in sortList:
        lineNumer = item[1]
        messageLine = slib.readFileAtLine(message_file, lineNumer).strip()
        # print(messageLine)
        slib.writeTempFile(flush=True)
        slib.writeTempFile(data=messageLine)
        
        
    

year = 2022
month = 7
mday = 1
hour = 6
minute = 30
second = 30
weekday = None
yearday = None



# temp = dateToTS("2022-07-02 06:02:15")
# input(f"temp: {temp}")
getMessages("+19728370200", cfg.msg_file)


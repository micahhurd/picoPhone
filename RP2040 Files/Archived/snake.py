import utime
# These are my files
import standardLibrary as slib
import lcdDriver
import keypadDriver
from ili9341 import color565

from machine import Pin, Timer
import utime

row_list = [4, 5, 8, 9]
col_list = [3, 2, 1, 0]

for x in range(0,4):
    row_list[x]=Pin(row_list[x], Pin.OUT)
    row_list[x].value(1)
    
for x in range(0,4):
    col_list[x] = Pin(col_list[x], Pin.IN, Pin.PULL_UP)
    

key_map=[["D","#","0","*"],\
        ["C","9","8","7"],\
        ["B","6","5","4"],\
        ["A","3","2","1"]]

def Keypad4x4Read(cols,rows):
    for r in rows:
        r.value(0)
        result=[cols[0].value(),cols[1].value(),cols[2].value(),cols[3].value()]
        if min(result)==0:
            key=key_map[int(rows.index(r))][int(result.index(0))]
            r.value(1) # manages key keept pressed
            return(key)
        r.value(1)

global keyGot
keyGot = None
def pollKeypad():
    global keyGot
    key=Keypad4x4Read(col_list, row_list)
    if key != None:
        
        keyGot = key
        
        print("You pressed: "+key)
        utime.sleep(0.1)
    
def hi():
    print("hi")
    

timer_two = Timer()
def startPolling():
    timer = Timer(-1)
    timer.init(freq=1, mode=Timer.PERIODIC, callback=lambda t:pollKeypad())
    # Start the main loop
    
    
   
        
        

lcd = lcdDriver.display()


color = color565(lcd.fontColorR, lcd.fontColorG, lcd.fontColorB)
black = color565(0,0,0)

def fillBlock(direction, x, y, color):
    if direction == 0:
        x-=4
    elif direction == 90:
        y+=4
    elif direction == 180:
        x+=4
    elif direction == 270:
        y-=4
    lcd.dispObj.fill_rectangle(x, y, 4, 4, color)

def newXY(direction, x, y):
    if direction == 0:
        x+=4
    elif direction == 90:
        y-=4
    elif direction == 180:
        x-=4
    elif direction == 270:
        y+=4
    return x, y


def getKey(keyGot, direction):
    keyGot = str(keyGot)
    if keyGot == "2":
        direction = 90
    elif keyGot == "4":
        direction = 180
    elif keyGot == "8":
        direction = 270
    elif keyGot == "6":
        direction = 0
    return direction
    
        
width = 4
length = 8
locX = 1
locY = 1
lcd.dispObj.fill_rectangle(locX, locY, width, length, color)


startPolling()

direction = 270
while True:
    utime.sleep(1)
    direction = getKey(keyGot, direction)
    print(f'direction {direction} keyGot {keyGot}')
    
    lcd.dispObj.fill_rectangle(locX, locY, width, length, color)

    newX, newY = newXY(direction, locX, locY)

    fillBlock(direction, locX, locY, black)

    locX = newX
    locY = newY
    # print(f"{locX} {locY}")
    
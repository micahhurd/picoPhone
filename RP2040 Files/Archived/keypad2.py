from machine import Pin
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


print(1)

while True:
    key=Keypad4x4Read(col_list, row_list)
    if key != None:
        print("You pressed: "+key)
        utime.sleep(0.3)

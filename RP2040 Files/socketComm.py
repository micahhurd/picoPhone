import socket
import config as cfg
import utime
import standardLibrary as slib

class communication:
    
    def __init__(self, lcd=None):
        self.lcd = lcd
        self.term = b'EOF\n'
        self.conn = None
        
    def connTx(self, string, conn=None, term="EOF\n"):
        if conn == None:
            conn = self.conn
        print("Sending message to Client")
        string+=term
        string = bytes(string, 'utf-8')
        conn.send(string)
    
    def connRx(self, conn=None, term="EOF\n"):
        if conn == None:
            conn = self.conn
        print("Waiting for response from Client")
        termLen = len(term)
        emptyByteCounter = 0
        client_sent = ""
        bucketLen = 0
        eofBucket = ""
        while (emptyByteCounter < 20):
            tempByte = conn.recv(1)
            tempStr = tempByte.decode("utf-8")
        
            eofBucket += tempStr
            if len(eofBucket) > termLen:
              client_sent += eofBucket[0]
              eofBucket = eofBucket[1:]
              if eofBucket == term:
                break
        return client_sent
            
    
    
    def initConnection(self):
        delay = cfg.socket_comm_delay
        s=socket.socket();
        s.settimeout(5)
        s.setblocking(True)
        utime.sleep(delay)
        
        try:
            s.connect((cfg.socket_server_IP, cfg.socket_port))
        except Exception as err:
            self.pLCD(f'SockConn-ERR#: {err} ')
            return False
        
        self.pLCD("\\nConnecting to server, waiting for ACK...")
        cmd=s.recv(1024)
        if cmd.startswith('ACK') == False: # I have Server send 'ACK' on connect
            self.pLCD(f"No ACK from server: {cmd}")
            s.close()
            return False
             
        else:            
            self.pLCD(f'Received server ACK')
            self.pLCD(f'Authenticating...')
            msg=self.connRx(conn=s)
            if msg == "USER":
                self.pLCD(f'sending username')
                self.connTx(cfg.server_user, conn=s)
            else:
                self.pLCD(f'Authentication Failed!')
                return False
            msg=self.connRx(conn=s)
            if msg == "PASS":
                self.pLCD(f'sending password')
                self.connTx(cfg.server_pass, conn=s)
            else:
                self.pLCD(f'Authentication Failed!')
                return False
            
            msg=self.connRx(conn=s)
            if msg != "AUTH VALID":
                self.pLCD(f'Authentication Failed! got message: {msg}')
                return False
            self.pLCD(f'Authentication Success!')
            
            self.conn = s
            return True
                   
    
    def get_msgs(self):
        if self.conn == None:
            self.pLCD(f'Get messages err: no connection!')
            return False
        
        self.pLCD("Checking server for any new messages...")
        self.connTx("GET MSGS")
        msgs = self.connRx()
        if msgs == "NO MSG":
            self.pLCD("Received no messages.")
            return False
        elif msgs == "MSG START":
            self.pLCD("Downloading messages...")
            msgQty = 0
            while True:
                msgs = self.connRx()
                if msgs != "MSG END":
                    msgQty+= self.sendToFile(msgs)
                    self.pLCD(".", end="")
                else:
                    break
            
            self.pLCD("")
            msgs = self.connRx()
            try:
                tempList = msgs.split(":")
                qtyReported = int(tempList[1])
            except:
                qtyReported = 0
            
            msgs = f"MSG QTY:{msgQty}"
            self.connTx(msgs)
            
            msgs = self.connRx()
            
            if msgs == "MSQ QTY NONPARITY":
                self.pLCD(f"WARNING: Server report message nonparity!")                 
        self.pLCD(f"Received {msgQty} messages.")
        self.pLCD("Message download complete!")
        return True
    
    
    def sendMsgs(self, file):
        if self.conn == None:
            self.pLCD(f'Get messages err: no connection!')
            return False
        
        self.pLCD("Uploading msgs to server...")
        self.connTx("SEND MSGS")
        msg = self.connRx()
        if msg != "MSG START":
            return False
        else:
            self.pLCD("Upload in progress")
            outputList = []
            fp = open(file)
            clientSentQty = 0
            for index, msg in enumerate(fp):
                msg = msg.strip()
                tempList = msg.split(",")
                msgType = tempList[-1]
                
                if msgType == "signal" or msgType == "discord" or msgType == "email":
                    self.connTx(msg)
                    clientSentQty+=1
                    self.pLCD(".", end="")
                    
                else:
                    # Only append lines not transmitted
                    outputList.append(msg)
        
            self.connTx("MSG END")
            utime.sleep(0.1)
            self.connTx(f"MSG QTY:{clientSentQty}")
            self.pLCD("\\nMsg upload complete!")
            
            response = self.connRx()
            qtyMsgsRcvd = int(response.split(":")[1])
            
            if qtyMsgsRcvd == clientSentQty:
                self.pLCD("Server reports parity!")
                
                # Overwrite outbox file to contain only messages not sent
                slib.writeTempFile(filePath=file, flush=True)
                if len(outputList) > 0:
                    for item in outputList:
                        slib.writeTempFile(data=item, filePath=file)
                
                return True
            else:
                self.pLCD("Server reports non-parity!")
                self.pLCD(f"Sent {clientSentQty} msgs, server received {qtyMsgsRcvd}")
                return False
    
    def close_conn(self):
        self.connTx("END")
        self.conn.close()
        self.conn = None
        self.pLCD("Terminated server connection")
        
        
    def pLCD(self, string, end=None):
        if self.lcd!= None:
            if end != None:
                self.lcd.print(string, end=end)
            else:
                self.lcd.print(string)
        else:
            print(string)
                      
    def sendToFile(self, msgString):
        msgString = msgString.strip()
        if msgString !="":
            slib.writeTempFile(msgString, filePath=cfg.inbox_file)
            return 1
        else:
            return 0
        
            

            
                      
                      

#!/usr/bin/python
import config as cfg
import time
import socket
import os

import standardLibrary as slib
from standardLibrary import cache


def recordPID():
    import os
    tempStr = os.getpid()
    print(f"This process has the PID: {tempStr}")
    cache.put("socket_server_pid", tempStr)



def setupSocket(port):
    s = socket.socket()
    host = socket.gethostname()

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # added allow to reuse when re-run

    try:
        s.bind(('', port))  # Needed (('',port)) or client never saw it
    except Exception as err:
        err = str(err)
        slib.error_and_exit(f"Got error when trying to start server: \n\n{err}")

    s.listen(5)

    return s, host


def connTx(conn, string, term="EOF\n"):
    string = str(string)
    print("Sending message to Client")
    string += term
    string = bytes(string, 'utf-8')
    conn.send(string)


def connRx(conn, term="EOF\n"):
    print("Waiting for response from Client")
    termLen = len(term)
    emptyByteCounter = 0
    client_sent = ""
    check = ""
    bucketLen = 0
    eofBucket = ""
    while check != term and (emptyByteCounter < 20):
        tempByte = conn.recv(1)
        tempStr = tempByte.decode("utf-8")
        # input(f">{tempStr}<: ")

        eofBucket += tempStr
        if len(eofBucket) > termLen:
            client_sent += eofBucket[0]
            eofBucket = eofBucket[1:]
            if eofBucket == term:
                break

        # input(f"tempStr>{tempStr}\n bucket >{eofBucket}\n term >{term}\n cliSent: >{client_sent}<")
    return client_sent


def connectAuth(conn, user="guest", password="guest"):
    returnBool = False
    connTx(conn, "ACK")

    connTx(conn, "USER")
    user_submitted = connRx(conn)

    connTx(conn, "PASS")
    pass_submitted = connRx(conn)

    if user == user_submitted and password == pass_submitted:
        # print("password validated")
        returnBool = True

    return returnBool


def transmitMessages(connection):
    print("Sending client their messages...")
    list_of_messages = slib.readTxtFile(cfg.outbox_file, outputFormat="list")
    qtyMsgs = len(list_of_messages)
    qtyMsgsRcvd = 0

    if qtyMsgs == 0:
        connTx(connection, "NO MSG")
    else:
        connTx(connection, "MSG START")

        for msg in list_of_messages:
            msg = msg.strip()
            msg += "\n"
            connTx(connection, msg)

        connTx(connection, "MSG END")
        connTx(connection, f"MSG QTY:{qtyMsgs}")

        response = connRx(connection)

        tempList = response.split(":")
        qtyMsgsRcvd = int(tempList[1])

        if qtyMsgsRcvd == qtyMsgs:
            # Communicate that the client received all messages
            connTx(connection, "MSG QTY PARITY")
            print("Message parity")

            # Clear the outbox file
            with open(cfg.outbox_file, 'w') as file:
                pass
        else:
            # Communicate client did NOT receive all messages; don't clear outbox file
            connTx(connection, "MSQ QTY NONPARITY")
            print("Message non-parity")

    print(f"Sending client messages complete! Sent {qtyMsgs} messages, client received {qtyMsgsRcvd} messages.")


def sendToFile(msgString):

    msgString = msgString.strip()
    if msgString != "":

        msgString+="\n"
        with open(cfg.inbox_file, "a+") as filehandle:
            filehandle.write(msgString)
        return 1
    else:
        return 0


def receiveMessages(connection):
    print("Receiving client messages...")
    connTx(connection, "MSG START")
    msgQtyRcvd = 0
    while True:
        msg = connRx(conn)
        if msg != "MSG END":
            if msg != "":
                msgQtyRcvd += sendToFile(msg)
                print(".", end="")
        else:
            break
    print("")

    response = connRx(connection)
    time.sleep(1)
    connTx(connection, f"MSG QTY:{msgQtyRcvd}")
    tempList = response.split(":")
    qtyClientSent= int(tempList[1])

    if qtyClientSent == msgQtyRcvd:
        # Communicate that the client received all messages
        print("Message parity")

    else:
        # Communicate client did NOT receive all messages; don't clear outbox file
        print("Message non-parity")

    print(f"Receiving client messages complete! Received {msgQtyRcvd} messages, client sent {qtyClientSent} messages.")


#
# **** While True Loop ****
recordPID()     # Enter PID of the server into the cache file
s, host = setupSocket(cfg.socket_port)  # Setup the server listening connection
i_cnt = 0
while True:
    print("\n===============================================================")
    print(f"Running server with hostname {host} at port {cfg.socket_port}")
    print("Waiting for connection...")
    print("===============================================================\n")
    timestamp = slib.getTstampSeconds()
    cache.put("connection_pending", timestamp)
    conn, addr = s.accept()  # Waits here until connection...

    # Mark time of connection start
    timestamp = slib.getTstampSeconds()
    cache.put("connection_start", timestamp)

    authorizedBool = connectAuth(conn, user=cfg.server_user, password=cfg.server_pass)
    if authorizedBool:
        print("PASSWORD VERIFIED")
        connTx(conn, "AUTH VALID")

        while True:

            cmd = connRx(conn)
            print(f"client sent cmd {cmd}")

            if cmd == "GET MSGS":
                response = transmitMessages(conn)

            elif cmd == "SEND MSGS":
                response = receiveMessages(conn)

            elif cmd == "END":
                print("Ending connection with client...")
                conn.close()
                print("Closed client connection!")
                break

            else:
                print(f"received unknown command from client: {cmd}")
                connTx(conn, "UNK")

    else:
        tempStr = "AUTH FAILED"
        connTx(conn, f"{tempStr}...\n")
        print("User and password not verified!")

#
# # ======================================================================================================
#   print('c, addr: ', c, addr)
#   print('Waiting for data from ESP8266...')
#   # it printed... c, addr:  <socket._socketobject object at 0x7ff4d063c670> ('192.168.1.200', 3073)
#   print("Connection accepted from " + repr(addr[1]) + "  Server ready for file transfer...\n")
#   # it printed... Connection accepted from xxxx  Server ready for file transfer...
#   #
#   # ACK the client, get filename and open file for writes
#   starttime = time.time()    # measure start of ET to get and write file
#   tempByte = bytes("ACK...\n", 'utf-8')
#   connection.send(tempByte)         # SEND MESSAGE TO CLIENT TO SEND DATA
#   #
#   tfile = "Server-WIP"
#   fobj = open(tfile, "w")
#   #
#   # Incoming Data, loop until "FILE-EOF", then repeat for additional file(s)
#   # get next line...
#
#   #
#   emptyByteCounter = 0
#   client_sent = ''
#   while client_sent != 'EOF\n' and (emptyByteCounter < 20):
#     client_sent = connection.recv(1026)
#
#     if client_sent != b'':
#       emptyByteCounter = 0
#     elif client_sent == b'':
#       emptyByteCounter+=1
#
#     tempStr = client_sent.decode("utf-8")
#     print(tempStr)
#     if tempStr != "EOF\n":
#       fobj.write(tempStr)
#
#     #
#   ######### HIT EOF\n
#   localtime = time.asctime( time.localtime(time.time()) )
#   print(localtime)
#   E_Time = (time.time() - starttime)
#   print("Elapsed Time:  %.2f Seconds" % E_Time)
#   fobj.write("Server:,,,,,Elapsed Time:  %.2f Seconds" %  E_Time + '\n' )
#   fobj.write("Server:,,,,,Program Name:  %s " %prg_n + '\n' )
#   fobj.close()
#   os.chmod(tfile,0o666) # assign RW- to Owner, Group, Other
#   os.rename(tfile, tfile[0:18] + '-' + str(i_cnt))
#   i_cnt += 1
#   print('addr[1]: '+repr(addr[1])+' FILE XFER DONE for: '+tfile[0:18]+'-'+ str(i_cnt))
#   #
#   ### close the socket
#   ### a new socket will be created for next upload;
#   ### as the client closes its socket after uploads
#   ###
#   print('ALL FILES RCVD this session')
#   print('close socket, open new socket and wait for next upload')
#   print('Back to top level # "**** While True Loop ****"\nServer Prog: ' + prg_n)
#   s.close()

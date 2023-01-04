import config as cfg
import standardLibrary as slib
from standardLibrary import cache
import time
import datetime
import subprocess

def recordPID(cachVarID: str):
    import os
    tempStr = os.getpid()
    print(f"This process has the PID: {tempStr}")
    cache.put(cachVarID, tempStr)


def display_messages(msgs_list):
    def arrange_by_timestamp(msgs_dict_list):
        output_dict_list = []
        for index, msg_dict in enumerate(msgs_dict_list):
            input_ts = msg_dict["timestamp"]
            input_ts = input_ts.strip()
            try:
                input_ts = str(input_ts)
            except Exception as err:
                slib.printLog(f"Could not parse timestamp from message\n{msg_dict}")

            if len(output_dict_list) == 0:
                output_dict_list.append(msg_dict)
            else:
                inserted_current_msg = False
                for index_output, msg_dict_output in enumerate(output_dict_list):
                    output_ts = msg_dict_output["timestamp"]
                    output_ts = str(output_ts)
                    if input_ts <= output_ts:
                        output_dict_list.insert(index_output, msg_dict)
                        inserted_current_msg = True
                        break
                if not inserted_current_msg:
                    output_dict_list.append(msg_dict)
        return output_dict_list

    msgs_list_reversed = arrange_by_timestamp(msgs_list)

    channel_list, unread_list = create_channel_list(msgs_list_reversed)

    selected_sender = select_channel_ui(channel_list, unread_list)

    for index, msg_dict in enumerate(msgs_list):
        sender = msg_dict["sender"]
        message = msg_dict["message text"]
        ts = float(msg_dict["timestamp"])
        group_name = msg_dict["Group name"]
        date_time = datetime.datetime.fromtimestamp(ts/1000.0)

        if sender == selected_sender:
            number = msg_dict["number"]

        if ((sender == selected_sender) or (group_name == selected_sender)) and message is not None:
            print(f"{sender} ({date_time}): \"{message}\"")
            msgs_list[index]["read"] = True
            input("...")
    print("(/r to reply)")
    response = input(">> ")
    if response == "/r":
        compose(msgs_list, channel=sender, number=number)

    return msgs_list





    # for item in msgs_list:
    #     sender = item["sender"]
    #     message = item["message text"]
    #     ts = item["timestamp"]
    #     pts = item["msg processed ts"]
    #     print(f"From {sender}: \"{message}\" ({ts} - {pts})")


def executeTerminalCmd(command):

    cmd_list = command.split(" ")
    try:
        response = subprocess.run(cmd_list)
        response = str(response)
    except:
        response = "-1"

    return response



def write_msgs_history_json(msgsDictList, filepath):
    import json

    slib.write_str_to_file("", filepath, writemode="w") # Clear out the history file

    for dictionary in msgsDictList:

        json_object = json.dumps(dictionary, indent=4)
        json_object+="\n"

        slib.write_str_to_file(json_object, filepath, writemode="a")


def read_signal_msg_history(filepath) -> list:
    # Imports text file containing JSON data, and converts to a list of dictionaries
    import json

    dictList = []
    if slib.file_check_exists(filepath) == False:
        slib.printLog("history file does not exist")
        slib.write_str_to_file("", filepath)
    else:
        slib.printLog(f"Located signal messages history file at {filepath}", console=False)

        rawHistoryList = slib.import_txt_file(filepath)

        jsonStr = ""
        for item in rawHistoryList:
            if item == '{':
                jsonStr = item
            elif item == '}':
                jsonStr+=item
                data = json.loads(jsonStr)
                dictList.append(data)
            else:
                jsonStr+=item

    return dictList


def rcvSigMsg(debug=False):
    # Syntax:
    # signal-cli -a ACCOUNT receive

    global accountNumber
    import chardet


    cmd = f"{cfg.runSigCli} -a {sigAuth} receive"
    cmd_list = cmd.split(" ")


    # input(cmd_list)

    # Initiate the command at the virtual terminal (or whatever it is)
    if debug == False:
        result = subprocess.run(cmd_list, capture_output=True)
        # print(f"result >{result}<")
        bytesStr = result.stdout
        resultStr = bytesStr.decode("utf-8")

        return resultStr
    else:
        return ""


def sendSigMsg(recip_number, msg, debug=False):
    # Syntax:
    # signal-cli -a ACCOUNT send -m "This is a message" RECIPIENT

    global accountNumber
    import subprocess
    sigCliCmd = f"{cfg.runSigCli} -a {accountNumber} send -m {recip_number}"

    cmd_list = []

    sigCliCmdList = sigCliCmd.split(" ")

    for item in sigCliCmdList:
        cmd_list.append(item)
        if item == "-m":
            cmd_list.append(msg)

    # input(cmd_list)

    # Initiate the command at the virtual terminal (or whatever it is)
    if debug == False:
        result = subprocess.run(cmd_list)
        return result
    else:
        return "1"


def verifySignalClientInstall():
    # ToDo

    global sigAuth

    def verifyAccountAuthorization():
        sigCliCmd = f"{cfg.runSigCli} -a {sigAuth} send -m {sigAuth}"
        msg = "test"

        cmd_list = []

        sigCliCmdList = sigCliCmd.split(" ")

        for item in sigCliCmdList:
            cmd_list.append(item)
            if item == "-m":
                cmd_list.append(msg)

        response = subprocess.run(cmd_list)
        response = str(response)

        return response


    tempBool = slib.file_check_exists(cfg.runSigCli)
    if tempBool == False:
        tempMsg = f"Could not locate signal binary at path >>> {cfg.runSigCli} <<<. Signal Service Ended!"
        slib.cache.put(cfg.phoneServerAlerts, tempMsg)
        slib.error_and_exit(tempMsg)
    else:
        slib.printLog("Confirmed signal-cli binaries exist", console=False)

    response = executeTerminalCmd(f"{cfg.runSigCli}")
    if not "returncode=1" in response:
        tempMsg = f"Signal binary exists but cannot be run - Check Java install. Signal Service Ended!"
        slib.cache.put(cfg.phoneServerAlerts, tempMsg)
        slib.error_and_exit(tempMsg)
    else:
        slib.printLog("Confirmed signal-cli binary will execute", console=False)

    response = verifyAccountAuthorization()
    if not "returncode=0" in response:
        tempMsg = f"Signal-cli does not appear to be registered via account number {sigAuth}. Signal Service Ended!"
        slib.cache.put(cfg.phoneServerAlerts, tempMsg)
        slib.error_and_exit(tempMsg)
    else:
        slib.printLog("Confirmed signal-cli appears to be authenticated.", console=False)

    slib.printLog("Successfully confirmed signal-cli installation and setup", console=False)


def extract_msgs_list(raw_message_str):
    def clean_list(input_list):
        output_list = []

        for index, item in enumerate(input_list):
            item = item.strip()


            if item != "":
                output_list.append(item)

        return output_list

    def parse_messages(messages_string):

        def get_sender_info(message_list):

            # Format that need to be handled:

            # Case 1: Envelope from: “Ilya Khait” +18476527804 (device: 1) to +19728370200
            # Case 2: Envelope from: “BravoEcho” 38850d44-2e74-4acd-8782-765503a55e1e (device: 1) to +19728370200
            # Case 3: Envelope from: +12143940797 (device: 2) to +19728370200

            sender_line = message_list[0] # Get the section of the message container sender and recipient info

            tempStr = sender_line.split("(device:")[0].strip()
            # Case 1:
            if ('“' in tempStr) and ('”' in tempStr) and ('+' in tempStr):
                tempStr = tempStr.replace('“', '')  # Remove leading quote
                tempStr = tempStr.replace('”', '')  # Remove trailing quote (yes, they look the same)
                tempStr = tempStr.strip()   # Remove any whitespace
                tempList = tempStr.split(' ')    # split by any spaces

                sender_number = tempList[-1]    # The sender's number will always be the last item in this sub-list

                if len(tempList) == 2:
                    sender_name = tempList[0].strip()
                elif len(tempList) > 2:
                    sender_name = ""
                    for index, item in enumerate(tempList):
                        if index >= (len(tempList) - 1):    # Break before the final item of the list, (the tel number)
                            sender_name = sender_name.strip()
                            break
                        else:
                            sender_name+=item + ' '
                else:
                    sender_name = ""
            # Case 2:
            elif ('“' in tempStr) and ('”' in tempStr) and ('+' not in tempStr):
                sender_number = "Unknown"
                tempStr = tempStr.replace('“', '')  # Remove leading quote
                tempStr = tempStr.replace('”', '')  # Remove trailing quote (yes, they look the same)
                tempStr = tempStr.strip()  # Remove any whitespace
                tempList = tempStr.split(' ')  # split by any spaces

                sender_name = ""
                for index, item in enumerate(tempList):
                    if index >= (len(tempList) - 1):  # Break before the final item of the list, (the unique ID#)
                        sender_name = sender_name.strip()
                        break
                    else:
                        sender_name += item + ' '

            # Case 3:
            elif ('“' not in tempStr) and ('”' not in tempStr) and ('+' in tempStr):
                sender_number = tempStr.strip()  # Remove any whitespace
                sender_name = "Unknown"
            else:
                sender_name = "Unknown"
                sender_number = "Unknown"

            if '(device:' in sender_line:
                temp_list = sender_line.split('(device:')
                tempStr = temp_list[1]
                device_id = tempStr.split(')')[0].strip()

            else:
                device_id = "Unknown"

            # print(sender_line)
            # input(f"sender: {sender_name}, number: {sender_number}, device ID: {device_id}")
            return sender_name, sender_number, device_id

        group_text_flag = False
        msg_types_list = ["Text", "Group Text", "delivery receipt", "read receipt"]

        msg_dict = {
            "message type": None,
            "sender": None,
            "number": None,
            "Device ID": None,
            "timestamp": None,
            "msg timestamp": None,
            "message text": None,
            "Group ID": None,
            "Group name": None,
            "transmitted": False,
            "read": False,
            "msg processed ts": None
        }

        # print(messages_string)
        messages_list = messages_string.split("\n")
        messages_list = clean_list(messages_list)
        messages_list_len = len(messages_list)
        receipt_index = messages_list_len - 4
        # print(messages_list)

        # sender_name, number, device_id = get_sender_info(messages_list)
        msg_dict["sender"], msg_dict["number"], msg_dict["Device ID"] = get_sender_info(messages_list)
        del messages_list[0]

        for item in messages_list:
            item = str(item)

            if (":" in item):  # Don't touch it unless it seems to have a valid header in it
                # print(item)
                filter_list = item.split(":")
                if len(filter_list) > 1:
                    item_name = filter_list[0]

                    if ("Timestamp" in item_name) and (not "Message timestamp" in item_name) and (
                    not "Timestamps" in item_name):
                        temp_list = item.split(": ")
                        temp_list = temp_list[1].split(" ")
                        # input(temp_list)
                        msg_dict["timestamp"] = temp_list[0]
                    if "Message timestamp" in item_name:
                        temp_list = item.split(" ")
                        # print(temp_list)
                        msg_dict["msg timestamp"] = temp_list[2]
                    elif "Body" in item_name:
                        temp_list = item.split(": ")
                        msg_dict["message text"] = temp_list[1]
                    elif "Id" in item_name:
                        temp_list = item.split(": ")
                        msg_dict["Group ID"] = temp_list[1]
                    elif "Name" in item_name:
                        temp_list = item.split(": ")
                        msg_dict["Group name"] = temp_list[1]
                    elif "Group info" in item_name:
                        group_text_flag = True
            # elif

            # print(f"===\n>{item}<")

        # input(f"messages_list[:-3] = {messages_list[receipt_index]}")
        if (group_text_flag == False) and (msg_dict["message text"] != None):
            msg_dict["message type"] = msg_types_list[0]
        elif (msg_dict["Group ID"] != None) and (msg_dict["Group name"] != None) and group_text_flag and (
                msg_dict["message text"] != None):
            msg_dict["message type"] = msg_types_list[1]
        elif "delivery receipt" in messages_list[receipt_index]:
            msg_dict["message type"] = msg_types_list[2]
        elif "read receipt" in messages_list[receipt_index]:
            msg_dict["message type"] = msg_types_list[3]

        t = time.time()
        t_ms = int(t * 1000)
        msg_dict["msg processed ts"] = t_ms     # Insert timestamp in milliseconds for when message was processed

        return msg_dict

    split_message_str = "Envelope from:"

    message_str_list = raw_message_str.split(split_message_str)

    message_str_list = clean_list(message_str_list)

    # single_message = message_str_list[14]
    # msg_dict = parse_messages(single_message)
    # print(single_message)
    # input(msg_dict)

    output_dict_list = []
    for single_message in message_str_list:
        # print(f">{single_message}<")
        msg_dict = parse_messages(single_message)
        if msg_dict["message type"] != None:
            output_dict_list.append(msg_dict)



    return output_dict_list


def downloadMsgsFromSignal(debug=False):
    # ToDo
    # Flag if the signal-cli fails to run properly
    # raw_message_str = slib.readTxtFile("./SignalMessages.txt", outputFormat="str")

    global historical_dict_list
    msgsList = []

    def updateMsgHistoryFile(output_dict_list):
        if len(output_dict_list) > 0:

            # Add new messages to the historical file
            for item in output_dict_list:

                historical_dict_list.append(item)

            write_msgs_history_json(historical_dict_list, history_file)

    def format_sig_mgs_for_phone(dictionaryList):
        msgList = []
        for message in dictionaryList:
            msgType = message['message type']

            if msgType == "Text" or msgType == "Group Text":

                # +19728370200,2022-07-02 16:46:01,0,mms,+19728370200,This is a message
                # channelName,datetime,0,signal,sender,msg_content

                if msgType == "Text":
                    channelName = message['sender']
                    sender = message['sender']
                else:
                    channelName = message['Group name']
                    sender = message['sender']

                msgTimeStamp = int(message['timestamp'])
                msgDateTime = slib.timestampToDatetime(msgTimeStamp / 1000)

                msgBody = message['message text']

                msgStr = f"{channelName},{msgDateTime},0,signal,{sender},{msgBody}"
                msgList.append(msgStr)

                # print(msgStr)
        return msgList

    if debug:
        testFile = "./ExampleSigMsgsRcvd.txt"

        signalMsgsRaw = slib.readTxtFile(testFile, outputFormat="str")
    else:
        print("Checking signal messages...")
        signalMsgsRaw = rcvSigMsg()  # Get latest messages from SigCli
        print("Done checking signal messages.")

    if signalMsgsRaw != "":
        slib.write_str_to_file(signalMsgsRaw, cfg.signalRcvdMsgsDump, writemode="w")
        output_dict_list = extract_msgs_list(signalMsgsRaw)  # Convert Raw Msgs to Usable Message List

        if debug == False:
            updateMsgHistoryFile(output_dict_list)  # Put messages into historical file




        msgsList = format_sig_mgs_for_phone(output_dict_list)

    return msgsList


def queMsgsToPhone(msgs: list):

    if len(msgs) > 0:
        if slib.cache.get(cfg.outbox_que_flag_variable_name) != cfg.outbox_que_flag_pending:
            slib.writeListToFile(cfg.outbox_file, msgs)
            slib.cache.put(cfg.outbox_que_flag_variable_name, cfg.outbox_que_flag_pending)


def getMsgsFromPhoneQue(outboundMsgsQue: list) -> list:

    if slib.cache.get(cfg.inbox_que_flag_variable_name) == cfg.inbox_que_flag_pending:
        outboundMsgsList = slib.import_txt_file(cfg.inbox_file)

        if len(outboundMsgsList) > 0:
            for item in outboundMsgsList:
                outboundMsgsQue.append(item)

        slib.cache.put(cfg.inbox_que_flag_variable_name, cfg.inbox_que_flag_empty)

    return outboundMsgsQue


def uploadMsgsToSignal(outboundMsgsQue: list) -> list:

    # Group message:
    # ./signal-cli -a +19728370200 send -m "Message Here." -g "Ahy1AROCc03cIkRgY5lQGqs6tsVc2qhdoQMa65Zq6EU="

    # Signal message string format:
    # [recipient],[message string]
    if len(outboundMsgsQue) > 0:
        for msgStr in outboundMsgsQue:
            tempList = msgStr.split(",")

            recip_number = tempList[0]

            msgStartIndex = slib.find_nth(msgStr, ',', nth_occurrence=1)

            msg = msgStr[msgStartIndex:]

            sendSigMsg(recip_number, msg, debug=False)

    pass


# ========= Establish Base Variables ============
sigAuth = cfg.signalAccountNumber
history_file = slib.standardize_file_path_format(f"{cfg.dbPath}/{cfg.signalMsgsHistory}")
outboundMsgsQue = []
# ===============================================

# ========= Prepare service Runtime =============
recordPID(cfg.signalServicePIDflag)     # Record the process ID; so the socket server can determine if this is running
historical_dict_list = read_signal_msg_history(history_file)

while False:
    verifySignalClientInstall()

# ===============================================


# ======== Start Main Loop ======================
slib.printLog("Started signalService.py main loop", console=False)
while True:     # Main event loop

    if True:
        msgsList = downloadMsgsFromSignal(debug=False)
        queMsgsToPhone(msgsList)
    if False:
        outboundMsgsQue = getMsgsFromPhoneQue(outboundMsgsQue)
        outboundMsgsQue = uploadMsgsToSignal(outboundMsgsQue)

    time.sleep(1)
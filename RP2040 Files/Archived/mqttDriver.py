import network
import utime
from mqtt_simple import MQTTClient
import config as cfg
import standardLibrary as slib

# Publish test messages e.g. with:
# mosquitto_pub -t foo_topic -m hello

# Example: mqttConn = mqttDriver.mqtt_conn(cfg.mqtt_server_IP, cfg.mqtt_cli_name)
class mqtt_conn:
    
    def __init__(self, serverAddress, clientName, keepalive=30):
        self.serverAddress = serverAddress
        self.clientName = clientName
        self.keepalive = keepalive
        self.broker_conn = self.create_broker_conn()
        self.msg = None
    
    def create_broker_conn(self):
        broker_connection = MQTTClient(self.clientName, self.serverAddress, user=cfg.mqtt_user, password=cfg.mqtt_pass,
                                       keepalive=self.keepalive)	# MUST have the keepalive param
        return broker_connection
    
    def test_connection(self):
        timestamp = str(utime.time())
        self.sendMsg("pico_conn_check", timestamp, success_code=1, error=-1)
        utime.sleep(1)
        response = self.getMsgs("pico_conn_check", retry_qty=4, interval=1, no_msgs_response="-1")
        print(f"Connection Check Reponse: {response}")
        if response == timestamp:
            return True
        else:
            return False
        
    
    def getMsgs(self, sub_topic, retry_qty=4, interval=1, no_msgs_response="No Msgs Received"):
        # Must provide the subscription topic name
        self.broker_conn.set_callback(self.sub_cb)
        try:
            self.broker_conn.connect(clean_session=False)
        except Exception as err:
            input(f"Cannot connect to MQTT Broker! Check the wireless data connection.\n({err})")
        self.broker_conn.subscribe(sub_topic, qos=1)			
        
        self.msg = no_msgs_response
        for i in range(retry_qty):
            self.broker_conn.check_msg()
            if self.msg != no_msgs_response:
                break
            utime.sleep(interval)
        self.broker_conn.disconnect()
        return self.msg
    
    def sendMsg(self, topic, message, success_code=1, error=-1):
        if slib.returnVarType(topic) != "bytes":
            topic = slib.strToBytes(topic)
        if slib.returnVarType(message) != "bytes":
            message = slib.strToBytes(message)
            
        try:
            self.broker_conn.connect(clean_session=False)
            self.broker_conn.publish(topic, message, qos=1)
            self.broker_conn.disconnect()
            return success_code
        except Exception as err:
            print(f"Failed to publish message!\\nn({message})\n\ndue to error:\n\n{err}")
            return error
        
    # Received messages from subscriptions will be delivered to this callback
    def sub_cb(self, topic, msg):
        self.msg = msg
        



    

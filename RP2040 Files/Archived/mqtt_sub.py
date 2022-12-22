import network
import time
from mqtt_simple import MQTTClient

# Publish test messages e.g. with:
# mosquitto_pub -t foo_topic -m hello

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print((topic, msg))


def main(server="192.168.68.106"):
    c = MQTTClient("umqtt_client", server)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(b"foo_topic")
    while True:
        if True:
            # Blocking wait for message
            c.wait_msg()
        else:
            # Non-blocking wait for message
            c.check_msg()
            # Then need to sleep to avoid 100% CPU usage (in a real
            # app other useful actions would be performed instead)
            time.sleep(1)

    c.disconnect()


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("YourMomGoesToCollege","hannahmt")
time.sleep(5)
print(wlan.isconnected())

if __name__ == "__main__":
    main()
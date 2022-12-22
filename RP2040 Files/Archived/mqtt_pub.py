import network
import time
from mqtt_simple import MQTTClient

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("YourMomGoesToCollege","hannahmt")
# time.sleep(5)
print(wlan.isconnected())



# Test reception e.g. with:
# mosquitto_sub -t foo_topic


def main(server="192.168.68.106"):
    c = MQTTClient("umqtt_client", server)
    c.connect()
    c.publish(b"foo_topic", b"New message")
    c.disconnect()


if __name__ == "__main__":
    main()


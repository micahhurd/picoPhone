# Version 0.002
mqtt_server_IP = "192.168.68.108"
mqtt_server_Port = const(1883)		# Not sure if required yet
mqtt_keepalive = const(30)

server_user = "pi-pico"
server_pass = "SomethingHardToGuess"
mqtt_cli_name = "Pi_Pico_Micah"
mqtt_topic_uplink = "from_pico"
mqtt_topic_downlink = "to_pico"
mqtt_confirmation_channel = "confirm_to_pico"
mqtt_sub_interval = const(1)

socket_port = const(1883)
socket_comm_delay = const(0.1)
socket_server_IP = "192.168.68.108"

wifi_ssid = "YourMomGoesToCollege"
wifi_pass = "hannahmt"
debug_bool1 = False		# Level 1 debug boolean
cursor_interval = const(1.25) # times per second
background_task_interval = const(0.5)	# How frequently (seconds) to run the background task (sends and receives msgs, etc.)
alphaNumeric_newline_char = "B"
alphaNumeric_enter_char = "D"
alphaNumeric_backspace_char = "C"
alphaNumeric_select_char = "*"
alphaNumeric_case_select_char = "#"
country_code = "+1"
mms_msg_file = "./mmsHistory.txt"
signal_msg_file = "./signalHistory.txt"
email_msg_file = "./emailHistory.txt"
discord_msg_file = "./discordHistory.txt"
unknown_msg_file = "./unknownMsgsHistory.txt"
temporary_msg_file = "./tempMsgFile.txt"
outbox_file = "./outbox.txt"
contacts_file ="./contacts.txt"
inbox_file = const("./inbox.txt")
contact_list = {
    "+15807437511": ("Hannah", "Hurd"),
    "+19728370200": ("Micah", "Hurd"),
    "+18177713638": ("Clarke", "Hurd"),
    }

multiLine = "Broadly, the organization    argues that the U.S. Department of Education is acting outside of its ---------------- --------------- administrative authority by forgiving student loans. The Department of Education is vested with the power to manage various loan programs but cannot, the applicants contend, forgive loans \"unilateral[ly].\" This power, they say, rests with Congress. This case will continue in the Seventh Circuit, where it is being heard on appeal. A federal district court judge dismissed the lawsuit earlier this month, on ground that the taxpayer group lacked \"standing.\" In short, the challengers, simply as taxpayers, could not show a personal injury as is required to bring a suit. In 2007, the Supreme Court said, \"if every federal taxpayer could sue to challenge any Government expenditure, the federal courts would cease to function as courts of law and would be cast in the role of general complaint bureaus.\" The Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Lorem ipsum dolor sit amet consectetur adipiscing elit. Risus viverra adipiscing at in tellus integer feugiat scelerisque varius. Morbi non arcu risus quis varius quam quisque. Sit amet dictum sit amet justo donec enim diam. Pulvinar proin gravida hendrerit lectus a. Purus in mollis nunc sed id semper risus. Sagittis orci a scelerisque purus semper eget duis at tellus. Consectetur a erat nam at lectus urna duis convallis convallis. Nec dui nunc mattis enim ut. Nulla malesuada pellentesque elit eget. Auctor elit sed vulputate mi sit amet mauris. Cras pulvinar mattis nunc sed blandit libero. Sapien et ligula ullamcorper malesuada. Et malesuada fames ac turpis egestas integer eget aliquet nibh. Varius duis at consectetur lorem donec. Vitae elementum c"
multiLine2 = "Broadly, the organization    argues that the U.S. Department of Education is acting outside of its "
                                                                                
lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Lorem ipsum dolor sit amet consectetur adipiscing elit. Risus viverra adipiscing at in tellus integer feugiat scelerisque varius. Morbi non arcu risus quis varius quam quisque. Sit amet dictum sit amet justo donec enim diam. Pulvinar proin gravida hendrerit lectus a. Purus in mollis nunc sed id semper risus. Sagittis orci a scelerisque purus semper eget duis at tellus. Consectetur a erat nam at lectus urna duis convallis convallis. Nec dui nunc mattis enim ut. Nulla malesuada pellentesque elit eget. Auctor elit sed vulputate mi sit amet mauris. Cras pulvinar mattis nunc sed blandit libero. Sapien et ligula ullamcorper malesuada. Et malesuada fames ac turpis egestas integer eget aliquet nibh. Varius duis at consectetur lorem donec. Vitae elementum curabitur vitae nunc sed. Quis eleifend quam adipiscing vitae proin sagittis nisl. Pulvinar neque laoreet suspendisse interdum consectetur libero id. Pretium vulputate sapien nec sagittis aliquam malesuada bibendum arcu vitae."
quickBrown = "The quick brown fox jumped over the lazy dog. Which was a really lazy dog, cause he was just letting the fox run around do his thang."
font_color = "amber"
background = "background0"
display_sizeX = const(240)
display_sizeY = const(320)
display_rotation = const(0)
backlight_timer = const(30) # Backlight timeout in seconds
device_phone_number = "9728370200"
device_user_first_Name = "Micah"
device_user_last_Name = "Hurd"



fontColors = {
    # https://superuser.com/questions/361297/what-colour-is-the-dark-green-on-old-fashioned-green-screen-computer-displays
    "white": (255,255,255),
    "red": (255,0,0),
    "green": (0,255,0),
    "blue": (0,0,255),
    "yellow": (255,255,0),
    "purple": (230,230,250),
    "thistle": (216,191,216),
    "plum": (221,160,221),
    "orange": (255,165,0),
    "black": (0,0,0),
    "amber": (255, 176, 0),
    "light amber": (255,204,0),
    "green 1": (51,255,0),
    "apple II": (51,255,51),
    "green 2": (0,255,51),
    "apple IIc": (102,255,102),
    "green 3": (0,255,102),
    "background0": (0,0,0),
    "background1": (255,255,255),
    "background2": (40,40,40)
    }

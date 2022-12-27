sigCliPath = "/home/micah/signal-cli/bin/"
dbPath = "./database/"
dbName = "sigCli.db"
channelsHistory = "history.json"

server_filepath = "~/home/micah/PycharmProjects/signalClient/socketServer.py"
server_user = "pi-pico"
server_pass = "SomethingHardToGuess"
outbox_file = "./outbox.txt"
inbox_file = "./inbox.txt"
server_max_hangtime = 60    # The max seconds the server is allowed to interact with client in one session

socket_port = 1883
# ================ Code executes below here =================
import standardLibrary as slib
slib.check_and_create_path(dbPath)
runSigCli = f"{sigCliPath}signal-cli"

mosquittoProcessName = "mosquitto"
mqtt_hostname = "192.168.68.108"
mqtt_port = 1883
mqtt_cli_ID_tx = "Ubuntu Desktop TX"
mqtt_cli_ID_rx = "Ubuntu Desktop RX"
mqtt_topic_from_pico = "from_pico"
mqtt_topic_to_pico = "to_pico"
mqtt_confirmation_channel = "confirm_to_pico"

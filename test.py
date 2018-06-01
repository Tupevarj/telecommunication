from random import randint
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import http.client
import time
from threading import Thread
import socket
import sys
import re
import json
import urllib.request

#######################
#  World boundaries:
#######################

LOWER_LIMIT_X = 0
LOWER_LIMIT_Y = 0
UPPER_LIMIT_X = 2000
UPPER_LIMIT_Y = 1000

#######################
#  Car parameters:
#######################

VELOCITY = 20
CAR_LENGTH = 10
x = 0
y = 0
direction = [0, 0]
pause = False

#######################
#  Client-server:
#######################

http_server = 0
RSU_IP = "130.234.158.68"  # TODO: CHANGE TO IP OF RSU
HOST_NAME = "130.234.158.68"  # TODO: Check IP of car 1
PORT_NUMBER_HTTP = 7777
PORT_NUMBER_CARS = 8888
PORT_RSU = 6666

#######################
#  Socket:
#######################

conn = 0
replied = False

#######################
#  RSU:
#######################

RESOURCE_SIZE_LIMITS = [10 * 1024, 15 * 1024]



####################################################################################
# START:    CAR UPDATE RELATED CODE
####################################################################################


def normalize_vector(vector):
    """ Normalizes the vector """
    magnitude = abs(vector[0]) + abs(vector[1])
    return [vector[0] / magnitude, vector[1] / magnitude]


def pick_direction(up, right):
    """ Picks a random direction based on coarse direction on parameters """
    if up and right:
        # random direction in north-east:
        y = randint(1, 10)
        x = randint(1, 10)
        return normalize_vector((x, y))
    elif up and not right:
        # random direction in north-west:
        y = randint(1, 10)
        x = randint(-10, -1)
        return normalize_vector((x, y))
    elif not up and right:
        # random direction in south-east:
        y = randint(-10, -1)
        x = randint(0, 10)
        return normalize_vector((x, y))
    elif not up and not right:
        # random direction in south-west:
        y = randint(-10, -1)
        x = randint(-10, -1)
        return normalize_vector((x, y))
    #else:
        # assert


def init_start_position():
    """ Initializes car position and direction """
    global x
    global y
    global direction
    up = False
    right = False
    x = randint(LOWER_LIMIT_X + CAR_LENGTH, UPPER_LIMIT_X - CAR_LENGTH)
    y = randint(LOWER_LIMIT_Y + CAR_LENGTH, UPPER_LIMIT_Y - CAR_LENGTH)
    # Determine the direction:
    if y < ((UPPER_LIMIT_X - LOWER_LIMIT_X) / 2):
        # direction should be on right:
        right = True
    if y < ((UPPER_LIMIT_Y - LOWER_LIMIT_Y) / 2):
        # direction should be up:
        up = True
    direction = pick_direction(up, right)


def start_car():
    """ Starts car by initializing its position and direction """
    init_start_position()


def update_car_position(elapsed_time):
    """" Updates car position based on VELOCITY"""
    global x
    global y
    global direction
    global VELOCITY
    x = x + (direction[0] * VELOCITY * elapsed_time)
    y = y + (direction[1] * VELOCITY * elapsed_time)


def update_car_direction():
    """ Updates car direction if needed
         - changes direction of car to direction having most space """
    global x
    global y
    global direction

    update_needed = False

    if (x > (UPPER_LIMIT_X - CAR_LENGTH)) or (x < (LOWER_LIMIT_X + CAR_LENGTH)) or  \
       (y > (UPPER_LIMIT_Y - CAR_LENGTH)) or (y < (LOWER_LIMIT_Y + CAR_LENGTH)):
        update_needed = True

    if not update_needed:
        return

    up = False
    right = False

    # Determine direction
    if (UPPER_LIMIT_X - x) > (LOWER_LIMIT_X + x):
        right = True
    if (UPPER_LIMIT_Y - y) > (LOWER_LIMIT_Y + y):
        up = True

    direction = pick_direction(up, right)


def update_car(elapsed_time):
    """" Main update routine for car. """
    global x
    global y
    global direction
    global pause
    update_car_position(elapsed_time)
    update_car_direction()


def change_car_vm():
    global pause
    send_message_through_socket("START " + str(x) + " " + str(y) + " "
                                + str(direction[0]) + " " + str(direction[1]) + "\n")
    pause = True


def start_changing_car_vm_timer():
    """ Changes from VM to another VM of car """
    threading.Timer(10.0, change_car_vm).start()

####################################################################################
# START:    COMMUNICATION THROUGH SOCKET CODE
####################################################################################


def start_client_socket():
    """" Starts communication with one client """
    global conn
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(('', PORT_NUMBER_CARS))
    except socket.error:
        print("Failed to open socket")
        sys.exit()

    while True:  # Wait for the first client to connect
        s.listen(10)
        conn, address = s.accept()
        print('Connected with ' + address[0] + ':' + str(address[1]))
        break

    thread_socket = Thread(target=client_socket)
    thread_socket.start()


def client_socket():
    """ Communication through socket 
        - Answers with 'OK' message when receives message,
          except when receives 'OK' message"""
    global conn
    global pause
    global x
    global y
    global direction
    global replied
    message = 'Socket server started\n'
    conn.send(message.encode('utf-8'))

    while True:
        data = conn.recv(1024)
        reply = "OK\n"
        if not data:
            break
        if not str(data.decode()) == 'OK\r\n':  # TODO: Check this
            conn.send(reply.encode('utf-8'))
        else:
            replied = True
        split_data = str(data.decode()).split()
        if split_data[0] == 'START':
            x = float(split_data[1])
            y = float(split_data[2])
            direction[0] = float(split_data[3])
            direction[1] = float(split_data[4])
            pause = False
            start_changing_car_vm_timer()
    conn.close()


def send_message_through_socket(message):
    """" Sends message to another client through socket"""
    global conn
    global replied
    # TODO: Check if connection is alive
    while True:
        conn.send(message.encode('utf-8'))
        if replied:
            break
        time.sleep(0.2)
    replied = False


####################################################################################
# START:    HTTP SERVER CODE
####################################################################################

class Server(BaseHTTPRequestHandler):


    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_AUTHHEAD(self):
        print("send header")
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()


    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>FUTURE CAR 2000.6</title></head>", "utf-8"))
        self.wfile.write(bytes("<body><p>You send request to Future Car 2000.6</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

        split_path = re.split('\?|&', self.path)

        # TODO: Add paramters
        try:
            html = split_path[0]
            command = split_path[1]
            params = split_path[2]
            exec(command)
        except IndexError:
            pass


def start_http_server():
    """" Starts HTTP server """
    global http_server
    http_server = HTTPServer((HOST_NAME, PORT_NUMBER_HTTP), Server)
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER_HTTP))
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    http_server.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER_HTTP))


##############################
# Zeeshan FRONT-END
##############################

FRONT_END_PORT = 9999
front_end_server = 0

class ServerFrontEnd(BaseHTTPRequestHandler):


    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.end_headers()
        payload = ("&x="+ str(x) +"&y=" + str(y)).encode('utf-8')
        self.wfile.write(payload)


def start_front_end_http_server():
    """" Starts Front-end HTTP server """
    global front_end_server
    global FRONT_END_PORT
    front_end_server = HTTPServer(('', FRONT_END_PORT), ServerFrontEnd)
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, FRONT_END_PORT))
    try:
        front_end_server.serve_forever()
    except KeyboardInterrupt:
        pass
    front_end_server.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, FRONT_END_PORT))


####################################################################################
# START:    OTHER COMMUNICATION CODE
####################################################################################


def start_sending_data_to_remote_host():
    """ Every seconds sends data to front-end."""
    # TODO: Implement this
    threading.Timer(1.0, start_sending_data_to_remote_host).start()


def start_sending_data_to_rsu():
    """ Every 10 seconds sends data to RSU"""
    # TODO: Implement his
    threading.Timer(10.0, start_sending_data_to_rsu).start()


def send_request_to_rsu(params):
    resource_size = randint(RESOURCE_SIZE_LIMITS[0], RESOURCE_SIZE_LIMITS[1])
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_address = ('', 0)
        s.bind(client_address)
        s.connect((RSU_IP, PORT_RSU))
        message = "GET /" + str(resource_size) + " HTTP/1.1\r\n\r\n"
        s.send(message.encode("utf-8"))
        s.send("{}\r\n".format("Accept-language: en-US,en,q=0.5").encode("utf-8"))
        #exec("while True: s.send('X-a: {}\\r\\n'.format(os.urandom(10))); sleep(10)")
        if params:
            try:
                exec(params)
            except:
                print('Unknown params')
        while True:
            buffer = s.recv(16000)
            if not buffer:
                break
        s.close()
    except Exception as e:
        print(e)


def start_generating_traffic():
    """ Starts generating traffic """
    threading.Timer(5.0, start_generating_traffic).start()
    send_request_to_rsu("")


def send_request_to_car():
    global FRONT_END_PORT
    resource_size = randint(RESOURCE_SIZE_LIMITS[0], RESOURCE_SIZE_LIMITS[1])
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_address = ('', 0)
        s.bind(client_address)
        s.connect(('', FRONT_END_PORT))
        message = "GET /" + str(resource_size) + " HTTP/1.1\r\n\r\n"
        s.send(message.encode("utf-8"))

        while True:
            buffer = s.recv(16000)
            # TODO: PARSE HERE!!!!!!!!!!
            #split_path = re.split('&', str(buffer))
            if not buffer:
                break
        s.close()
    except Exception as e:
        print(e)


########################
# START SERVER:
########################

thread_front_end = Thread(target=start_front_end_http_server)
thread_http = Thread(target=start_http_server)
thread_http.start()
thread_front_end.start()

########################
# CLIENT FOR TESTING:
########################
send_request_to_car()


#http_conn = http.client.HTTPConnection(HOST_NAME + ":" + str(PORT_NUMBER_HTTP))
#http_conn.request("GET", "Car2000.html ")

########################
# OPEN SOCKET:
########################
start_client_socket()

########################
# START CAR:
########################

start_car()
start_sending_data_to_remote_host()
start_sending_data_to_rsu()
start_changing_car_vm_timer()

########################
# CAR UPDATE LOOP:
########################

elapsed_time = 0

# RSU_IP = sys.argv[1]
#start_generating_traffic()
start_generating_traffic()

while True:
    if not pause:
        start_time = time.time()
        update_car(elapsed_time)
        print("X : " + str(x) + " Y : " + str(y) + " DIR : " + str(direction))
        elapsed_time = time.time() - start_time

########################
# CLEANING UP:
########################

#thread_front_end.join()
thread_http.join()
thread_socket.join()
s.close()
http_server.server_close()
front_end_server.server_close()





from random import randint
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

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
        x = randint(1, 2000)
        y = randint(1, 1000)
        payload = ("&x="+ str(x) +"&y=" + str(y)).encode('utf-8')
        self.wfile.write(payload)


def start_front_end_http_server():
    """" Starts Front-end HTTP server """
    global front_end_server
    global FRONT_END_PORT
    front_end_server = HTTPServer(('', FRONT_END_PORT), ServerFrontEnd)
    print(time.asctime(), "Server Starts - %s:%s" % ('', FRONT_END_PORT))
    try:
        front_end_server.serve_forever()
    except KeyboardInterrupt:
        pass
    front_end_server.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % ('', FRONT_END_PORT))


start_front_end_http_server()


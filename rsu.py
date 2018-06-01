
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import os, threading, socket
from queue import Queue
from datetime import datetime


class ThreadPoolMixIn(ThreadingMixIn):
    numThreads = 100
    allow_reuse_address = True

    def serve_forever(self):
        self.requests = Queue(self.numThreads)
        for x in range(self.numThreads):
            t = threading.Thread(target=self.process_request_thread)
            t.setDaemon(1)
            t.start()
        while True:
            self.handle_request()
        self.server_close()

    def process_request_thread(self):
        while True:
            ThreadingMixIn.process_request_thread(self, *self.requests.get())

    def handle_request(self):
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            self.requests.put((request, client_address))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            size = int((self.path.decode()).split('/')[1])
            self.send_response(200)
            self.end_headers()
            payload = os.urandom(size)
            self.wfile.write(payload)
            with open('rsu.log', 'a') as f:
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' GET ' + self.path + '\n')
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            self._set_headers()
            with open('rsu.log', 'a') as f:
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' POST ' + self.path + '\n')
        except:
            pass


class ThreadedHTTPServer(ThreadPoolMixIn, HTTPServer):
    pass


if __name__ == '__main__':
    server = ThreadedHTTPServer(('', 6666), Handler)
    print('Starting Road Site Unit, use <Ctrl-C> to stop')
    server.serve_forever()
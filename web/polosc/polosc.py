# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

#import CGIHTTPServer
import BaseHTTPServer
import logging
import csv
import sys
import OSC as osc
import threading
import json
import random

LOG_FILENAME = '/tmp/polosc.out'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)
logging.info("")
logging.info("***STARTING***")

# Webserver-OSC->alj
NET_SEND_ADDR=('127.0.0.1', 57140)
# alj->Webserver-OSC:
NET_ADDR=('127.0.0.1', 57141)

players = dict()

class PoloHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    def write_response(self):
        if self.server.mappings.has_key(self.path):
            logging.debug("path '%s' is mapped"%(self.path))
            self.send_response(200)
            self.send_header("Content-type", self.mimeTypeForPath(self.path))
            self.end_headers()
            self.wfile.write(self.server.mappings[self.path])
        elif self.path == "/getrandom":
            logging.debug("got request for a random number")
            random_int = random.randint(0, 0xFFFFFFFF)
            logging.debug("sending %x"%(random_int))
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("%x"%(random_int))
        elif self.path[:3] == "/id":
            logging.debug("got request with id %s"%(self.path[3:]))
            print players
            if self.path[3:] in players:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    self.server.mappings["/start.html"]%(
                        ['maroon', 'red','green', 'lime', 'olive', 
                         'yellow', 'navy', 'blue', 'purple', 'fuchsia'
                         ][players[self.path[3:]]]))
                for i in range(8):
                    self.wfile.write(
                        self.server.mappings["/field.html"]%(
                            str(i), str(i), str(i), str(i), str(i), 
                            str(i), str(i), str(i), str(i), str(i)))
                self.wfile.write(self.server.mappings["/end.html"])
            else:
                self.wfile.write("<html><body><h1>Error</h1>: all seats taken, %s</body></html>"%(self.path[3:]))
            #self.wfile.write(self.server.mappings["/index.html"])
            #self.wfile.write("%x"%(random_int))
        else:
            logging.debug("path '%s' is not mapped"%(self.path))
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><body><h1>404 Error</h1>invalid path: '%s'</body></html>"%(self.path))

    def mimeTypeForPath(self, path):
        suffix = path.split(".")[-1].lower()
        
        mimeTypes = {
            "png": "image/png",
            "html": "text/html",
            "js": "application/javascript"
        }
        
        return mimeTypes.get(suffix, "text/html")
    
    def send_notifications(self, osc_address, osc_data):
        if self.server.notifications.has_key(self.path):
            for n in self.server.notifications[self.path]:
                logging.debug("sending notification to '%s:%s%s'"%(n.host, n.port, osc_address))
                if (type(osc_address) == str and type(osc_data) == list):
                        msg = osc.OSCMessage()
                        msg.setAddress(osc_address)
                        for i in osc_data:
                            msg.append(i)
                            client.sendto(msg, (n.host, n.port)) 
                else:
                    logging.error("did not send message. string address and list message expected, got %s %s."%(type(osc_address), type(osc_data)))
        else:
            logging.debug("no notification for '%s'"%(self.path))
            
    def do_HEAD(self):
        if self.server.mappings.has_key(self.path):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()

    def do_GET(self):
        """Respond to a GET request."""
        logging.info("GET for '%s'"%(self.path))
        self.write_response()
        # data = None
        # self.send_notifications(data)

    def do_POST(self):
        """Respond to a POST request."""
        logging.info("POST for '%s'"%(self.path))
        self.write_response()
        length = int(self.headers.getheader('content-length'))
        message_str = self.rfile.read(length)
        logging.debug("got incoming data '%s'"%(message_str))
        message = {}
        try:
            message = json.loads(message_str)
            try:
                if (message.has_key(u"address") and message.has_key(u"data")):
                    logging.debug("sending data '%s' '%s'"%(message["address"], message["data"]))
                    if message.has_key("types"):
                        try:
                            convertMap = {"s":str, "i":int, "f":float}
                            message["data"] = [convertMap[t](d) for t, d in zip(message["types"], message["data"])]
                        except Exception, e:
                            logging.error("could not convert the data to the specified types '%s'"%(message["types"]))
                            logging.error("exception: %s"%(e))
                    self.send_notifications(str(message["address"]), message["data"])
                else:
                    logging.error("message was missing address and/or data")
            except Exception, e:
                logging.error("error sending message")
                logging.error("exception: %s"%(e))
        except Exception, e:
            logging.error("Could not parse incoming data '%s'"%(message_str))
            logging.error("%s"%(e))

class PoloServer (BaseHTTPServer.HTTPServer):
    def __init__(self, server_address, handler_class, mappings = None, notifications = None):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, handler_class)
        if mappings:
            self.mappings = mappings
        else:
            self.mappings = Mappings()
        if notifications:
            self.notifications = notifications
        else:
            self.notifications = Notifications()

def run(server_class = PoloServer,
        handler_class = PoloHandler,
        server_port = 8000,
        mappings = None,
        notifications = None):
    """Create a server instance and run it"""
    server_address = ('', server_port)
    httpd = server_class(server_address, handler_class, mappings, notifications)
    try:
        httpd.serve_forever()
    except:
        print "\nClosing OSCServer."
        oscServer.close()
        print "Waiting for Server-thread to finish"
        oscServerThread.join()
        httpd.server_close()

def get_filenames(arg_list, extension):
    """return a list of the strings in the input list that have the given extension"""
    return filter(lambda x: x.endswith(extension), arg_list)
    
class Mappings (dict):
    """a string-keyed dictionary of mappings between paths and actual files"""
    def read_mappings_file(self, mapping_filename):
        """read mappings from a file"""
        mapping_file = None
        try:
            logging.info("reading mapping file '%s'"%(mapping_filename))
            mapping_file = open(mapping_filename)
            reader = csv.reader(mapping_file)
            for row in reader:
                logging.info("'%s' maps to '%s'"%(row[0], row[1]))
                mapped_file = None
                try:
                    mapped_file = open(row[1])
                    self[row[0]] = mapped_file.read()
                except Exception, e:
                    logging.error("Could not read mapped file '%s'."%(row[1]))
                    logging.error("%s"%(e))
                if mapped_file:
                    mapped_file.close()
        except Exception, e:
            logging.error("Could not read mapping file '%s'."%(mapping_filename))
            logging.error("%s"%(e))
        if mapping_file:
            mapping_file.close()

    def read_mappings(self, mapping_filenames):
        """read mappings from a list of files"""
        for fn in mapping_filenames:
            self.read_mappings_file(fn)

class Notifications (dict):
    def add_notification_data(self, path, host, port):
        self.add_notification(path, Notification(host, port))
        
    def add_notification(self, path, notification):
        if not self.has_key(path):
            logging.debug("adding new notification path '%s'"%(path))
            self[path] = []
        logging.debug("adding notification '%s:%s' to path '%s'"%(notification.host, notification.port, path))
        self[path].append(notification)

    def read_notifications_file(self, notifications_filename):
        """read notifications from a file"""
        logging.debug("starting to read notifications file '%s'"%(notifications_filename))
        notifications_file = None
        try:
            logging.info("reading notifications file '%s'"%(notifications_filename))
            notifications_file = open(notifications_filename)
            reader = csv.reader(notifications_file)
            logging.info("parsed notifications file '%s'"%(notifications_filename))
            for row in reader:
                path = row[0]
                host = row[1]
                port = int(row[2])
                logging.info("'%s' notifies '%s:%s'"%(path, host, port))
                self.add_notification_data(path, host, port)
        except Exception, e:
            logging.error("Could not read notifications file '%s'."%(notifications_filename))
            logging.error("%s"%(e))
        if notifications_file:
            notifications_file.close()

    def read_notifications(self, notifications_filenames):
        """read notifications from a list of files"""
        for fn in notifications_filenames:
            self.read_notifications_file(fn)

class Notification (object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

def update_dict(*msg):
    print "got message ", msg
    if msg[2][1] != -1:
        players[msg[2][0]] = msg[2][1]
    else:
        logging.debug("got max players message")

if "__main__" == __name__:
    mapping_extension = ".map"
    notification_extension = ".not"

    mapping_filenames = get_filenames(sys.argv, mapping_extension)
    mappings = Mappings()
    mappings.read_mappings(mapping_filenames)

    notification_filenames = get_filenames(sys.argv, notification_extension)
    notifications = Notifications()
    notifications.read_notifications(notification_filenames)

    ## start communication and send specs
    client = osc.OSCClient()

    oscServer = osc.OSCServer(NET_ADDR)
    oscServer.addDefaultHandlers()

    oscServer.addMsgHandler("/alj/dict", update_dict)
    # Start OSCServer
    print "\nStarting OSCServer. Use ctrl-C to quit."
    oscServerThread = threading.Thread( target = oscServer.serve_forever )
    oscServerThread.start()

    port = 8000
    if (sys.argv[1] not in mapping_filenames) and (sys.argv[1] not in notification_filenames):
        port = int(sys.argv[1])

    logging.info("HTTP port: %d"%(port))

    run(mappings = mappings, notifications = notifications, server_port = port)

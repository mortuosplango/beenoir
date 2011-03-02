import BaseHTTPServer
from htmlpage import *

class BeenoirServer (BaseHTTPServer.HTTPServer):

    def __init__(self, server_address, handler_class, actors):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, handler_class)
        self.actors = actors

    
def run(actors, port=8000):
    server_address = ('', port)
    httpd = BeenoirServer(server_address, BeenoirHandler, actors)
    try:
        httpd.serve_forever()
    except:
        print "Waiting for Server-thread to finish"
        httpd.server_close()

class BeenoirHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(self):
        for actor in self.server.actors:
            if actor.is_responsible(self):
                success = actor.try_handle(self)
                if success:
                    self.send_response_head(200)
                    break                 
        else:
            self.send_response_head(404)
        
    def send_response_head(self, response=200, mime_type="text/html"):
        self.send_response(response)
        self.send_header("Content-type", mime_type)
        self.end_headers()
    
    def send_response_content(self, content):
        self.wfile.write(content)
    
    def do_GET(self):
        self.dispatch_to_actor("GET")
    
    def do_POST(self):
        self.dispatch_to_actor("POST")
    
    def dispatch_to_actor(self, request):
        for actor in self.server.actors:
            if actor.request == request:
                if actor.is_responsible(self):
                    actor.handle(self)
                    break
        else:        
            self.send_response_head(404)
            self.send_response_content(HTTP404ErrorHTMLPage(self.path))
            
    def mimeTypeForPath(self, path):
        suffix = path.split(".")[-1].lower()
            
        mimeTypes = {
            "png": "image/png",
            "gif": "image/gif",
            "html": "text/html",
            "js": "application/javascript",
            "css": "text/css"
        }
            
        return mimeTypes.get(suffix, "text/html")
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
        
    def send_response_header(self, response=200, mime_type="text/html"):
        self.send_response(response)
        self.send_header("Content-type", mime_type)
        self.end_headers()
    
    def send_response_content(self, content):
        self.wfile.write(content)
        
    def send_page(self, content, response=200, mime_type="text/html"):
        self.send_response_header(response, mime_type)
        self.send_response_content(content)
    
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
            self.send_page(HTTP404ErrorHTMLPage(self.path), 404)
            
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

class BaseActor:
    def __init__(self, request):
        self.request = request
    
    def is_responsible(self, handler):
        return False
    
    def try_handle(self, handler):
        # in normal cases an Actor can handle any request he's responsible for
        return True
    
    def handle(self, handler):
        handler.send_page("Generic Handler. Please overwrite handle function", 200)
    

class Actor(BaseActor):
    def __init__(self, request, responsible_func, handle_func):
        BaseActor.__init__(self, request)
        self.is_responsible_func = responsible_func
        self.handle_func = handle_func
    
    def is_responsible(self, handler):
        return self.is_responsible_func(self, handler)
     
    def handle(self, handler):
        self.handle_func(self, handler)
        
class PathActor(Actor):
    def __init__(self, request, path, handle_func):
        Actor.__init__(self, request, lambda s, h: h.path == path, handle_func)

class StringActor(Actor):
    def __init__(self, request, responsible_func, string):
        Actor.__init__(self, request, responsible_func, None)
        self.string = string
    
    def handle(self, handler):
        handler.send_page(self.string)

class StringFuncActor(Actor):
    def __init__(self, request, responsible_func, string_func):
        Actor.__init__(self, request, responsible_func, 
                       lambda s, h: h.send_page(string_func(s,h)))
 
class StringFuncPathActor(Actor):
    def __init__(self, request, path, string_func):
        Actor.__init__(self, request,
                       lambda s, h: h.path == path, 
                       lambda s, h: h.send_page(string_func(s,h)))

class StringPathActor(StringActor):
    def __init__(self, request, path, string):
        StringActor.__init__(self, request,
                       lambda s, h: h.path == path, string)

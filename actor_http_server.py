import BaseHTTPServer
from htmlpage import *
import os
from threading import Thread
import json


class ActorHTTPServer (BaseHTTPServer.HTTPServer):
    def __init__(self, server_address, handler_class, actors):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, handler_class)
        self.actors = actors

def run(actors, port=8000):
    server_address = ('', port)
    httpd = ActorHTTPServer(server_address, ActorHandler, actors)
    try:
        httpd.serve_forever()
    except:
        print "Waiting for Server-thread to finish"
        httpd.server_close()

class ActorHTTPServerThread(Thread):
    def __init__(self, actors, port=8000):
        Thread.__init__(self)
        self.actors = actors
        self.port = port
        self.running = True

    def run(self):
        server_address = ('', self.port)
        httpd = ActorHTTPServer(server_address, ActorHandler, self.actors)
        while self.running:
            httpd.handle_request()
    
    def close(self):
        self.running = False
        
    

class ActorHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(self):
        for actor in self.server.actors:
            if actor.is_responsible(self):
                success = actor.try_handle(self)
                if success:
                    self.send_response_header(200)
                    break                 
        else:
            self.send_response_head(404)
        
    def send_response_header(self, response=200, mime_type="text/html"):
        self.send_response(response)
        self.send_header("Content-Type", mime_type)
        self.end_headers()
    
    def send_response_content(self, content):
        self.wfile.write(content)
        
    def send_page(self, content, response=200, mime_type="text/html"):
        self.send_response_header(response, mime_type)
        self.send_response_content(content)
    
    def send_redirect(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()
    
    def do_GET(self):
        self.dispatch_to_actor("GET")
    
    def do_POST(self):
        self.dispatch_to_actor("POST")
    
    def path_base(self):
        return self.path.partition('?')[0]
    
    def get_arguments(self):
        arg_string = self.path.partition('?')[2]
        dict = {}
        arg_pairs = arg_string.split('&')
        for pair in arg_pairs:
            x = pair.split('=')
            dict[x[0]] = x[1]
        return dict
    
    def dispatch_to_actor(self, request):
        for actor in self.server.actors:
            if actor.request == request:
                if actor.is_responsible(self):
                    actor.handle(self)
                    break
        else:        
            self.send_page(HTTP404ErrorHTMLPage(self.path), 404)

    def get_post_json_dict(self):
        msg_len = int(self.headers.getheader('Content-Length'))
        msg = self.rfile.read(msg_len)
        try:
            return json.loads(msg)
        except Exception, e:
            return {}

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
    
# naming conventions for lambda functions: a = actor, h = handler

class Actor(BaseActor):
    def __init__(self, request, responsible_func=None, handle_func=None):
        BaseActor.__init__(self, request)
        self.is_responsible_func = responsible_func
        self.handle_func = handle_func
    
    def is_responsible(self, handler):
        return self.is_responsible_func(self, handler)
     
    def handle(self, handler):
        self.handle_func(self, handler)

# these are some generic Actors. Don't know if they will be used.
        
class PathActor(Actor):
    def __init__(self, request, path, handle_func):
        Actor.__init__(self, request, 
                       lambda a, h: h.path_base() == path,
                       handle_func)

class StringActor(Actor):
    def __init__(self, request, responsible_func, string):
        Actor.__init__(self, request, responsible_func)
        self.string = string
    
    def handle(self, handler):
        handler.send_page(self.string)

class StringFuncActor(Actor):
    def __init__(self, request, responsible_func, string_func):
        Actor.__init__(self, request, responsible_func, 
                       lambda a, h: h.send_page(string_func(a, h)))
 
class StringFuncPathActor(Actor):
    def __init__(self, request, path, string_func):
        Actor.__init__(self, request,
                       lambda a, h: h.path_base()  == path, 
                       lambda a, h: h.send_page(string_func(a, h)))

class StringPathActor(StringActor):
    def __init__(self, request, path, string):
        StringActor.__init__(self, request,
                       lambda a, h: h.path_base() == path, string)




class StaticFilesActor(BaseActor):
    def __init__(self, map, path):
        BaseActor.__init__(self, "GET")
        self.path = path
        self.map = map
    
    def is_responsible(self, handler):
        return handler.path.startswith(self.map)
        
    def file_path(self, full_path):
        return self.path + full_path[len(self.map):]
    
    def try_handle(self, handler):
        return os.path.exists(self.file_path(handler.path))
    
    def path_is_secure(self, path):
        # IMPLEMENT!!
        return True
    
    def handle(self, handler):
        file_path = self.file_path(handler.path)
        if not os.path.exists(file_path):
            handler.send_page(HTTP404ErrorHTMLPage(handler.path), 404)
        elif not self.path_is_secure(file_path):
            handler.send_page(ShortErrorHTMLPage("Invalid Request!"))
        else:
            with open(file_path, "rb") as fp:
                handler.send_page(fp.read(), 200,
                                  self.mime_type_for_path(file_path))
        
    def mime_type_for_path(self, path):
        suffix = path.split(".")[-1].lower()
            
        types = {
            "png": "image/png",
            "gif": "image/gif",
            "html": "text/html",
            "js": "application/javascript",
            "css": "text/css"
        }
            
        return types.get(suffix, "text/html")
        
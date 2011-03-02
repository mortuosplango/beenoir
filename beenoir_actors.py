from actor_http_server import *
from htmlpage import *

class BeenoirStartActor(PathActor):
    def __init__(self, path, world):
        PathActor.__init__(self, "GET", path, None)
        self.world = world
    
    def handle(self, handler):
        controller_id = self.world.register_and_create_web_player()
        print controller_id
        if controller_id:
            handler.send_redirect("/game?id=" + str(controller_id))
        else:
            handler.send_page(ShortErrorHTMLPage("Keine freien Spieler verf&uuml;gbar!"))

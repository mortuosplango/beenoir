from actor_http_server import *
from htmlpage import *
from common import colors

class BeenoirBaseActor(PathActor):
    def __init__(self, path, world):
        PathActor.__init__(self, "GET", path, None)
        self.world = world
    
    def controller_id(self, handler):
        pass
        # TODO: controller ID aus Argument

class BeenoirStartActor(BeenoirBaseActor):
    def handle(self, handler):
        controller_id = self.world.register_and_create_web_player()
        if controller_id:
            handler.send_redirect("/game?id=" + str(controller_id))
        else:
            handler.send_page(ShortErrorHTMLPage("Keine freien Spieler verf&uuml;gbar!"))

class BeenoirGameActor(BeenoirBaseActor):
    def handle(self, handler):
        
        player_id = world.controllers(self.controller_id)
        
        if player_id:
            page = HTMLPage("Beenoir")
            page.head = page.template_string("game_head")%{
                "player_color": colors[player_id]
            }
            page.content = page.template_string("game")%{
                
            }
            handler.send_page(page)
        else:
            handler.send_page(ShortErrorHTMLPage("Spieler nicht mehr verf&uumlgbar!"))
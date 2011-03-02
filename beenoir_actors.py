from actor_http_server import *
from htmlpage import *
from common import *
import beenoir
import time

class BeenoirBaseActor(PathActor):
    def __init__(self, path, world):
        PathActor.__init__(self, "GET", path, None)
        self.world = world
    
    def controller_id(self, handler):
        return handler.get_arguments().get("id")
    
    def player_id(self, handler):
        return self.world.controllers.get(self.controller_id(handler))

class BeenoirStartActor(BeenoirBaseActor):
    def handle(self, handler):
        controller_id = self.world.register_and_create_web_player()
        if controller_id:
            # handler.send_redirect("/game?id=" + str(controller_id))
            # TODO: Lazy Redirect ...
        else:
            handler.send_page(ShortErrorHTMLPage("Keine freien Spieler verf&uuml;gbar!"))

class BeenoirGameActor(BeenoirBaseActor):
    def handle(self, handler):
        
        player_id = self.player_id(handler)
        
        if player_id:
            controller_id = self.controller_id(handler)
            player_code = self.world.players[player_id].code
            
            # stupid implementation
            code_array = "[" + str(player_code[0])
            for code in player_code[1:]:
                code_array += ", "
                code_array += code
            code_array += "]"
            
            code_table = "<table><tr>"
            for i in range(CODESIZE):
                code_table += "<td>"
                code_table += "<div class='topSpaceDummy'> </div>"
                code_table += "<img src='/static/opcodes_%s.png' width='48' height='48' border='0' alt='Code' class='not'><br />"%(player_code[i])
                code_table += "<div class='bottomSpaceDummy'> </div>"
                
                for e in range(NUMCODES):
                    inactive = ""
                    if player_code[i] != e:
                        inactive = "1"
                    code_table += "<img src='/static/opcodes_%s%s.png' onClick='sendNewCode(ID, %s, %s)' width='48' height='48' alt='%s' id='%s_%s' />\n"%(inactive, e, i, e, opcode_alts[e], i, e)
                    if e < (NUMCODES - 1):
                        code_table += "<br />"
    
                code_table += "</td>"
            
            code_table += "</tr></table>"
        
            page = HTMLPage("Beenoir")
            page.head = page.template_string("game_head")%{
                "player_color": colors[player_id]
            }
            page.content = page.template_string("game")%{
                "controller_id": controller_id,
                "player_id": player_id,
                "code_array": code_array,
                "code_table": code_table
            }
            handler.send_page(page)
        else:
            handler.send_page(ShortErrorHTMLPage("Spieler nicht mehr verf&uuml;gbar!"))
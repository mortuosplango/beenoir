from actor_http_server import *
from htmlpage import *
from common import *
import beenoir
import time

class BeenoirBaseActor(PathActor):
    def __init__(self, path, world, request="GET"):
        PathActor.__init__(self, request, path, None)
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
            page = HTMLPage("Einen Moment Bitte &hellip;")
            page.head = page.template_string("wait_head")%{
                "url": "/game?id=" + str(controller_id)
            }
            page.content = page.template_string("wait")
            
            handler.send_page(page)
            
        else:
            handler.send_page(ShortErrorHTMLPage("Keine freien Spieler verf&uuml;gbar!"))

class BeenoirPingActor(BeenoirBaseActor):
    def __init__(self, path, world):
        BeenoirBaseActor.__init__(self, path, world, "POST")
    
    def handle(self, handler):
        controller_id = self.controller_id(handler)
        player_id = self.player_id(handler)
        if player_id:
            self.world.ping_player(controller_id)
            handler.send_page("ok")
        else:
            handler.send_page("fail")

class BeenoirCodeActor(BeenoirBaseActor):
    def __init__(self, path, world):
        BeenoirBaseActor.__init__(self, path, world, "POST")
    
    def handle(self, handler):
        controller_id = self.controller_id(handler)
        player_id = self.player_id(handler)
        if player_id:
            dict = handler.get_json_dict()
            self.world.update_code(controller_id, 
                                   dict.get("code", [0] * 8))
            handler.send_page("ok")
        else:
            handler.send_page("fail")


class BeenoirGameActor(BeenoirBaseActor):
    def handle(self, handler):
        
        player_id = self.player_id(handler)
        
        # this is quite ugly. player creation is delayed, so
        # if this page is accessed too early we have a problem.
        # we bypass this with a lazy redirect.
        
        if player_id and self.world.players[player_id]:
            controller_id = self.controller_id(handler)
            player_code = self.world.players[player_id].code
            
            # stupid implementation
            code_array = "[" + str(player_code[0])
            for code in player_code[1:]:
                code_array += ", "
                code_array += str(code)
            code_array += "]"
            
            code_table = "<table style=\"clear: both;\"><tr>"
            for i in range(CODESIZE):
                code_table += "<td>"
                code_table += "<div class='topSpaceDummy'> </div>"
                code_table += "<img src='/static/opcodes_%s.png' width='48' height='48' border='0' alt='Code' class='not' id='%s_x'><br />\n"%(player_code[i], i)
                code_table += "<div class='bottomSpaceDummy'> </div>"
                
                for e in range(NUMCODES):
                    inactive = ""
                    if player_code[i] != e:
                        inactive = "1"
                    code_table += "<img src='/static/opcodes_%s%s.png' onClick='changeCode(%s, %s)' width='48' height='48' alt='%s' id='%s_%s' />\n"%(inactive, e, i, e, opcode_alts[e], i, e)
                    if e < (NUMCODES - 1):
                        code_table += "<br />"
                code_table += "</td>"
            code_table += "</tr></table>"
        
            page = HTMLPage("Beenoir")
            page.head = page.template_string("game_head")%{
                "player_color": colors[player_id],
                "controller_id": controller_id,
                "player_id": player_id,
                "code_array": code_array
            }
            page.content = page.template_string("game")%{
                "code_table": code_table,
                "player_id": player_id
            }
            handler.send_page(page)
        else:
            handler.send_page(ShortErrorHTMLPage("Spieler nicht mehr verf&uuml;gbar!"))
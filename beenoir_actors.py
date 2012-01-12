from actor_http_server import *
from htmlpage import *
from common import *
import beenoir
import time

class PlayerFailHTMLPage(ShortErrorHTMLPage):
    def __init__(self):
        ShortErrorHTMLPage.__init__(self, 
            I18N["player_lost"], 
            I18N["sorry!"]
        )


class BeenoirBaseActor(PathActor):
    def __init__(self, path, world, request="GET"):
        PathActor.__init__(self, request, path, None)
        self.world = world
        
    def get_controller_id(self, handler):
        return handler.get_arguments().get("id")
    
    def get_player_id(self, handler):
        return self.world.controllers.get(self.get_controller_id(handler))

class BeenoirPlayerActor(BeenoirBaseActor):
    def __init__(self, path, world):
        BeenoirBaseActor.__init__(self, path, world, "POST")
        
    def handle(self, handler):
        # get values from handler and world
        self.controller_id = self.get_controller_id(handler)
        self.player_id = self.get_player_id(handler)
        
        # these can be overwritten by handle_action
        self.success_response = "ok"
        self.fail_response = "fail"
        
        if self.player_id != None and self.world.players[self.player_id]:
            self.handle_success(handler)
            handler.send_page(self.success_response)
        else:
            self.handle_fail(handler)
            handler.send_page(self.fail_response)
            
    def handle_success(self, handler):
        pass
    
    def handle_fail(self, handler):
        pass

# Start of more concrete actors

class BeenoirStartActor(BeenoirBaseActor):
    def handle(self, handler):
        controller_id, player_id = self.world.register_and_create_web_player()
        if controller_id:
            # handler.send_redirect("/game?id=" + str(controller_id))
            page = HTMLPage(I18N["just_a_moment"])
            page.head = page.template_string("wait_head")%{
                "url": "/game?id=" + str(controller_id)
            }
            page.content = page.template_string("wait")%{
                "color": COLORS[player_id],
                "player_id": player_id,
                "i18n_player": I18N["player"],
                "i18n_just_a_moment": I18N["just_a_moment"]
            }
            handler.send_page(page)
        else:
            handler.send_page(ShortErrorHTMLPage(I18N["no_free_players"], I18N["sorry!"]))


class BeenoirPingActor(BeenoirPlayerActor):
    def handle_success(self, handler):
        self.world.ping_player(self.controller_id)


class BeenoirCodeActor(BeenoirPlayerActor):
    def handle_success(self, handler):
        dict = handler.get_post_json_dict()
        self.world.update_code(self.controller_id, 
                               dict.get("code", [0] * 8))


class BeenoirTempoActor(BeenoirPlayerActor):
    def handle_success(self, handler):
        dict = handler.get_post_json_dict()
        player = self.world.players[self.player_id]
        player.change_tempo(dict.get("tempo", 0))

class BeenoirVisualHintActor(BeenoirPlayerActor):
    def handle_success(self, handler):
        self.world.push_visual_hint(self.player_id)

class BeenoirGameActor(BeenoirBaseActor):
    def handle(self, handler):
        
        player_id = self.get_player_id(handler)
        
        # this is quite ugly. player creation is delayed, so
        # if this page is accessed too early we have a problem.
        # we bypass this with a lazy redirect.
        
        if player_id != None and self.world.players[player_id]:
            controller_id = self.get_controller_id(handler)
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
                    code_table += "<img src='/static/opcodes_%s%s.png' onClick='changeCode(%s, %s)' width='48' height='48' alt='%s' id='%s_%s' />\n"%(inactive, e, i, e, OPCODE_ALTS[e], i, e)
                    if e < (NUMCODES - 1):
                        code_table += "<br />"
                code_table += "</td>"
            code_table += "</tr></table>"
            
            help_table = "<table style=\"clear: both;\">"
            for i in range(NUMCODES):
                help_table += "<tr><td class=\"code\"><img src='static/opcodes_%s.png' width='32' height='32' class=\"not\" \></td><td class=\"text\">%s</td></tr>"%(
                    i,
                    OPCODE_HELP[i]
                )
            help_table += "</table>"
            
            tempo_control = "<div id='tempoControl'>%s: \n"%(I18N["tempo"])
            for i in range(NUMTEMPOS):
                tempo_class = "button tempo off"
                if self.world.players[player_id].tempo == i:
                    tempo_class = "button tempo on"
                if i == 0: tempo_class += " first"
                if i == NUMTEMPOS - 1 : tempo_class += " last"
                tempo_control += "<a href='#' class='%s' id='%s' onclick='changeTempo(%s)'>%s</a>\n"%(
                    tempo_class,"tempo_" + str(i),i, "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                 )
            tempo_control += "</div>"
            
            page = HTMLPage("Bee Noir")
            page.head = page.template_string("game_head")%{
                "player_color": COLORS[player_id],
                "controller_id": controller_id,
                "player_id": player_id,
                "code_array": code_array,
                "codesize": CODESIZE,
                "numcodes": NUMCODES,
                "numtempos": NUMTEMPOS
            }
            page.content = page.template_string("game")%{
                "code_table": code_table,
                "tempo_control": tempo_control,
                "player_id": player_id,
                "i18n_player": I18N["player"],
                "i18n_back_to_start": I18N["back_to_start"],
                "i18n_lost_connection": I18N["lost_connection"],
                "i18n_reset_button": I18N["reset_button"],
                "i18n_clear_button": I18N["clear_button"],
                "i18n_help_button": I18N["help_button"],
                
                "i18n_help": I18N["help"],
                "i18n_help_descr": I18N["help_descr"],
                "i18n_back_to_game": I18N["back_to_game"],
                "i18n_back_to_help": I18N["back_to_help"],
                "help_table": help_table,
                
                "i18n_about": I18N["about"],
                "i18n_about_text": I18N["about_text"]
                
            }
            handler.send_page(page)
        else:
            handler.send_page(PlayerFailHTMLPage())
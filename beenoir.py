import random
import math
import threading
import sys

import OSC as osc

import pyglet.window
import pyglet.clock
from pyglet.window import key

WIN_WIDTH = 1200
WIN_HEIGHT = 800

WORLD_WIDTH = 16
WORLD_HEIGHT = 12

PLAYERS = 10

# (verbose) debugging output
DEBUG = True
VERBOSE = False

FPS = 24.0

# Webserver-OSC->alj
NET_ADDR = ('127.0.0.1', 57140)
# alj->Webserver-OSC:
NET_SEND_ADDR = ('127.0.0.1', 57141)

# alj-OSC->SuperCollider
SC_ADDR = ('127.0.0.1', 57120)

batch = pyglet.graphics.Batch()
background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)
players = pyglet.graphics.OrderedGroup(2)

colors = [ 'ffffff', 'ff0000', 'ff00ff', '0000ff', '00ffff',
           '00ff00', 'ffff00', '7f0000', '7f007f', '00007f',
           '007f7f', '007f00,' '827f00']


class vec3(object):
    """
    """
    
    def __init__(self, x=0, y=0, z=0):
        """
        """
        self.x = x
        self.y = y
        self.z = z

    def add(self, other): 
        return vec3(
            self.x + other.x,
            self.y + other.y, 
            self.z + other.z)

    def sub(self, other): 
        return vec3(
            self.x - other.x,
            self.y - other.y, 
            self.z - other.z)

    def mag(self):
        return math.sqrt(self.x * self.x
                 + self.y * self.y
                 + self.z * self.z)

    def lerp(self, other, t):
        return vec3(self.x * (1 - t) + other.x,
                    self.y * (1 - t) + other.y,
                    self.z * (1 - t) + other.z)


class Entity(object):
    """
    """
    
    def __init__(self, pos, image_filename, group=background):
        """
        """
        self.pos = pos
        self.image = pyglet.resource.image(image_filename)
        self.sprite = pyglet.sprite.Sprite(self.image, batch=batch, group=group)
        self.tile_width = 67 # TODO
        self.tile_height = 58 # TODO
        self.update_pos()

    def change_bitmap(self,image_filename):
        #print "Changed to ", image_filename
        self.image = pyglet.resource.image(image_filename)
        self.sprite.image = self.image

    def _pos2screenpos(self,pos):
        """
        2d grid -> hexagonal positioning
        """
        if (pos.x%2) == 0: # even
            y = pos.y 
        else:
            y = pos.y + 0.5
        return vec3(
            (WIN_WIDTH * 0.3)  + (50 * pos.x),
            (WIN_HEIGHT * 0.9) - (self.tile_height * y),
            0)

    def update_pos(self):
        realpos = self._pos2screenpos(self.pos)
        self.sprite.x = realpos.x
        self.sprite.y = realpos.y 
        
    def update(self,dt):
        pass


class Hole(Entity):
    def __init__(self, pos):
        """
        """
        Entity.__init__(self,pos,'graphics/tile_hole.png')
        self.teleport = True
        self.occupied = False


class Field(Entity):
    max_value = 4

    tiles = []
    for i in range(5):
        tiles.append(
            'graphics/tile_' + str(i) + '.png')
    active_img = pyglet.resource.image('graphics/tile_active.png')

    def __init__(self, pos):
        """
        """
        self.active_sprite = pyglet.sprite.Sprite(self.active_img, 
                                                  batch=batch, group=foreground)
        Entity.__init__(self,pos,self.tiles[0])
        self._active = True
        self.teleport = False
        self.occupied = False
        self.animation = False
        self.value = 0
        self._activedt = 0.2

    def update(self, dt):
        if self._active:
            self._activedt -= dt
            if self._activedt <= 0:
                self.deactivate()
                self.active_sprite.opacity = 0
            else:
                self.active_sprite.opacity = self._activedt * 510

    def update_pos(self):
        Entity.update_pos(self)
        self.active_sprite.x = self.sprite.x
        self.active_sprite.y = self.sprite.y 

    def increase(self):
        if self.value < self.max_value:
            self.value += 1
            self._update_bitmap()

    def decrease(self):
        if self.value > 0:
            self.value -= 1
            self._update_bitmap()

    def _update_bitmap(self):
        self.change_bitmap(self.tiles[self.value])

    def activate(self):
        self._active = True
        self._activedt = 0.5

    def deactivate(self):
        self._active = False
                

class Player(Entity):
    """ Player Avatar
    """
    opcodes_grid = []
    for i in range(10):
        opcodes_grid.append(
            pyglet.resource.image(
                'web/opcodes_' + str(i) + '.png'))

    def __init__(self, pos, controller_id, color, player_id=0):
        self.image_file = 'graphics/player_' + str(player_id) + '.png'
        Entity.__init__(self,pos,self.image_file, group=players)
        # center image anchor for rotation
        self.image.anchor_x = self.image.width // 2 
        self.image.anchor_y = self.image.height // 2

        ## movement
        self.moving = False
        self.update_pos()
        self.old_pos = vec3(self.pos.x, self.pos.y, self.pos.z)
        self.wrap_pos = False
        self.dest_pos = vec3(self.pos.x, self.pos.y, self.pos.z)
        
        ## direction
        self.rotating = False
        self.direction = 0
        self.old_direction = 0

        ## time
        self.time_index = 0
        self.timeout = 0
        self.granulation = 2

        ## color
        self.color =  [] 
        for i in range(3):
            self.color.append(eval('0x' + colors[player_id][i*2:(i*2)+2]))
        self.color.append(255)

        ## code
        self.code = []
        self.index = 0
        for i in range(8):
            self.code.append(random.randint(0,9))
        self.controller = controller_id
        self.player_id = player_id

        ## label
        self.labels = []
        for i in range(len(self.code)):
            self.labels.append(
                pyglet.sprite.Sprite(
                    self.opcodes_grid[0],
                    batch=batch, 
                    group=background,
                    x= 37 * (i + 1), 
                    y= WIN_HEIGHT - (self.player_id * 60) - 60))
            self.labels[-1].scale = 32.0 / self.labels[-1].width
        self.label = pyglet.text.Label(
            "Spieler " + str(self.player_id),
            font_name='Tahoma',
            font_size=12,
            x= 37, 
            y= WIN_HEIGHT - (self.player_id * 60) - 15,
            anchor_x='left', 
            color=self.color,
            anchor_y='center',
            batch=batch)

        self._update_label()
        if DEBUG:
            print "player id ", self.player_id, " created"

    
    def resetTimeout(self):
        self.timeout = 5

    def _change_time(self):
        self.granulation = [2,3,4,6,8][world.get_tile(self.pos).value]

    def active(self):
        return self.controller

    def change_code(self, index, change = False):
        if change:
            self.code[index] = (self.code[index] + change) % 10
        else:
            self.code[index] = 0
        self._update_label()

    def update(self,dt):
        if self.controller:
            if self.timeout < 0:
                world.controllers.pop(self.controller)
                self.controller = False
            else:
                self.timeout -= dt

        percent = ((self.time_index % (24 / self.granulation)) /
                   ((24.0 / self.granulation) - 1))
        if self.moving:
            self._change_position(percent=percent)
        if self.rotating:
            self._turn(percent=percent)
        if (self.time_index % (24 / self.granulation)) == 0:
            action = self.code[self.index]
            if 0 < action <= 9:
                if action == (1 or 'forward'):
                    self._move(forward=True)
                elif action == (2 or 'back'):
                    self._move(forward=False)
                elif action == (3 or 'turnLeft'):
                    self._turn(-1)
                elif action == (4 or 'turnRight'):
                    self._turn(1)
                elif action == (5 or 'jump'):
                    self._jump()
                elif action == (6 or 'increase'):
                    world.get_tile(self.pos).increase()
                elif action == (7 or 'decrease'):
                    world.get_tile(self.pos).decrease()
                elif action == (8 or 'time'):
                    self._change_time()
                elif action == (9 or 'action'):
                    self._action()
            self.index = (self.index + 1) % len(self.code)
        self._update_label(percent)
        self.time_index = (self.time_index + 1) % 24

    def _update_label(self, percent = 0):
        text = "Spieler " + str(self.player_id) + " "
        if not self.controller:
            text += "(frei):" 
        else:
            text += ":"
        self.label.text = text
        for index,i in enumerate(self.code):
            self.labels[index].image = self.opcodes_grid[i]
            if self.index == index:
                self.labels[index].opacity = 192 + (63 * (percent))
            elif self.index == ((index + 1) % len(self.code)):
                self.labels[index].opacity = 64 + (64 * (1 - percent))
            else:
                self.labels[index].opacity = 64

    def _turn(self, direction=0, percent=0):
        if percent == 0:
            self.rotating = True
            self.old_direction = self.direction
            self.direction =  (self.direction + direction) % 6
            if (self.old_direction + direction) == 6:
                self.old_direction = -1
            elif (self.old_direction + direction) == -1:
                self.old_direction = 6
        elif percent == 1:
            self.rotating = False
        self.sprite.rotation = (
            (self.direction * percent) +
            (self.old_direction * (1-percent))) * 60

    def _pos2screenpos(self,pos):
        """
        slightly different positioning for smaller graphics (hacky)
        """
        if 0 < (pos.x%2) <= 1: # odd
            y = pos.y + (0.5 * (pos.x%2))
        elif (pos.x%2) == 0:
            y = pos.y
        else:
            y = pos.y + (0.5 - (0.5 * ((pos.x%2) - 1)))
        return vec3(
            WIN_WIDTH*0.3  + 50*pos.x + 25 + self.sprite.width/2,
            WIN_HEIGHT*0.9 - self.tile_height*y + self.tile_height/2,
            0)
    
    def _change_position(self, pos=False, percent=0, wrap_pos=False): 
        if percent == 0:
            self.moving = True
            self.old_pos = self.pos
            world.get_tile(self.pos).occupied = False
            self.pos = pos
            self.dest_pos = pos
            world.get_tile(self.pos).occupied = True
            if wrap_pos:
                self.wrap_pos = wrap_pos
                self.dest_pos = self.wrap_pos
        elif percent == 1:
            self.moving = False
            self.wrap_pos = False
        if self.wrap_pos != False:
            if percent < 0.5:
                percent *= 1.5
            else:
                self.old_pos = vec3(self.wrap_pos.x%world.width,
                                     self.wrap_pos.y%world.height,
                                     self.wrap_pos.z)
                self.dest_pos = self.pos
                percent = (percent - 0.5) * 2
        new_pos = vec3(
            (self.dest_pos.x * percent) + (self.old_pos.x * (1-percent)), 
            (self.dest_pos.y * percent) + (self.old_pos.y * (1-percent)), 
            self.pos.z)
        realpos = self._pos2screenpos(new_pos)
        self.sprite.x = realpos.x
        self.sprite.y = realpos.y 

    def _get_target_pos(self, pos, forward=True):
        if forward:
            direction = self.direction
        else:
            direction = (self.direction + 3) % 6

        if direction == 0: # up
            pos.y -= 1
        elif direction < 3: # rightish
            pos.x += 1
        elif direction == 3: # down
            pos.y += 1
        else: # leftish
            pos.x -= 1

        if pos.x%2 == 0: # even
            if (direction == 2) or (direction == 4):
                pos.y += 1
        else:
            if (direction == 1) or (direction == 5):
                pos.y -= 1

        wrap_pos = False
        if ((pos.x < 0) or (pos.x >= world.width) 
            or (pos.y < 0) or (pos.y >= world.height)):
            wrap_pos = vec3(pos.x,pos.y,pos.z)
            pos.x = pos.x%world.width
            pos.y = pos.y%world.height
        return pos, wrap_pos

    def _move(self, forward=True, do_it=True, pos=False):
        """         
        movement in hexagonal fields 
        """
        if not pos:
            pos = vec3(self.pos.x,self.pos.y,self.pos.z)
        pos, wrap_pos = self._get_target_pos(pos, forward)
        if not world.get_tile(pos).occupied:
            if do_it:
                if world.get_tile(pos).teleport:
                    print "teleport!"
                    target = False
                    while not target:
                        target, pos, wrap_pos = self._move(
                            do_it=False,
                            pos=vec3(random.randint(0, world.width),
                                 random.randint(0, world.height),
                                 0))
                    
                self._change_position(pos, wrap_pos=wrap_pos)
            return True, pos, wrap_pos
        else:
            return False, pos, wrap_pos

    def _jump(self):
        amount = world.get_tile(self.pos).value
        if amount != 0:
            if amount == 1:
                self._move()
            else:
                new_pos = vec3(self.pos.x,self.pos.y,self.pos.z)
                target = False
                wrap = []
                for i in range(amount):
                    is_result, new_pos, wrap_pos = self._move(
                        do_it=False,pos=new_pos)
                    wrap.append(wrap_pos)
                    if is_result:
                        target_index = i
                        target = new_pos
                if target:
                    if world.get_tile(target).teleport:
                        self._move(target, do_it=True)
                    else:
                        wrap_pos = False
                        for i in range(target_index+1):
                            if wrap[i]:
                                wrap_pos = wrap[i]
                        self._change_position(target, wrap_pos=wrap_pos)
                
    def _action(self):
        tile = world.get_tile(self.pos)
        tile.activate()
        msg = osc.OSCMessage()
        msg.setAddress("/alj/action")
        for i in [self.player_id, 
              self.pos.x / float(world.width), 
              self.pos.y / float(world.height), 
              tile.value / float(tile.max_value),
              (1.0 / self.granulation) * (24 / FPS)]:
            msg.append(i)
        client.sendto(msg, SC_ADDR) 
        if DEBUG:
            print "actione!"


class BeeNoirWorld(object):
    """
    """
    
    def __init__(self, w, h):
        """
        """
        self.width=w
        self.height=h
        self.objs = []
        self.players = []
        self.controllers = dict()
        for i, color in enumerate(colors[:5]):
            self.players.append(Player(vec3(i,5,1),
                              False, color, i))

        for y in range(h):
            for x in range(w):
                self.objs.append(Field(vec3()))

        # make teleport fields
        middle = (w / 2 * w) + (h / 2)
        fields = [middle, middle - w]
        if (w / 2) % 2 == 0:
            fields.append(middle + 1)
            fields.append(middle - 1)
        else:
            fields.append(middle + 1 - w)
            fields.append(middle - 1 - w)
        for i in fields:
            self.objs[i] = Hole(vec3())

        for i in range(len(self.objs)):
            pos = vec3(i % self.width,
                   math.floor(i / self.width),
                   0)
            self.objs[i].pos = pos
            self.objs[i].update_pos()

    def mouse_pressed(self, x, y, button):
        """ 
        change a specific player's code on press 
        """
        if WIN_HEIGHT > y > WIN_HEIGHT - (len(self.players) * 60):
            if 37 < x < (len(self.players[-1].code) + 2) * 37:
                playerno = (WIN_HEIGHT - y) / 60
                if (WIN_HEIGHT - (playerno * 60) - 37) > y > (WIN_HEIGHT - 
                                                              (playerno * 60)) - 67:
                    change = False
                    if button == 1: change = 1
                    elif button == 4: change = -1
                    self.players[playerno].change_code((x - 37) / 37, change)
        

    def update(self,dt):
        if VERBOSE:
            print "upd ", self.players, len(self.players)
        for t in self.objs:
            t.update(dt)
        if self.players:
            for p in self.players:
                p.update(dt)

    def get_tile(self,pos):
        return self.objs[pos.x+pos.y*self.width]

## osc functions
def update_code(addr, tags, data, client_addr):
    if DEBUG:
        print "got update: ", data
    key = data[0]
    playerID = data[1]
    if key in world.controllers:
        if len(data[2:]) == len(world.players[world.controllers[key]].code):
            world.players[world.controllers[key]].code = data[2:]
        else:
            print "something went wrong: code is too short"

def ping_players(addr, tags, data, client_addr):
    if DEBUG:
        print "got ping: ", data
    key = data[0]
    if key in world.controllers:
        world.players[world.controllers[key]].resetTimeout()
    elif len(world.controllers) < PLAYERS:
        for i, p in enumerate(world.players):
            if not p.active():
                world.controllers[key] = i
                p.resetTimeout()
                p.controller = key
                msg = osc.OSCMessage()
                msg.setAddress("/alj/dict")
                for i in [key, i] + p.code:
                    msg.append(i)
                client.sendto(msg, NET_SEND_ADDR) 
                break
            else:
                print "something went wrong: there should be free players!"
    else:
        msg = osc.OSCMessage()
        msg.setAddress("/alj/dict")
        for i in [key, -1]:
            msg.append(i)
            client.sendto(msg, NET_SEND_ADDR)
        print "no free player!"

def get_player(addr, tags, data, client_addr):
    if DEBUG:
        print "got ping: ", data
    key = data[0]
    if key in world.controllers:
        world.players[world.controllers[key]].resetTimeout()
    elif len(world.controllers) < PLAYERS:
        for i, p in enumerate(world.players):
            if not p.active():
                world.controllers[key] = i
                p.resetTimeout()
                p.controller = key
                msg = osc.OSCMessage()
                msg.setAddress("/alj/dict")
                for i in [key, i] + p.code:
                    msg.append(i)
                client.sendto(msg, NET_SEND_ADDR) 
                break
            else:
                print "something went wrong: there should be free players!"
    else:
        msg = osc.OSCMessage()
        msg.setAddress("/alj/dict")
        for i in [key, -1]:
            msg.append(i)
            client.sendto(msg, NET_SEND_ADDR)
        print "no free player!"

if __name__ == '__main__':
    window = pyglet.window.Window(WIN_WIDTH, WIN_HEIGHT, caption='bee noir')

    world = BeeNoirWorld(WORLD_WIDTH,WORLD_HEIGHT)

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == key.ESCAPE:
            print "shutting down..."

            print "\nClosing OSCServer."
            oscServer.close()
            print "Waiting for Server-thread to finish"
            oscServerThread.join()
            pyglet.app.exit()
        return pyglet.event.EVENT_HANDLED


    @window.event
    def on_mouse_press(x, y, button, modifiers):
        world.mouse_pressed(x, y, button)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    ## start communication and send specs
    client = osc.OSCClient()

    oscServer = osc.OSCServer(NET_ADDR)
    oscServer.addDefaultHandlers()

    if len(sys.argv) > 1:
        SC_ADDR = ('127.0.0.1', int(sys.argv[1]))
    
    msg = osc.OSCMessage()
    msg.setAddress("/alj/start")
    for i in [world.width, world.height]:
        msg.append(i)
    client.sendto(msg, SC_ADDR) 

    oscServer.addMsgHandler("/alj/code", update_code)
    oscServer.addMsgHandler("/alj/ping", ping_players)
    oscServer.addMsgHandler("/alj/getplayer", get_player)

    # Start OSCServer
    print "\nStarting OSCServer. Use ctrl-C to quit."
    oscServerThread = threading.Thread( target = oscServer.serve_forever )
    oscServerThread.start()

    pyglet.clock.schedule_interval(world.update, 1/FPS)
    pyglet.app.run()

import random
import math
import sys

import OSC as osc

import pyglet.window
import pyglet.clock
from pyglet.window import key

from common import *

WIN_WIDTH = 1200
WIN_HEIGHT = 800

WORLD_WIDTH = 16
WORLD_HEIGHT = 12

PLAYERS = 10

CODESIZE = 8
CODEPAD = 37

FPS = 28.0

# Webserver-OSC->alj
# NET_ADDR = ('127.0.0.1', 57140)
# alj->Webserver-OSC:
# NET_SEND_ADDR = ('127.0.0.1', 57141)

# alj-OSC->SuperCollider
SC_ADDR = ('127.0.0.1', 57120)

SC_OSC_PREFIX = '/alj'

batch = pyglet.graphics.Batch()
background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)
players = pyglet.graphics.OrderedGroup(2)


class vec3(object):
    """
    """
    
    def __init__(self, x=0, y=0, z=0):
        """
        """
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other): 
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
            (WIN_WIDTH * 0.3)  + (50 * pos.x) + PADDING[0],
            (WIN_HEIGHT * 0.9) - (self.tile_height * y) + PADDING[1],
            0)

    def update_pos(self):
        realpos = self._pos2screenpos(self.pos)
        self.sprite.x = realpos.x
        self.sprite.y = realpos.y 
        
    def update(self,dt):
        pass


class Tile(Entity):
    """
    A generic tile
    """

    def __init__(self, pos, image):
        Entity.__init__(self,pos,image)
        self.occupied = False
        self._active = False
        self._activedt = 0.0
   
    def update(self, dt):
        if self._active:
            self._activedt -= dt
            if self._activedt <= 0:
                self._active = False
                self.sprite.opacity = 255
            else:
                self.sprite.opacity = 255 - self._activedt * 510
             
    def activate(self):
        self._active = True
        self._activedt = 0.5
        
    def is_teleport(self):
        return False


class Teleport(Tile):
    """
    A tile, that teleports the player to a random location when stepped on.
    """
    def __init__(self, pos):
        Tile.__init__(self,pos, 'graphics/tile_hole.png')
    
    def is_teleport(self):
        return True


class Field(Tile):
    """
    A tile, which has a value and can be activated
    """

    max_value = 4

    tiles = ['graphics/tile_%d.png'%(i) for i in range(5) ]
    active_img = pyglet.resource.image('graphics/tile_active.png')

    def __init__(self, pos):
        """
        """
        self.active_sprite = pyglet.sprite.Sprite(self.active_img, 
                                                  batch=batch, group=foreground)
        self.active_sprite.opacity = 0
        Tile.__init__(self,pos,self.tiles[0])
        self.animation = False
        self.value = 0

    def update(self, dt):
        if self._active:
            self._activedt -= dt
            if self._activedt <= 0:
                self._active = False
                self.active_sprite.opacity = 0
            else:
                self.active_sprite.opacity = self._activedt * (255 / 0.5)
        # if VERBOSE:
        #    if self.occupied:
        #        self.change_bitmap('graphics/tile.png')
        #    else:
        #        self._update_bitmap()

    def update_pos(self):
        Tile.update_pos(self)
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


class Player(Entity):
    """ 
    Generic Player
    """
    opcodes_grid = [pyglet.resource.image('web/opcodes_%d.png'%(i)) 
                     for i in range(10)]

    def __init__(self, world, pos, player_id=0, beat=0, title='GrundSpieler'):
        self.image_file = 'graphics/player_%d.png'%(player_id)
        Entity.__init__(self,pos,self.image_file, group=players)
        
        # center image anchor for rotation
        self.image.anchor_x = self.image.width // 2 
        self.image.anchor_y = self.image.height // 2
        self.world = world

        ## movement
        self.moving = False
        self.old_pos = vec3(self.pos.x, self.pos.y, self.pos.z)
        self.wrap_pos = False
        self.dest_pos = vec3(self.pos.x, self.pos.y, self.pos.z)
        self.update_pos()
        
        ## direction
        self.rotating = False
        self.direction = 0
        self.old_direction = 0

        ## time
        self.time_index = beat
        self.granulation = 16
        self.new_granulation = False

        ## color
        self.color =  [eval('0x' + colors[player_id][i*2:(i*2)+2]) 
                       for i in range(3)] + [255,]

        ## code
        self.code = [0] * CODESIZE
        self.index = 0
        self.player_id = player_id

        ## label
        
        self.labels = []
        ystart = self.player_id * LABEL_HEIGHT
        for i in range(CODESIZE):
            self.labels.append(
                pyglet.sprite.Sprite(
                    self.opcodes_grid[0],
                    batch=batch, 
                    group=foreground,
                    x= CODEPAD * (i + 1), 
                    y= window.height - ystart - 60))
            self.labels[-1].scale = 32.0 / self.labels[-1].width

        self.label = pyglet.text.Label(
            "%s %d"%(title, self.player_id),
            font_name='Tahoma',
            font_size=12,
            bold=True,
            x=CODEPAD + 10, 
            y=window.height - ystart - 15,
            anchor_x='left', 
            color=(222,) * 4 ,
            anchor_y='center',
            batch=batch)

        self.label_icon = pyglet.sprite.Sprite(self.image, 
                                               batch=batch, 
                                               group=background, 
                                               x=30, 
                                               y= window.height - 
                                               ystart - 20)
        self.label_icon.scale = 1
        self.label_icon.rotation = 20 + random.randint(0,100)

        self._update_label()

        self.send_status('newplayer')

        debug_print('player id %d created'%(self.player_id))


    def delete(self):
        self.send_status('playerdeleted')
        for i in [self.label, self.sprite, self.label_icon] + self.labels:
            i.delete()
        self.world.players[self.player_id] = False
        self.world.get_tile(self.pos).occupied = False
        
        debug_print('deleted player %d'%(self.player_id))

    def _change_time(self):
        self.new_granulation = [32, 24, 16, 12, 8][self.world.get_tile(self.pos).value]
        # old timing: [12,8,6,4,3]
        # [8, 6, 4, 3, 2]
        # 1/2, 3/8, 1/4, 3/16, 1/8

    def send_status(self, status):
        tile = self.world.get_tile(self.pos)
        send_osc_to_sc('/' + status,  [self.player_id, 
                               self.pos.x / float(self.world.width), 
                               self.pos.y / float(self.world.height), 
                               tile.value / float(tile.max_value),
                               (self.granulation / FPS)])

    def change_code(self, index, change = False):
        if change:
            self.code[index] = (self.code[index] + change) % 10
        else:
            self.code[index] = 0
        self._update_label()

    def active(self):
        return True

    def update(self,dt):
        percent = self.time_index / float(self.granulation - 1)
        if self.moving:
            self._change_position(percent=percent)
        if self.rotating:
            self._turn(percent=percent)

        if self.time_index == 0:
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
                    self._move(jump=True)
                elif action == (6 or 'increase'):
                    self.world.get_tile(self.pos).increase()
                elif action == (7 or 'decrease'):
                    self.world.get_tile(self.pos).decrease()
                elif action == (8 or 'time'):
                    self._change_time()
                elif action == (9 or 'action'):
                    self._action()

            self.index = (self.index + 1) % CODESIZE
            if self.new_granulation:
                self.granulation = self.new_granulation
                self.new_granulation = False
                self.time_index = 0

        self._update_label(percent)
        self.time_index = (self.time_index + 1) % self.granulation

    def _update_label(self, percent = 0):
        for index,i in enumerate(self.code):
            self.labels[index].image = self.opcodes_grid[i]
            if self.index == ((index + 1) % CODESIZE):
                self.labels[index].opacity = 192 + (63 * (percent))
            elif self.index == ((index + 2) % CODESIZE):
                self.labels[index].opacity = 64 + (64 * (1 - percent))
            else:
                self.labels[index].opacity = 64

    def _turn(self, direction=0, percent=0):
        """
        Turns the sprite to a new direction over time
        """
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
            (self.old_direction * (1 - percent))) * 60

  
    def _pos2screenpos(self,pos):
        """
        Translates a relative position to pixel coordinates
        """
        if 0 < (pos.x%2) <= 1: # odd
            y = pos.y + (0.5 * (pos.x%2))
        elif (pos.x%2) == 0:
            y = pos.y
        else:
            y = pos.y + (0.5 - (0.5 * ((pos.x%2) - 1)))

        return vec3(
            (WIN_WIDTH * 0.3  + 50 * pos.x 
             + (self.tile_width - self.sprite.width) / 2.0 
             + self.sprite.width / 2) + PADDING[0],
            (WIN_HEIGHT * 0.9 + 
             (self.tile_height - self.sprite.height) / 2.0 
             - self.tile_height * y + self.tile_height / 2) + PADDING[1],
            0)

    def _change_position(self, pos=vec3(), percent=0): 
        """
        Actually changes the position of the sprite over time
        """
        if percent == 0:
            self.moving = True
            self.old_pos = self.pos
            self.world.get_tile(self.pos).occupied = False
            self.pos = pos
            self.dest_pos = pos
            self.world.get_tile(self.pos).occupied = True
            if self.wrap_pos:
                self.dest_pos = self.wrap_pos
        elif percent == 1:
            self.moving = False
            self.wrap_pos = False

        if self.wrap_pos != False:
            if percent < 0.5:
                percent *= 1.5
            else:
                self.old_pos = vec3(self.wrap_pos.x%self.world.width,
                                     self.wrap_pos.y%self.world.height,
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

    def _get_target_pos(self, pos=False, forward=True):
        """
        Determines the next relative position in a hexagonal field
        """

        if not pos:
            pos = vec3(self.pos.x, self.pos.y, self.pos.z)
        
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
        if ((pos.x < 0) or (pos.x >= self.world.width) 
            or (pos.y < 0) or (pos.y >= self.world.height)):
            wrap_pos = vec3(pos.x,pos.y,pos.z)
            pos.x = pos.x % self.world.width
            pos.y = pos.y % self.world.height

        if not self.world.get_tile(pos).occupied:
            if wrap_pos:
                self.wrap_pos = wrap_pos
            return pos
        else:
            return False
        
    def _move(self, forward=True, jump=False):
        """         
        Moves the player to a new location
        """
        if jump:
            new_pos = vec3(self.pos.x,self.pos.y,self.pos.z)
            pos = False
            for i in range(self.world.get_tile(self.pos).value):
                new_pos = self._get_target_pos(pos=new_pos)
                if new_pos:
                    pos = new_pos
                else:
                    break
        else:
            pos = self._get_target_pos(forward=forward)

        if pos:
            if self.world.get_tile(pos).is_teleport():
                self._teleport()
                self.world.get_tile(pos).activate()
                pos = self.world.random_pos()
                self.send_status('teleport')
            elif jump: 
                self.send_status('jump')
            else:
                self.send_status('move')
            self._change_position(pos)
    
    def _teleport(self):
        print 'teleport!'

    def _action(self):
        tile = self.world.get_tile(self.pos)
        tile.activate()
        self.send_status('action')
        
        debug_print('actione!')


class BotPlayer(Player):
    """
    Player-Bot with randomly generated code
    """
    def __init__(self, world, pos, player_id=0, beat=0):
        Player.__init__(self, world, pos, player_id, beat, 'Bot')
        self.code = ([ random.randint(0,9) for i in range(CODESIZE - 4) ] + 
                     [ random.choice([1,2,3,4,6,9]) for i in range(3) ] + [ 9 ])
        random.shuffle(self.code)

    def _teleport(self):
        debug_print('teleport and scramble!')
        random.shuffle(self.code)


class WebPlayer(Player):
    """
    Player with specific controller and timeout
    """
    def __init__(self, world, pos, controller_id, player_id=0, beat=0):
        self.controller = controller_id
        self.title = 'Spieler'
        Player.__init__(self, world, pos, player_id, beat, self.title)
        self.timeout = 5
        send_osc_to_server('dict', [controller_id, player_id] + self.code)

    def update(self, dt):
        Player.update(self, dt)
        if self.timeout < -5:
            self.delete()
        elif (self.timeout < 0) and self.controller:
            self.world.controllers.pop(self.controller)
            self.controller = False          
        self.timeout -= dt

    def active(self):
        return self.controller

    def reset_timeout(self):
        self.timeout = 8

    def _update_label(self, percent = 0):
        Player._update_label(self, percent)
        text = self.title + ' ' + str(self.player_id)
        if not self.controller:
            text += ' (frei)' 
        self.label.text = text


class BeeNoirWorld(object):
    """
    Represents the game
    """
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.players = [False] * PLAYERS
        self.objs = [ Field(vec3()) for i in range(h*w) ]
        self.players_waiting = []
        self.controllers = dict()
        self.beat = 0

        ## make teleport fields
        middle = (w / 2 * w) + (h / 2)
        fields = [middle, middle - w]
        if (w / 2) % 2 == 0:
            fields.append(middle + 1)
            fields.append(middle - 1)
        else:
            fields.append(middle + 1 - w)
            fields.append(middle - 1 - w)
        for i in fields:
            self.objs[i] = Teleport(vec3())

        for i in range(len(self.objs)):
            pos = vec3(i % self.width,
                   math.floor(i / self.width),
                   0)
            self.objs[i].pos = pos
            self.objs[i].update_pos()

        self.label = pyglet.text.Label(
            'Bee Noir',
            font_name='Tahoma',
            font_size=22,
            bold=True,
            x=window.width - 20, 
            y=10,
            anchor_x='right', 
            color=(40, 88, 89, 255),
            anchor_y='bottom',
            batch=batch)
        

    def mouse_pressed(self, x, y, button):
        """ 
        change a specific player's code on press 
        """
        if window.height > y > (window.height -
                                PLAYERS * LABEL_HEIGHT):
            if CODEPAD < x < (CODESIZE + 2) * CODEPAD:
                playerno = int((window.height - y) / LABEL_HEIGHT)
                player = self.players[playerno]
                if player and (CODEPAD >
                               y - ((window.height -
                                     (playerno * LABEL_HEIGHT)) - 60) > 0):
                    change = False
                    if button == pyglet.window.mouse.LEFT: change = 1
                    elif button == pyglet.window.mouse.RIGHT: change = -1
                    player.change_code((x - CODEPAD) / CODEPAD, change)
                elif player and (button == pyglet.window.mouse.RIGHT):
                    player.delete()
                elif not player and (button == pyglet.window.mouse.LEFT):
                    self.players_waiting.append(('bot', playerno))
                    
    def create_waiting_players(self):
        """
        creates the waiting players all at once to avoid
        confusion in the rendering engine
        """
        for i in self.players_waiting:
            if not self.players[i[1]]:
                if i[0] == 'web':
                    self.create_web_player(i[1], i[2])
                elif i[0] == 'bot':
                    self.create_bot_player(i[1])
            else:
                print 'already there'
        if len(self.players_waiting) > 0:
            self.players_waiting = []

    def create_web_player(self, playerID, controllerID=False):
        self.controllers[controllerID] = playerID
        self.players[playerID] = WebPlayer(self, 
                                           self.random_pos(),
                                           controllerID, playerID,
                                           self.beat)

    def create_bot_player(self, playerID):
        self.players[playerID] = BotPlayer(self, 
                                           self.random_pos(),
                                           playerID,
                                           self.beat)

    def update(self,dt):
        self.beat = (self.beat + 1) % 16
        # debug_print('upd %s %s'%(self.players, PLAYERS))
        for t in self.objs:
            t.update(dt)
        if self.players:
            for p in self.players:
                if p:
                    p.update(dt)

    def random_pos(self):
        while True:
            pos = vec3(random.randint(0, self.width - 1),
                       random.randint(0, self.height - 1), 
                       0)
            tile = self.get_tile(pos)
            if not (tile.is_teleport() or tile.occupied):
                return pos

    def get_tile(self,pos):
        return self.objs[pos.x + pos.y * self.width]

    ## osc handler functions
    def update_code(self, addr, tags, data, client_addr):
        """
        Changes the code of a player to the one sent by its controller
        """
        debug_print('got update: %s'%(data))
        
        key = data[0]
        playerID = data[1]
        if key in self.controllers:
            if len(data[2:]) == CODESIZE:
                self.players[self.controllers[key]].code = data[2:]
            else:
                print 'something went wrong: code is too short'

    def ping_players(self, addr, tags, data, client_addr):
        """
        Resets the timeout of a player when pinged from the controller
        """
        debug_print('got ping: %s'%(data))

        key = data[0]
        if key in self.controllers:
            self.players[self.controllers[key]].reset_timeout()
        else:
            print 'no such controller: ', data

    def get_player(self, addr, tags, data, client_addr):
        """
        Returns the player to a specific controller or creates a new player
        """
        debug_print('got player request: %s'%(data))

        key = data[0]
        if key in self.controllers:
            p = self.players[self.controllers[key]]
            p.reset_timeout()
            send_osc_to_server("dict", [key, p.player_id] + p.code)
        elif len(filter(lambda x: x, self.players)) < PLAYERS:
            found = False
            counter = 50
            while not found:
                i = random.choice(range(PLAYERS))
                p = self.players[i]
                counter -= 1
                if not p: 
                    self.players_waiting.append(('web', i, key))
                    print 'created player nr ', i
                    found = True
                elif not p.active():
                    self.controllers[key] = i
                    p.reset_timeout()
                    p.controller = key
                    send_osc_to_server("dict", [key, i] + p.code)
                    found = True
                elif counter < 0:
                    found = True
                    print 'something went wrong: no free player found ...'
        else:
            send_osc_to_server("dict", [key, -1])
            print 'no free player!'


## osc functions
# def send_osc_to_server(addr, data):
#    send_osc(NET_SEND_ADDR, "/alj/" + addr, data)

def send_osc_to_sc(addr, data):
    send_osc(SC_ADDR, SC_OSC_PREFIX + addr, data)

def send_osc(netaddr, addr, data):
    msg = osc.OSCMessage()
    msg.setAddress(addr)
    for i in data:
        msg.append(i)
    try:
        client.sendto(msg, netaddr)
    except:
        print "Could not send OSC. Is SuperCollider running?"
        

if __name__ == '__main__':

    fullscreen = False
    for i, arg in enumerate(sys.argv):
        if arg == '-p':
            SC_ADDR = ('127.0.0.1', int(sys.argv[i+1]))
        elif arg == '-f':
            fullscreen = True

    if fullscreen:
        window = pyglet.window.Window(fullscreen=True, caption='bee noir')
    else:
        window = pyglet.window.Window(WIN_WIDTH, WIN_HEIGHT, caption='bee noir')


    PADDING = [int((window.width - WIN_WIDTH) / 2.0), 
               int((window.height - WIN_HEIGHT) / 2.0)]
    
    LABEL_HEIGHT = 1.0 * window.height/PLAYERS

    beenoir = BeeNoirWorld(WORLD_WIDTH,WORLD_HEIGHT)
    pyglet.gl.glClearColor(*[i/255.0 for i in [26,58,59,255]])

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == key.ESCAPE:
            print 'shutting down...'

            print '\nClosing OSCServer.'
            oscServer.close()
            print 'Waiting for Server-thread to finish'
            pyglet.app.exit()
        return pyglet.event.EVENT_HANDLED

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        beenoir.mouse_pressed(x, y, button)

    @window.event
    def on_draw():
        beenoir.create_waiting_players()
        window.clear()
        batch.draw()

    ## start communication
    client = osc.OSCClient()

    # oscServer = osc.OSCServer(NET_ADDR)
    # oscServer.addDefaultHandlers()

    send_osc_to_sc('/start', [beenoir.width, beenoir.height])

    # oscServer.addMsgHandler("/alj/code", beenoir.update_code)
    # oscServer.addMsgHandler("/alj/ping", beenoir.ping_players)
    # oscServer.addMsgHandler("/alj/getplayer", beenoir.get_player)


    pyglet.clock.schedule_interval(beenoir.update, 1/FPS)
    pyglet.app.run()

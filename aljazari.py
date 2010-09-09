import random
import math
import OSC as osc
import threading


import pyglet.window
import pyglet.clock

from pyglet.window import key
from pyglet.gl import *


WIN_WIDTH=1200
WIN_HEIGHT=800

WORLD_WIDTH=12
WORLD_HEIGHT=10

PLAYERS=10

# (verbose) debugging output
DEBUG=True
VERBOSE=False

# Webserver-OSC->alj
NET_ADDR=('127.0.0.1', 57140)
# alj->Webserver-OSC:
NET_SEND_ADDR=('127.0.0.1', 57141)

# alj-OSC->SuperCollider
SC_ADDR=('127.0.0.1', 57120)

batch = pyglet.graphics.Batch()
background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)

class vec3(object):
	"""
	"""
	
	def __init__(self, x=0,y=0,z=0):
		"""
		"""
		self.x=x
		self.y=y
		self.z=z

	def add(self,other): 
		return vec3(
			self.x + other.x,
			self.y + other.y, 
			self.z + other.z)

	def sub(self,other): 
		return vec3(
			self.x - other.x,
			self.y - other.y, 
			self.z - other.z)

	def mag(self):
		return math.sqrt(self.x * self.x
				 + self.y * self.y
				 + self.z * self.z)

	def lerp(self,other,t):
		return vec3(self.x * (1-t) + other.x,
			    self.y * (1-t) + other.y,
			    self.z * (1-t) +other.z)
	
## needs update: makes no sense in hex
# class circle(object):
# 	"""
# 	"""
	
# 	def __init__(self, centre, radius):
# 		"""
		
#                 Arguments:
#                 - `centre`:
#                 - `radius`:
#                 """
# 		self.centre = centre
#                 self.radius = radius

# 	def inside(self,pos):
# 		return pos.sub(self.centre).mag() < self.radius

class entity(object):
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

	def pos2screenpos(self,pos):
		"""
		2d grid -> hexagonal positioning
		"""
		if (pos.x%2) == 0: # even
			y = pos.y 
		else:
			y = pos.y + 0.5
		return vec3(
			(WIN_WIDTH * 0.4)  + (50 * pos.x),
			(WIN_HEIGHT * 0.8) - (self.tile_height * y),
			0)

	def update_pos(self):
		realpos = self.pos2screenpos(self.pos)
		self.sprite.x = realpos.x
		self.sprite.y = realpos.y 
		
	def update(self,frame,world):
		pass


# class animated_entity(entity):
# 	"""
# 	"""
# 	def __init__(self, pos, bitmap_filename):
# 		"""
# 		"""
# 		entity.__init__(self,pos,bitmap_filename)
# 		self.src_pos= vec3()
# 		self.dest_pos= vec3()
# 		self.time=10.0
# 		self.speed=0.0
		
# 	def move_to(self,pos,speed):
# 		self.src_pos=pos
# 		self.dest_pos=pos
# 		self.time=0.0
# 		self.speed=speed
		
# 	def update(self,dt, frame,world):
# 		## if self.time<1:
# 		## 	self.time += self.speed
# 		## 	if self.time>1:
# 		## 		self.time=1
# 		## 	self.pos = self.src_pos.lerp(self.dest_pos,self.time)
# 		self.pos = self.dest_pos
# 		self.update_pos()


class tile(entity):
	def __init__(self, pos):
		"""
		"""
		entity.__init__(self,pos,'graphics/tile.png')
		self.active = False

	def activate(self):
		self.change_state(True)

	def deactivate(self):
		self.change_state(False)

	def change_state(self,state):
		self.active = state
		if state:
			self.change_bitmap('graphics/tile-active.png')
		else:
			self.change_bitmap('graphics/tile.png')

		
class player_entity(entity):
	""" Player Avatar
	"""
	image = 'graphics/player.png'
	def __init__(self, pos, controller_id, color, player_id=0):
		entity.__init__(self,pos,self.image, group=foreground)
		# center image anchor for rotation
		self.image.anchor_x = self.image.width // 2 
		self.image.anchor_y = self.image.height // 2
		self.update_pos()

		self.direction = 0
		self.index = 0
		self.timeout = 0
		self.color = color
		self.code = []
		for i in range(8):
			self.code.append(random.randint(0,4))
		self.controller = controller_id
		self.player_id = player_id
		self.label = pyglet.text.Label(self.color,
					       font_name='Terminus',
					       font_size=14,
					       x=20, 
					       y= WIN_HEIGHT - (self.player_id * 20) - 20,
					       anchor_x='left', 
					       anchor_y='center',
					       batch=batch)
		self.update_label()
		if DEBUG:
			print "player id ", self.player_id, " created"

	
	def resetTimeout(self):
		self.timeout = 5

	def active(self):
		return self.controller

	def update(self,dt):
		if self.controller:
			if self.timeout < 0:
				world.controllers.pop(self.controller)
				self.controller = False
			else:
				self.timeout -= dt

		action = self.code[self.index]
		if 0 < action <= 5:
			if action == (1 or 'move'):
				self.move()
			elif action == (2 or 'turnRight'):
				self.turn_right()
			elif action == (3 or 'turnLeft'):
				self.turn_left()
			elif action == (4 or 'action'):
				self.action()
		self.update_label()
		if ((self.code[self.index-1] == (4 or 'action')) 
		    and (action != (4 or 'action'))):
			world.get_tile(self.pos).deactivate()
			
		self.index = (self.index + 1) % len(self.code)

	def update_label(self):
		text = self.color
		if not self.controller:
			text += " (inactive)"
		text += ": "
		for index,i in enumerate(self.code):
			if self.index == index:
				text += '>'
			else:
				text += ' '
			text += str(['_','M','R','L','A'][i])
		self.label.document.text = text

	def turn(self, direction):
		self.direction = (self.direction + direction) % 6
		self.sprite.rotation = self.direction * 60
		# if DEBUG:
		# 	print "Turn", self.direction, " ", self.sprite.rotation
			
	def turn_right(self):
		self.turn(1)

	def turn_left(self):
		self.turn(-1)

	def action(self):
		world.get_tile(self.pos).activate()
		msg = osc.OSCMessage()
		msg.setAddress("/alj/action")
		for i in [self.player_id, self.pos.x, self.pos.y]:
			msg.append(i)
		client.sendto(msg, SC_ADDR) 
		if DEBUG:
			print "actione!"

	def pos2screenpos(self,pos):
		"""
		slightly different positioning for smaller graphics (hacky)
		"""
		if (pos.x%2) == 1: # odd
			y = pos.y + 0.5
		else:
			y = pos.y
		return vec3(
			WIN_WIDTH*0.4  + 50*pos.x + 25 + self.sprite.width/2,
			WIN_HEIGHT*0.8 - self.tile_height*y + self.tile_height/2,
			0)

	def move(self):
		""" 
		movement in hexagonal fields 
		"""
		pos = vec3(self.pos.x,self.pos.y,self.pos.z)

		if self.direction == 0: # up
			pos.y -= 1
		elif self.direction < 3: # rightish
			pos.x += 1
		elif self.direction == 3: # down
			pos.y += 1
		else: # leftish
			pos.x -= 1

		if self.pos.x%2 == 1: # odd
			if (self.direction == 2) or (self.direction == 4):
				pos.y += 1
		else:
			if (self.direction == 1) or (self.direction == 5):
				pos.y -= 1

		if pos.x < 0:
			pos.x=world.width-1
		if pos.x >= world.width:
			pos.x=0
		if pos.y < 0:
			pos.y=world.height-1
		if pos.y >= world.height:
			pos.y=0
		if world.get_tile(pos).pos.z == 0:
			#if DEBUG:
			#	print pos.x, pos.y, self.pos.x, self.pos.y
			world.get_tile(self.pos).pos.z = 0
			self.pos = pos
			world.get_tile(self.pos).pos.z = 1
			self.update_pos()

		# if DEBUG:
		# 	print self.player_id, "Move ", self.direction, world.get_tile(self.pos).pos.z



class aljWorld(object):
	"""
	"""
	
	def __init__(self, w, h):
		"""
		"""
		self.width=w
		self.height=h
		self.objs = []
		self.my_name = "no name"

		self.players = []
		self.controllers = dict()
		for i, color in enumerate(['maroon', 'red','green', 'lime', 'olive', 
					   'yellow', 'navy', 'blue', 'purple', 
					   'fuchsia']):
			self.players.append(player_entity(vec3(i,5,1),
							  False, color, i))

		for y in range(h):
			for x in range(w):
				self.objs.append(tile(vec3()))

		for i in range(len(self.objs)):
			pos = vec3(i % self.width,
				   math.floor(i / self.width),
				   0)
			self.objs[i].pos = pos
			self.objs[i].update_pos()

	def update(self,dt):
		if VERBOSE:
			print "upd ", self.players, len(self.players)
		if len(self.players) > 0:
			for p in self.players:
				p.update(dt)

	def tile_occupied(self, pos):
		if self.get_tile(pos).z == 1:
			return True
		else:
			return False

	def get_tile(self,pos):
		"""
		"""
		return self.objs[pos.x+pos.y*self.width]

## osc functions
def update_code(addr, tags, data, client_addr):
	if DEBUG:
		print "got update: ", data
	key = data[0]
	if key in world.controllers:
		world.players[world.controllers[key]].code = data[1:]

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
				for i in [key, i]:
					msg.append(i)
				client.sendto(msg, NET_SEND_ADDR) 
				break
			else:
				print "something went wrong: no free player!"
	else:
		msg = osc.OSCMessage()
		msg.setAddress("/alj/dict")
		for i in [key, -1]:
			msg.append(i)
			client.sendto(msg, NET_SEND_ADDR)
		print "no free player!"
		

if __name__ == '__main__':
	window = pyglet.window.Window(WIN_WIDTH, WIN_HEIGHT, caption='alj')

	world = aljWorld(WORLD_WIDTH,WORLD_HEIGHT)

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
	def on_draw():
		window.clear()
		batch.draw()

	## start communication and send specs
	client = osc.OSCClient()

	oscServer = osc.OSCServer(NET_ADDR)
	oscServer.addDefaultHandlers()

	msg = osc.OSCMessage()
	msg.setAddress("/alj/start")
	for i in [world.width, world.height]:
		msg.append(i)
	client.sendto(msg, SC_ADDR) 

	oscServer.addMsgHandler("/alj/code", update_code)
	oscServer.addMsgHandler("/alj/ping", ping_players)

	# Start OSCServer
	print "\nStarting OSCServer. Use ctrl-C to quit."
	oscServerThread = threading.Thread( target = oscServer.serve_forever )
	oscServerThread.start()


	pyglet.clock.schedule_interval(world.update, 1/4.0)
	pyglet.app.run()

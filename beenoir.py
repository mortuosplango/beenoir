import random
import math
import OSC as osc
import threading
import sys

import pyglet.window
import pyglet.clock

from pyglet.window import key
from pyglet.gl import *


WIN_WIDTH=1200
WIN_HEIGHT=800

WORLD_WIDTH=16
WORLD_HEIGHT=12

PLAYERS=10

# (verbose) debugging output
DEBUG=True
VERBOSE=False

FPS=24.0

# Webserver-OSC->alj
NET_ADDR=('127.0.0.1', 57140)
# alj->Webserver-OSC:
NET_SEND_ADDR=('127.0.0.1', 57141)

# alj-OSC->SuperCollider
SC_ADDR=('127.0.0.1', 57120)

batch = pyglet.graphics.Batch()
background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)

colors = [ 'ffffff', 'ff0000', 'ff00ff', '0000ff', '00ffff',
  '00ff00', 'ffff00', '7f0000', '7f007f', '00007f',
  '007f7f', '007f00,' '827f00']



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
			(WIN_WIDTH * 0.3)  + (50 * pos.x),
			(WIN_HEIGHT * 0.9) - (self.tile_height * y),
			0)

	def update_pos(self):
		realpos = self.pos2screenpos(self.pos)
		self.sprite.x = realpos.x
		self.sprite.y = realpos.y 
		
	def update(self,frame,world):
		pass

class tile(entity):
	vertex_list = []
	max_value = 4

	def __init__(self, pos):
		"""
		"""
		self.image_file = 'graphics/tile_0.png'
		entity.__init__(self,pos,self.image_file)
		self.active = False
		self.occupied = False
		self.animation = False
		self.teleport = False
		self.value = 0

	def update(self, dt):
		if self.active:
			self.deactivate()

	def increase(self):
		#self.activate()
		if self.value < self.max_value:
			self.value += 1
			self.update_bitmap()

	def decrease(self):
		#self.activate()
		if self.value > 0:
			self.value -= 1
			self.update_bitmap()

	def update_bitmap(self):
		self.image_file = 'graphics/tile_' + str(self.value) + '.png'
		self.change_bitmap(self.image_file)

	def activate(self):
		self.change_state(True)

	def deactivate(self):
		self.change_state(False)
		
	def change_state(self,state):
		self.active = state
		if state:
			self.change_bitmap('graphics/tile_active.png')
		else:
			self.change_bitmap(self.image_file)

		
class player_entity(entity):
	""" Player Avatar
	"""
	#image = 'graphics/player.png'
	opcodes = pyglet.resource.image('graphics/opcodes.png')
	def __init__(self, pos, controller_id, color, player_id=0):
		self.image_file = 'graphics/player_' + str(player_id) + '.png'
		entity.__init__(self,pos,self.image_file, group=foreground)
		# center image anchor for rotation
		self.image.anchor_x = self.image.width // 2 
		self.image.anchor_y = self.image.height // 2

		## movement
		self.moving = False
		self.update_pos()
		self.old_pos = vec3(self.pos.x, self.pos.y, self.pos.z)
		
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
		self.opcodes_grid = pyglet.image.TextureGrid(
			pyglet.image.ImageGrid(self.opcodes, 2, 10))
		for i in range(len(self.code)):
			self.labels.append(
				pyglet.sprite.Sprite(
					self.opcodes_grid[0],
					batch=batch, 
					group=background,
					x= 37 * (i + 1), 
					y= WIN_HEIGHT - (self.player_id * 60) - 60))
			self.labels[-1].scale = 32.0/self.labels[-1].width
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

		self.update_label()
		if DEBUG:
			print "player id ", self.player_id, " created"

	
	def resetTimeout(self):
		self.timeout = 5

	def change_time(self):
		self.granulation = [2,3,4,6,8][world.get_tile(self.pos).value]

	def active(self):
		return self.controller

	def update(self,dt):
		if self.controller:
			if self.timeout < 0:
				world.controllers.pop(self.controller)
				self.controller = False
			else:
				self.timeout -= dt

		percent = (self.time_index % (24 / self.granulation)) / ((24.0 / self.granulation) - 1)
		if self.moving:
			self.change_position(percent=percent)
		if self.rotating:
			self.turn(percent=percent)
		if (self.time_index % (24 / self.granulation)) == 0:
			action = self.code[self.index]
			if 0 < action <= 9:
				if action == (1 or 'forward'):
					self.move(forward=True)
				elif action == (2 or 'back'):
					self.move(forward=False)
				elif action == (3 or 'turnLeft'):
					self.turn(-1)
				elif action == (4 or 'turnRight'):
					self.turn(1)
				elif action == (5 or 'jump'):
					self.jump()
				elif action == (6 or 'increase'):
					world.get_tile(self.pos).increase()
				elif action == (7 or 'decrease'):
					world.get_tile(self.pos).decrease()
				elif action == (8 or 'time'):
					self.change_time()
				elif action == (9 or 'action'):
					self.action()
			self.update_label()			
			self.index = (self.index + 1) % len(self.code)
		self.time_index = (self.time_index + 1) % 24

	def update_label(self):
		text = "Spieler " + str(self.player_id) + " "
		if not self.controller:
			text += "(frei):" 
		else:
			text += ":"
		self.label.text = text
		for index,i in enumerate(self.code):
			if self.index == index:
				self.labels[index].image = self.opcodes_grid[i+10]
			else:
				self.labels[index].image = self.opcodes_grid[i]

	def turn(self, direction=0, percent=0):
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

	def pos2screenpos(self,pos):
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
			
	def change_position(self, pos=False, percent=0, wrap=False): 
		if percent == 0:
			self.moving = True
			self.old_pos = self.pos
			world.get_tile(self.pos).occupied = False
			self.pos = pos
			world.get_tile(self.pos).occupied = True
			if wrap:
				self.moving = False
				percent = 1
		elif percent == 1:
			self.moving = False
		new_pos = vec3(
			(self.pos.x * percent) + (self.old_pos.x * (1-percent)), 
			(self.pos.y * percent) + (self.old_pos.y * (1-percent)), 
			self.pos.z)
		realpos = self.pos2screenpos(new_pos)
		self.sprite.x = realpos.x
		self.sprite.y = realpos.y 

	def move(self, forward=True, do_it=True, pos=False):
		""" 
		movement in hexagonal fields 
		"""

		if not pos:
			pos = vec3(self.pos.x,self.pos.y,self.pos.z)
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

		wrap = False
		if ((pos.x < 0) or (pos.x >= world.width) 
		    or (pos.y < 0) or (pos.y >= world.height)):
			pos.x = pos.x%world.width
			pos.y = pos.y%world.height
			wrap = True

		if not world.get_tile(pos).occupied:
			if do_it:
				if world.get_tile(pos).teleport:
					print "teleport!"
					target = False
					while not target:
						target, pos = self.move(
							do_it=False,
							pos=vec3(random.randint(0, world.width),
								 random.randint(0, world.height),
								 0))
					
				self.change_position(pos, wrap=wrap)
			return True, pos
		else:
			return False, pos

	def jump(self):
		amount = world.get_tile(self.pos).value
		if amount != 0:
			if amount == 1:
				self.move()
			else:
				new_pos = vec3(self.pos.x,self.pos.y,self.pos.z)
				target = False
				for i in range(amount):
					result = self.move(do_it=False,pos=new_pos)
					new_pos = result[1]
					if result[0]:
						target = new_pos
				if target:
					self.change_position(target, wrap=True)
				
	def action(self):
		tile = world.get_tile(self.pos)
		tile.activate()
		msg = osc.OSCMessage()
		msg.setAddress("/alj/action")
		for i in [self.player_id, 
			  self.pos.x/float(world.width), 
			  self.pos.y/float(world.height), 
			  tile.value /float(tile.max_value),
			  (1.0/self.granulation) * (24/FPS)]:
			msg.append(i)
		client.sendto(msg, SC_ADDR) 
		if DEBUG:
			print "actione!"


class aljWorld(object):
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
			self.players.append(player_entity(vec3(i,5,1),
							  False, color, i))

		for y in range(h):
			for x in range(w):
				self.objs.append(tile(vec3()))

		# make teleport fields
		middle = (w/2 * w + h/2)
		fields = [middle, middle - w]
		if (w/2)%2 == 0:
			fields.append(middle + 1)
			fields.append(middle - 1)
		else:
			fields.append(middle + 1 - w)
			fields.append(middle - 1 - w)
		for i in fields:
			self.objs[i].teleport = True
			self.objs[i].change_bitmap('graphics/tile_hole.png')

		for i in range(len(self.objs)):
			pos = vec3(i % self.width,
				   math.floor(i / self.width),
				   0)
			self.objs[i].pos = pos
			self.objs[i].update_pos()

	def update(self,dt):
		if VERBOSE:
			print "upd ", self.players, len(self.players)
		for t in self.objs:
			t.update(dt)
		if len(self.players) > 0:
			for p in self.players:
				p.update(dt)

	def get_tile(self,pos):
		return self.objs[pos.x+pos.y*self.width]

## osc functions
def update_code(addr, tags, data, client_addr):
	if DEBUG:
		print "got update: ", data
	key = data[0]
	if key in world.controllers:
		if len(data[1:]) == len(world.players[world.controllers[key]].code):
			world.players[world.controllers[key]].code = data[1:]
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
				for i in [key, i]:
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

	if len(sys.argv) > 1:
		SC_ADDR = ('127.0.0.1', int(sys.argv[1]))
	
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

	pyglet.clock.schedule_interval(world.update, 1/FPS)
	pyglet.app.run()

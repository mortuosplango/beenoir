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
	vertex_list = []
	max_value = 4
	# for i in range(6):
	# 	vertex_list.append(math.sin(i/6.0*2*M_PI))
	# 	vertex_list.append(math.cos(i/6.0*2*M_PI))

	def __init__(self, pos):
		"""
		"""
		self.image_file = 'graphics/tile_0.png'
		entity.__init__(self,pos,self.image_file)
		self.active = False
		self.occupied = False
		self.value = 0
		# vertex_list = batch.add(2, pyglet.gl.GL_POLYGON, None,
		# 			('v2i', vertex_list),
		# 			('c3B', (0, 0, 255) * 6))

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
			self.change_bitmap('graphics/tile-active.png')
		else:
			self.change_bitmap(self.image_file)

		
class player_entity(entity):
	""" Player Avatar
	"""
	#image = 'graphics/player.png'
	def __init__(self, pos, controller_id, color, player_id=0):
		self.image_file = 'graphics/player_' + str(player_id) + '.png'
		entity.__init__(self,pos,self.image_file, group=foreground)
		# center image anchor for rotation
		self.image.anchor_x = self.image.width // 2 
		self.image.anchor_y = self.image.height // 2
		self.update_pos()

		self.direction = 0
		self.index = 0
		self.time_index = 0
		self.timeout = 0

		self.color =  [] 
		for i in range(3):
			self.color.append(eval('0x' + colors[player_id][i*2:(i*2)+2]))
		self.color.append(255)

		self.code = []
		for i in range(8):
			self.code.append(random.randint(0,9))
		self.controller = controller_id
		self.player_id = player_id
		self.granulation = 2
		self.label = pyglet.text.Label("",
					       font_name='Terminus',
					       font_size=14,
					       x=20, 
					       y= WIN_HEIGHT - (self.player_id * 20) - 20,
					       anchor_x='left', 
					       color=self.color,
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
		if (self.time_index % (24 / self.granulation)) == 0:
			action = self.code[self.index]
			if 0 < action <= 9:
				if action == (1 or 'forward'):
					self.move(forward=True)
				elif action == (2 or 'back'):
					self.move(forward=False)
				elif action == (3 or 'turnRight'):
					self.turn_right()
				elif action == (4 or 'turnLeft'):
					self.turn_left()
				elif action == (5 or 'jump'):
					self.jump()
				elif action == (6 or 'action'):
					self.action()
				elif action == (7 or 'increase'):
					world.get_tile(self.pos).increase()
				elif action == (8 or 'decrease'):
					world.get_tile(self.pos).decrease()
				elif action == (9 or 'time'):
					self.change_time()
			self.update_label()			
			self.index = (self.index + 1) % len(self.code)
		self.time_index = (self.time_index + 1) % 24

	def change_time(self):
		self.granulation = [2,3,4,6,8][world.get_tile(self.pos).value]

	def update_label(self):
		text = ""
		if not self.controller:
			text += "(inactive)"
		text += ": "
		for index,i in enumerate(self.code):
			if self.index == index:
				text += '>'
			else:
				text += ' '
			text += str(['_','F','B','R','L','J','A','I','D','T'][i])
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
		tile = world.get_tile(self.pos)
		tile.activate()
		msg = osc.OSCMessage()
		msg.setAddress("/alj/action")
		for i in [self.player_id, 
			  self.pos.x/float(world.width), 
			  self.pos.y/float(world.height), 
			  tile.value /float(tile.max_value),
			  self.granulation]:
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
					self.change_position(target)
				
				
			
	def change_position(self, pos): 
		world.get_tile(self.pos).occupied = False
		self.pos = pos
		world.get_tile(self.pos).occupied = True
		self.update_pos()

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

		if pos.x < 0:
			pos.x=world.width-1
		if pos.x >= world.width:
			pos.x=0
		if pos.y < 0:
			pos.y=world.height-1
		if pos.y >= world.height:
			pos.y=0

		if not world.get_tile(pos).occupied:
			#if DEBUG:
			#	print pos.x, pos.y, self.pos.x, self.pos.y
			if do_it:
				self.change_position(pos)
			return True, pos
		else:
			return False, pos

		# if DEBUG:
		# 	print self.player_id, "Move ", direction, world.get_tile(self.pos).pos.z



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
				print "something went wrong: there should be free players!"
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


	pyglet.clock.schedule_interval(world.update, 1/24.0)
	pyglet.app.run()

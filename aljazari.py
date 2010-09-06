
import random
import math

import pyglet.window
import pyglet.clock
from pyglet.window import key
from pyglet.gl import *


WIN_WIDTH=1200
WIN_HEIGHT=800
WORLD_SIZE=10
DEBUG=True

filenames = [
	'sea-cube-01.png',    'sea-cube-02.png',    'sea-cube-03.png',
	'grass-cube-01.png', 'grass-cube-02.png','grass-cube-03.png',
	'red-grass-cube-01.png', 'red-grass-cube-02.png', 'red-grass-cube-03.png',
	'green-cube.png', 'blue-cube.png'
	]

class vec3(object):
	"""
	"""
	
	def __init__(self, x=0,y=0,z=0):
		"""
		"""
		self.x=x
		self.y=y
		self.z=z

	def add(self,other): return vec3(self.x + other.x,self.y + other.y, self.z + other.z)
	def sub(self,other): return vec3(self.x - other.x,self.y - other.y, self.z - other.z)
	def mag(self):
		return math.sqrt(self.x * self.x
				 + self.y * self.y
				 + self.z * self.z)

	def lerp(self,other,t):
		return vec3(self.x * (1-t) + other.x,
			    self.y * (1-t) + other.y,
			    self.z * (1-t) +other.z)
	


class rnd_gen(object):
	"""
	"""
	
	def __init__(self):
		"""
		"""
		self.state=0

	def seed(self,s):
		self.state=s

	def rnd_int(self):
		self.state=10331 * self.state + 1203432033
		self.state=self.state % 256
		return self.state

	def rnd_flt(self):
		return self.rnd_int()/256.0

class circle(object):
	"""
	"""
	
	def __init__(self, centre, radius):
		"""
		
                Arguments:
                - `centre`:
                - `radius`:
                """
		self.centre = centre
                self.radius = radius

	def inside(self,pos):
		return pos.sub(self.centre).mag() < self.radius

class entity(object):
	"""
	"""
	
	def __init__(self, pos, image_filename):
		"""
		"""
		self.pos = pos
		self.image = pyglet.resource.image(image_filename)
		self.sprite = pyglet.sprite.Sprite(self.image, batch=batch)
		self.scale = 1.0 # todo: replace with matrix
		self.rotate = 0.0
		self.tileWidth = 67
		self.tileHeight = 58
		self.update_pos()

	def change_bitmap(self,image_filename):
		#print "Changed to ", image_filename
		self.image = pyglet.resource.image(image_filename)
		self.sprite.image = self.image

	def pos2screenpos(self,pos):
		if (pos.x%2) == 1: # odd
			y = pos.y + 0.5
		else:
			y = pos.y
		return vec3(
			(WIN_WIDTH * 0.4)  + (50 * pos.x),
			(WIN_HEIGHT * 0.8) - (self.tileHeight * y),
			0)

	def update_pos(self):
		realpos = self.pos2screenpos(self.pos)
		self.sprite.x = realpos.x
		self.sprite.y = realpos.y 
		
	def update(self,frame,world):
		pass


class animated_entity(entity):
	"""
	"""
	def __init__(self, pos, bitmap_filename):
		"""
		"""
		entity.__init__(self,pos,bitmap_filename)
		self.src_pos= vec3()
		self.dest_pos= vec3()
		self.time=10.0
		self.speed=0.0
		
	def move_to(self,pos,speed):
		self.src_pos=pos
		self.dest_pos=pos
		self.time=0.0
		self.speed=speed
		
	def update(self,dt, frame,world):
		## if self.time<1:
		## 	self.time += self.speed
		## 	if self.time>1:
		## 		self.time=1
		## 	self.pos = self.src_pos.lerp(self.dest_pos,self.time)
		self.pos = self.dest_pos
		self.update_pos()


class tile(entity):
	def __init__(self, pos):
		"""
		"""
		entity.__init__(self,pos,'graphics/tile.png')

class player_entity(entity):
	""" Player Avatar
	"""
	images = ['graphics/player.png',
		  'graphics/player.png',
		  'graphics/player.png',
		  'graphics/player.png']
	
	def __init__(self, pos):
		entity.__init__(self,pos,self.images[0])
		self.direction = 1
		self.code = [1,1,2,1,
			     1,1,2,4]
		self.index = 0

	def update(self,dt):
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
		self.index = (self.index + 1) % len(self.code)

	def turn(self, direction):
		self.direction = (self.direction + direction) % 6
		self.sprite.rotation = self.direction * 60
		if DEBUG:
			print "Turn", self.direction, " ", self.sprite.rotation
			

	def turn_right(self):
		self.turn(1)

	def turn_left(self):
		self.turn(-1)

	def action(self):
		print "actione!"

	def move(self):
		pos = vec3(self.pos.x,self.pos.y,self.pos.z)

		if self.direction == 0: # up
			pos.y -= 1
		elif self.direction == 3: # down
			pos.y += 1
		elif 1 <= self.direction <= 2: # rightish
			pos.x += 1
		elif 4 <= self.direction <= 5: # leftish
			pos.x -= 1

		if self.pos.x%2 == 0: # even
			if (self.direction == 2) or (self.direction == 4):
				pos.y -= 1
		else:
			if (self.direction == 1) or (self.direction == 5):
				pos.y += 1

		if pos.x < 0:
			pos.x=world.width-1
		if pos.x >= world.width:
			pos.x=0
		if pos.y < 0:
			pos.y=world.height-1
		if pos.y >= world.height:
			pos.y=0
		if world.get_cube(pos).pos.z > -1:
			self.pos = pos
			self.pos.z = world.get_cube(self.pos).pos.z+1
			self.update_pos()

		if DEBUG:
			print "Move ", self.direction



class wilderness_world(object):
	"""
	"""
	
	def __init__(self, w, h):
		"""
		"""
		self.width=w
		self.height=h
		self.objs = []
		self.my_name = "no name"

		for y in range(h):
			for x in range(w):
				self.objs.append(tile(vec3()))

		self.update_world(vec3())
		self.players = [ ]
		self.players.append(player_entity(vec3(5,5,1)))

		
	def update_world(self,pos):
		"""
		"""
		self.world_pos=pos
		circles = []
					
		for i in range(len(self.objs)):
			pos = vec3(i % self.width,
				   math.floor(i / self.width),
				   0)

			self.objs[i].pos = pos
			self.objs[i].update_pos()

	def update(self,dt):
		for p in self.players:
			p.update(dt)

	def get_cube(self,pos):
		"""
		"""
		return self.objs[pos.x+pos.y*self.width]

	def add_server_plant(self,pos,type=-1):
		# call by reference! :S
		self.plants.append(plant(self.my_name,
					 vec3(pos.x,pos.y,1),
					 self.world_pos,
					 type))

window = pyglet.window.Window(WIN_WIDTH, WIN_HEIGHT, caption='tune-x')

label = pyglet.text.Label('Hello, groworld',
                          font_name='Trebuchet MS',
                          font_size=36,
                          x=window.width//2, y= (7 * window.height//8),
                          anchor_x='center', anchor_y='center')


batch = pyglet.graphics.Batch()
world = wilderness_world(WORLD_SIZE,WORLD_SIZE)

pyglet.clock.schedule_interval(world.update, 1/1.0)

window.push_handlers(world.players[0])

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.ENTER:
	    world.players[0].turn_right()
    elif symbol == key.RIGHT:
	    world.players[0].move()
    elif symbol == key.LEFT:
	    world.players[0].move()
    elif symbol == key.UP:
	    world.players[0].move()
    elif symbol == key.DOWN:
	    world.players[0].move()
#    return pyglet.event.EVENT_HANDLED


@window.event
def on_draw():
    window.clear()
    batch.draw()
    label.draw()
#    world.player.sprite.draw()



#buildWorld(10)
pyglet.app.run()

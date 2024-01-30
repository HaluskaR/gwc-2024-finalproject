from math import sin
from processing import *

# This is a map creation program/puzzle/adventure game for GWC 2024!
# On run, it loads in a map from a few choices (I suggest the demo to start). Control the character with
# WASD and collect all the keys to win.

# The challenge is that not all required types of tiles have been implemented; look below for unimplemented
# tiles and what they're supposed to do! You can add new tiles, new items etc.
# Scroll down to the DATA section if you'd like to add a map.

# Have fun and good luck!

screen_side_length = 400
chosen_level = None  # Set this to a level name to bypass level select (should help with debugging)

###################################################   TILES   ####################################################

######## TILETYPES ######## 
# Take a look at the TileType object for an idea of what's available to you, and Ice and Water for how some tiles
# can be implemented. Scroll down a bit to see unimplemented ones (marked with comments describing what
# they should do). Feel free to create brand new tiles!

class TileType(object):
  color = (0, 0, 0)
  def __init__(self, block):
    self.block = block

  def can_enter(self, player):
    return True
    
  def can_leave(self, player):
    return True
    
  def enter(self, player):
    return
    
  def leave(self, player):
    return
  
  def draw(self, map):
    stroke(255, 255, 255, 100)
    fill(*self.color)
    rect(self.block.x*map.grid_square_length, self.block.y*map.grid_square_height,
         map.grid_square_length, map.grid_square_height, 0)
    
  
class Ice(TileType):
  color = (230, 230, 255)
  def leave(self, player):
    self.block.set_tile(Water(self.block))
    
class Water(TileType):
  color = (140, 140, 255)

  def can_enter(self, player):
    return player.has("flippers")
  
  def enter(self, player):
    player.hydration = 100
    
class Grass(TileType):
  color = (120, 200, 10)
  
class Rock(TileType):
  # Rock cannot be passed through (optional: without a pickaxe). Test in any level but demo
  color = (120, 100, 140)
  def can_enter(self, player):
    return False
  
class RockFloor(TileType):
  color = (80, 60, 100)

# Prisha
class Teleporter(TileType):
  # Teleporters skip the player forward 3 blocks in the direction they entered. Test in teleport_across
  color = (255, 0, 210)
  
# Cedalia
class Sludge(TileType):
  # Sludge damages the player when stepped on, but is turned to rock floor right after. Test in sludge_lavafields
  color = (180, 90, 120)
  def enter(self, player):
    player.health -= 8
    # print("You stamp out the sludge, but it deals some damage. Health: {}".format(player.health))
    print("You step on the sludge and it deals some damage. Health: {}".format(player.health))
  
# Bhadra
class Lava(TileType):
  # Lava deals more damage than sludge and is not destroyed when stepped on. Test in sludge_lavafields
  color = (240, 150, 0)
  
# Nikita
class HealBlock(TileType):
  # Heal blocks refill the player's health to full. Test in heal_corridor
  color = (255, 160, 180)


class OneTimeHeal(TileType):
  # One time heal blocks refill the player's health, then turn to rock floor. Will also need a map! :)
  color = (200, 165, 165)

# ISH
class QuickSand(TileType):
  # Quicksand has a %chance of not being able to exit. Test in quicksand
  color = (220, 175, 100)


######## ITEMS ########
# Items are a bit simpler than TileTypes, and there's only one for now (keys). Use it as a template if
# you'd like to make another!

class Item(object):
  color = (0, 0, 0)
  item_name = "unset"
  def __init__(self, block):
    self.block = block
    
  def claim(self, player):
    player.claim(self.item_name)
    self.block.set_item(None)
    
  def enter(self, player):
    return
  
  def draw(self, map):
    stroke(255)
    fill(*self.color)
    item_margin = map.grid_square_length / 4
    rect(self.block.x*map.grid_square_length + item_margin,
         self.block.y*map.grid_square_height + item_margin,
         map.grid_square_length - item_margin*2,
         map.grid_square_height - item_margin*2, 0)
    
class Key(Item):
  item_name = "key"
  color = (220, 200, 0)
  
  def enter(self, player):
    self.claim(player)

#####################################################################################################################

########################################### ADDITIONAL CLASSES ##################################################

class Block(object):
  # An individual block on the map. Contains a tile, zero or one items, and possibly the player.
  has_player = False
  
  def __init__(self, tilegen, item, x, y):
    self.tiletype = tilegen(self)
    self.item = item(self)
    # These are used ONLY to do the draw call.
    # we can't (seemingly?) return a canvas like we could in js to be drawn at some position, so kludge
    self.x = x
    self.y = y
    
  def can_enter(self, player):
    return self.tiletype.can_enter(player)
  
  def can_leave(self, player):
    return self.tiletype.can_leave(player)

  def enter(self, player):
    self.tiletype.enter(player)
    if self.item:
      self.item.enter(player)
    self.has_player = True
    self.draw(player.map)
    
  def leave(self, player):
    self.tiletype.leave(player)
    self.has_player = False
    self.draw(player.map)
    
  def set_tile(self, tiletype):
    self.tiletype = tiletype
    
  def set_item(self, item):
    self.item = item
    
  def draw(self, map):
    self.tiletype.draw(map)
    if self.item:
      self.item.draw(map)
    if self.has_player:
      map.draw_player(self.x, self.y)

  
class Map(object):
  # The map, which creates itself from a template and holds all the required blocks.
  def __init__(self, map_name, player):
    self.name = map_name
    map_template = maps[map_name]
    self.win_condition = map_template["win_condition"]
    map_height = len(map_template["terrain"])
    map_width = len(map_template["terrain"][0])
    self.grid_square_length = screen_side_length/map_width
    self.grid_square_height = screen_side_length/map_height
    self.blocks = []
    for y in range(map_height):
      row = []
      for x in range(map_width):
        block = Block(terrain[map_template["terrain"][y][x]],
                      item[map_template["items"][y][x]],
                      x, y)
        if x == player.x and y == player.y:
          block.has_player = True
        block.draw(self)
        row.append(block)
      self.blocks.append(row)
      
  def draw_player(self, x, y):
    stroke(255)
    fill(100, 100, 100)
    item_margin = self.grid_square_length / 1.5
    rect(x*self.grid_square_length + item_margin,
         y*self.grid_square_height + item_margin,
         self.grid_square_length - item_margin*2,
         self.grid_square_height - item_margin*2, 0)

 
class Player(object):
  # move in 4 directions: DONE
  # lose health: DONE
  # gain health
  # fight
  # check health, end game if <=0 (die): DONE
  # have inventory (currency?): DONE
  # change world on tilestep: DONE
  health = 100
  currency = 0
  hydration = 100
  inventory = []
  x = 0
  y = 0
  map = None
  game_over = False
  chosen_level = None
  
  def choose_level(self):
    print("Available levels: {}".format(", ".join(maps.keys())))
    while self.chosen_level not in maps.keys():
      self.chosen_level = raw_input("Enter name of level to load: ")
  
  def start_level(self):
    self.x = maps[self.chosen_level]["player_start_x"]
    self.y = maps[self.chosen_level]["player_start_y"]
    self.health = 100
    self.currency = 0
    self.inventory = []
    self.map = Map(self.chosen_level, player)
   
  def has(self, item_name):
    return item_name in self.inventory
      
  def claim(self, item_name):
    self.inventory.append(item_name)
    print("Picked up {}".format(item_name))
    
  def win(self):
    fill(142, 255, 242)
    textSize(40)
    text("YOU WIN!", screen_side_length * 0.26, screen_side_length * 0.5)
    self.game_over = True
    
  def lose(self):
    fill(200, 0, 0)
    textSize(40)
    text("YOU LOSE...", screen_side_length * 0.26, screen_side_length * 0.5)
    self.game_over = True
       
  def take_turn(self, dir):
    if self.game_over:
      self.chosen_level = None
      self.choose_level()
      self.start_level()
      self.game_over = False
      return
    self.move_direction = dir
    if not self.map.blocks[self.y][self.x].can_leave(self):
      return
    new_x = self.x
    new_y = self.y
    if dir == "left":
      new_x -= 1
    elif dir == "right":
      new_x += 1
    elif dir == "up":
      new_y -= 1
    elif dir == "down":
      new_y += 1
    if (new_x > -1 and new_x < len(self.map.blocks)
        and new_y > -1 and new_y < len(self.map.blocks[0])
        and self.map.blocks[new_y][new_x].can_enter(self)):
      self.map.blocks[self.y][self.x].leave(self)
      self.map.blocks[new_y][new_x].enter(self)
      self.x = new_x
      self.y = new_y
    if self.health <= 0:
      self.lose()
    if self.hydration < 10:
      self.health -= 2
      print("You are dehydrated. Health: {}".format(player.health))
    if self.map.win_condition(self):
      self.win()

#####################################################################################################################

##################################################### DATA #######################################################

terrain = {
  0: lambda x: Grass(x),
  1: lambda x: Ice(x),
  2: lambda x: Water(x),
  3: lambda x: Rock(x),
  4: lambda x: RockFloor(x),
  5: lambda x: Teleporter(x),
  6: lambda x: Sludge(x),
  7: lambda x: Lava(x),
  8: lambda x: HealBlock(x),
  9: lambda x: OneTimeHeal(x),
  10: lambda x: QuickSand(x)
}

item = {
  0: lambda x: None,
  1: lambda x: Key(x),
}

maps ={
  "demo": {"player_start_x": 2, "player_start_y": 0,
    "win_condition": lambda x: x.inventory.count("key") == 3,
    "terrain": [
     [2, 2, 1, 2, 2, 2],
     [2, 1, 1, 2, 2, 2],
     [1, 1, 2, 2, 1, 1],
     [1, 1, 1, 1, 1, 1],
     [2, 2, 2, 2, 2, 1],
     [2, 2, 2, 2, 1, 1]
     ], "items": [
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [1, 0, 0, 0, 0, 1],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 1, 0]
     ]},
  "quicksand": {"player_start_x": 3, "player_start_y": 1,
    "win_condition": lambda x: x.inventory.count("key") == 3,
    "terrain": [
     [10, 10, 10, 10, 10],
     [10, 10, 10, 10, 10],
     [10, 10, 10, 10, 10],
     [10, 10, 10, 10, 10],
     [10, 10, 10, 10, 10]
     ], "items": [
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 1, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 1, 0]
     ]},
  "teleport_across": {"player_start_x": 3, "player_start_y": 3,
    "win_condition": lambda x: x.inventory.count("key") == 1,
    "terrain": [
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 4, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 4, 4, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 5, 3, 3, 4, 4, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 4, 4, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 4, 4, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 4, 4, 4, 4],
     [0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 4, 4, 4, 4],
     [0, 2, 2, 0, 0, 0, 0, 0, 3, 3, 4, 4, 4, 4, 4],
     [2, 2, 2, 2, 0, 0, 0, 0, 3, 3, 4, 4, 4, 4, 4],
     [2, 2, 2, 2, 2, 2, 0, 0, 3, 3, 3, 4, 4, 4, 4]
     ], "items": [
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
     ]},
  "sludge_lavafields": {"player_start_x": 3, "player_start_y": 0,
    "win_condition": lambda x: x.inventory.count("key") == 2,
    "terrain": [
     [6, 6, 6, 4, 6, 6, 7],
     [6, 7, 7, 7, 6, 6, 7],
     [6, 7, 7, 7, 6, 7, 3],
     [6, 6, 3, 6, 6, 3, 4],
     [3, 6, 3, 6, 7, 6, 6],
     [4, 4, 4, 6, 6, 6, 7],
     [4, 4, 4, 4, 6, 7, 7]
     ], "items": [
     [0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 1],
     [0, 0, 0, 0, 0, 0, 0],
     [0, 1, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0]
     ]},
  "heal_corridor": {"player_start_x": 0, "player_start_y": 1,
    "win_condition": lambda x: x.inventory.count("key") == 1,
    "terrain": [
     [3, 3, 3, 3, 3, 3, 3],
     [4, 6, 6, 6, 6, 6, 3],
     [3, 3, 3, 3, 3, 6, 8],
     [3, 6, 6, 6, 6, 6, 3],
     [8, 6, 3, 3, 3, 3, 3],
     [3, 6, 6, 6, 6, 8, 3],
     [3, 3, 3, 3, 3, 3, 3]
     ], "items": [
     [0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 1, 0],
     [0, 0, 0, 0, 0, 0, 0]
     ]},
}

#####################################################################################################################

def keyPressed():
  global player
  if keyboard.key=="w":
    player.take_turn("up")
  elif keyboard.key=="a":
    player.take_turn("left")
  elif keyboard.key=="s":
   player.take_turn("down")
  elif keyboard.key=="d":
    player.take_turn("right")
  elif keyboard.key=="q":
    setup()
  
def setup():
  global player
  player = Player()
  size(screen_side_length, screen_side_length)
  background(0, 255, 0)
  frameRate(24)
  if chosen_level == None:
    player.choose_level()
  else:
    player.chosen_level = chosen_level
  player.start_level()

run()

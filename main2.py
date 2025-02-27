import pygame  # type: ignore
import math
import time
import threading
from sys import exit

# Some global variables
grass_loc = "img/grass.png"
wall_col = (121, 125, 13)
friction = 0.98
in_motion = False
max_level = 4
total_time = 300 #In seconds [5 minutes]
time_left = total_time
count_down_running = False

class Level:
     def __init__(self, walls, ball, hole, platforms, buttons, title):
          self.walls = walls
          self.ball = ball
          self.hole = hole
          self.platforms = platforms
          self.buttons = buttons
          self.title = title
          self.def_ball_pos = ball.pos if ball != None else None

     def add_objects(self, screen):
          global current_mode, current_level, reset_btn

          for platform in self.platforms:
               screen.blit(platform.img, (platform.x, platform.y))

          self.hole.draw(screen)

          # Draw the ball and walls
          self.ball.draw(screen)

          # If the ball is not moving, show the direction
          if not self.ball.is_moving:
               cursor_pos = pygame.mouse.get_pos()
               self.ball.show_dir(cursor_pos, screen)

          # Move the ball if it's in motion
          self.ball.move()

          # Check for collisions with walls
          for wall in self.walls:
               collision, closest_x, closest_y = wall.rect_collision(self.ball)

               if collision:
                    self.ball.deflect(closest_x, closest_y)

               wall.draw(screen)

          # Check if the ball is inside the hole
          if self.hole.check_ball_in_hole(self.ball):
               if current_level >= max_level:
                    current_mode = "END_MENU"
               else:
                    current_level += 1
                    current_mode = f"LEVEL_{current_level}"

     def add_buttons(self, screen):
          for button in self.buttons:
               button.draw(screen)

          self.title.create_title(screen)

     def reset_ball(self):
          self.ball.x = self.def_ball_pos[0]
          self.ball.y = self.def_ball_pos[1]
          self.ball.pos = self.def_ball_pos
          self.ball.vel_x = 0
          self.ball.vel_y = 0

class Title:
     def __init__(self, text):
          self.text = text

     def create_title(self, screen):
          font = pygame.font.Font(None, 90)
          text_surf = font.render(self.text, True, "BLACK")
          screen.blit(text_surf, (650, 100))

class Button:
    def __init__(self, x, y, width, height, text, action):
          self.rect = pygame.Rect(x, y, width, height)
          self.text = text
          self.action = action
          self.width = width
          self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, "WHITE", self.rect)
        font = pygame.font.Font(None, 50)
        text_surf = font.render(self.text, True, "BLACK")
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def check_click(self, mouse_pos):
          global current_level

          if self.rect.collidepoint(mouse_pos):
               current_level += 1
               self.action()
          

# A Ball class
class Ball:
     def __init__(self, x, y, radius):
          self.x = x
          self.y = y
          self.pos = (x, y)
          self.vel_x = 0
          self.vel_y = 0
          self.rad = radius
          self.circle = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
          self.is_moving = False  # Flag to check if the ball is moving

     # Method to draw the ball
     def draw(self, screen):
          pygame.draw.circle(screen, "White", (int(self.x), int(self.y)), self.rad)
          pygame.draw.circle(screen, "Black", (int(self.x), int(self.y)), self.rad, 5)

     def show_dir(self, mouse_pos, screen):
          global m_posA
          # Calculates and draws the direction line from the ball to the mouse position
          # Meaning it rotates the mouse position by 180 degrees around the ball's position
          m_posA = (2 * self.x - mouse_pos[0], 2 * self.y - mouse_pos[1])
          pygame.draw.line(screen, "Black", self.pos, m_posA, 3)

     # Method to move the ball based on calculated velocity
     def move(self):
          if self.is_moving:
               # Move the ball based on the velocity and angle
               self.x += self.vel_x * math.cos(angle)
               self.y += self.vel_y * math.sin(angle)
               self.pos = (self.x, self.y)

               # Apply friction to slow the ball down
               self.vel_x *= friction
               self.vel_y *= friction

               # Stop the ball if it's very slow
               if abs(self.vel_x) < 0.01 and abs(self.vel_y) < 0.01:
                    self.is_moving = False
                    self.vel_x = 0
                    self.vel_y = 0

     # Method to shoot the ball in the direction of the line
     def shoot(self):
          global angle

          # Gets the x and y component of the vector
          direction_x = m_posA[0] - self.x
          direction_y = m_posA[1] - self.y

          # Gets the whole angle (all 4 quadrants instead of 2)
          angle = math.atan2(direction_y, direction_x)
          distance = math.hypot(direction_x, direction_y)

          # Gets the preferred velocity (Its just my preference, no special logic)
          self.vel_x = math.sqrt(distance)
          self.vel_y = math.sqrt(distance)

          self.is_moving = True

     # Method to handle deflection
     def deflect(self, closest_x, closest_y):
          # Calculates the difference in the ball's position to the closest point of the wall
          delta_x = self.x - closest_x
          delta_y = self.y - closest_y 

          # Checks if the ball is hitting a vertical wall or a horizontal wall
          if abs(delta_x) > abs(delta_y):
               # Vertical collision -> reflect horizontally
               self.vel_x = -self.vel_x
          else:
               # Horizontal collision -> reflect vertically
               self.vel_y = -self.vel_y

class Platform:
     img = pygame.image.load(grass_loc)

     def __init__(self, x, y, width, height):
          self.x = x
          self.y = y
          self.width = width
          self.height = height
          self.img = pygame.image.load(grass_loc)
          self.img = pygame.transform.scale(self.img, (self.width, self.height))

# A class for the Walls
class Wall:
     def __init__(self, x, y, width, height):
          self.x = x
          self.y = y
          self.width = width
          self.height = height
          self.wall = pygame.Rect(x, y, width, height)

     # Method to draw the wall
     def draw(self, screen):
          pygame.draw.rect(screen, wall_col, self.wall)
          pygame.draw.rect(screen, "Black", (self.x, self.y, self.width, self.height), 5)

     def rect_collision(self, ball):
          closest_x = max(self.wall.left, min(ball.x, self.wall.right))
          closest_y = max(self.wall.top, min(ball.y, self.wall.bottom))

          distance = math.sqrt((closest_x - ball.x) ** 2 + (closest_y - ball.y) ** 2)

          return distance <= ball.rad, closest_x, closest_y

# A class for the Hole
class Hole:
     def __init__(self, x, y, radius):
          self.x = x
          self.y = y
          self.rad = radius
          self.hole = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

     # Method to draw the Hole
     def draw(self, screen):
          pygame.draw.circle(screen, "Black", (self.x, self.y), self.rad)

     # Method to check if the ball is inside the hole
     def check_ball_in_hole(self, ball):
          distance = math.hypot(self.x - ball.x, self.y - ball.y)
          return distance <= self.rad
     
def start_game():
     global current_mode, current_level, timer_thread, count_down_running
     current_mode = f"LEVEL_{current_level}"
     count_down_running = True
     timer_thread = threading.Thread(target=count_down)
     timer_thread.start()

def exit_game():
     pygame.quit()
     exit()

def reset_ball():
     global current_mode, levels, lvl_idxs
     level = levels[lvl_idxs[current_mode]]
     level.reset_ball()

def go_to_menu():
     global current_mode, lvl_idxs, level_list, current_level, total_time, time_left, count_down_running

     current_mode = "START_MENU"
     current_level = 0
     time_left = total_time
     count_down_running = False

     key_list = list(lvl_idxs.keys())
     level_list = [levels[lvl_idxs[level]] for level in key_list]

     for level in level_list:
          level.ball.x = level.def_ball_pos[0]
          level.ball.y = level.def_ball_pos[1]
          level.ball.pos = level.def_ball_pos
          level.ball.vel_x = 0
          level.ball.vel_y = 0
          level.ball.is_moving = False

def count_down():
     global time_left, current_mode

     while time_left > 0 and count_down_running:
          time.sleep(1)
          time_left -= 1

     try:
          raise ValueError("Something went wrong")
     except:
          if current_mode in list(lvl_idxs.keys()):
               current_mode = "GAME_OVER_MENU"

# Initialize the game
pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

cursor_pos = None

sky_img = pygame.image.load("img/sky.png")
sky_img = pygame.transform.scale(sky_img, (2500, 1000))

#Level-1 Platforms
platforms_1 = [
     Platform(400, 200, 500, 200),
     Platform(800, 200, 200, 400)
]

#Level-1 Walls
walls_1 = [
     Wall(450, 150, 600, 50),
     Wall(1000, 150, 50, 450),
     Wall(800, 600, 250, 50),
     Wall(400, 400, 400, 50),
     Wall(400, 150, 50, 250),
     Wall(750, 450, 50, 200)
]

#Level-2 Platforms
platforms_2 = [
     Platform(400, 100, 200, 500),
     Platform(400, 600, 550, 200),
     Platform(950, 400, 200, 400),
     Platform(950, 200, 350, 200)
]

#Level-2 Walls
walls_2 = [
     Wall(350, 100, 50, 700),
     Wall(350, 800, 800, 50),
     Wall(1150, 400, 50, 450),
     Wall(1200, 400, 100, 50),
     Wall(1300, 200, 50, 250),
     Wall(950, 150, 400, 50),
     Wall(900, 150, 50, 450),
     Wall(600, 550, 300, 50),
     Wall(600, 100, 50, 450),
     Wall(350, 50, 300, 50)
]

#Level-3 Platforms
platforms_3 = [
     Platform(100, 600, 400, 200),
     Platform(500, 300, 200, 500),
     Platform(700, 300, 300, 200),
     Platform(800, 100, 200, 300),
     Platform(1000, 100, 400, 200),
     Platform(1200, 300, 200, 500)
]

#Level-3 Walls
walls_3 = [
     Wall(50, 600, 50, 250),
     Wall(100, 800, 650, 50),
     Wall(700, 500, 50, 300),
     Wall(750, 500, 300, 50),
     Wall(1000, 300, 50, 200),
     Wall(1050, 300, 150, 50),
     Wall(1150, 350, 50, 500),
     Wall(1200, 800, 250, 50),
     Wall(1400, 50, 50, 750),
     Wall(750, 50, 650, 50),
     Wall(750, 100, 50, 200),
     Wall(450, 250, 300, 50),
     Wall(450, 300, 50, 300),
     Wall(50, 550, 400, 50)
]

#Level-4 Platforms
platforms_4 = [
     Platform(100, 100, 400, 200),
     Platform(300, 300, 200, 300),
     Platform(500, 400, 400, 200),
     Platform(700, 600, 200, 200),
     Platform(900, 600, 400, 200),
     Platform(1100, 100, 200, 500),
     Platform(1300, 100, 200, 200)
]

#Level-4 Wall
walls_4 = [
     Wall(50, 50, 50, 300),
     Wall(100, 300, 200, 50),
     Wall(250, 350, 50, 300),
     Wall(300, 600, 400, 50),
     Wall(650, 650, 50, 200),
     Wall(700, 800, 650, 50),
     Wall(1300, 300, 50, 500),
     Wall(1350, 300, 200, 50),
     Wall(1500, 50, 50, 250),
     Wall(1050, 50, 450, 50),
     Wall(1050, 100, 50, 500),
     Wall(900, 550, 150, 50),
     Wall(900, 350, 50, 200),
     Wall(500, 350, 400, 50),
     Wall(500, 50, 50, 300),
     Wall(100, 50, 400, 50)
]

levels = [
     Level(walls_1, Ball(550, 300, 20), Hole(900, 500, 20), platforms_1, None, None),
     Level(walls_2, Ball(450, 150, 20), Hole(1200, 300, 20), platforms_2, None, None),
     Level(walls_3, Ball(200, 700, 20), Hole(1300, 700, 20), platforms_3, None, None),
     Level(walls_4, Ball(200, 200, 20), Hole(1400, 200, 20), platforms_4, None, None)
]

buttons1 = [
     Button(750, 400, 100, 50, "Start", start_game),
     Button(750, 500, 100, 50, "Exit", exit_game)
]

buttons2 = [
     Button(750, 400, 100, 50, "Menu", go_to_menu)
]

reset_btn = Button(1300, 50, 100, 50, "Reset", reset_ball)

start_menu = Level(None, None, None, None, buttons1, Title("Mini-Golf"))
end_menu = Level(None, None, None, None, buttons2, Title("Congratulations!"))
loss_menu = Level(None, None, None, None, buttons2, Title("GAME OVER!"))

"""
NOTE: The following array `parts` is only for the information of the different parts of 
the game, the array is not used in any part of the code
"""
parts = [
     "START_MENU",
     "LEVEL_1",
     "LEVEL_2",
     "LEVEL_3",
     "LEVEL_4",
     "GAME_OVER_MENU",
     "END_MENU"
]

lvl_idxs = {
     "LEVEL_1" : 0,
     "LEVEL_2" : 1,
     "LEVEL_3" : 2,
     "LEVEL_4" : 3
}

current_mode = "START_MENU"
current_level = 0

font = pygame.font.Font(None, 70)

# Main game loop
while True:
     if total_time == 0:
          current_mode = "GAME_OVER_MENU"

     if current_mode not in ["START_MENU", "GAME_OVER_MENU", "END_MENU", "LEVEL_5"]:
          level_index = lvl_idxs[current_mode]              

     for event in pygame.event.get():
          if event.type == pygame.QUIT:
               pygame.quit()
               exit()

          if event.type == pygame.MOUSEBUTTONDOWN and current_mode in list(lvl_idxs.keys()) and not levels[level_index].ball.is_moving:
               levels[level_index].ball.shoot()
          if event.type == pygame.MOUSEBUTTONDOWN and current_mode == "START_MENU":
               for button in buttons1:
                    button.check_click(pygame.mouse.get_pos())

          if event.type == pygame.MOUSEBUTTONDOWN and current_mode in ["END_MENU", "GAME_OVER_MENU"]:
               for button in buttons2:
                    button.check_click(pygame.mouse.get_pos())

          if event.type == pygame.MOUSEBUTTONDOWN and current_mode in list(lvl_idxs.keys()):
               reset_btn.check_click(pygame.mouse.get_pos())
               
     screen.blit(sky_img, (0, 0))

     if current_mode not in ["START_MENU", "GAME_OVER_MENU", "END_MENU", "LEVEL_5"]:
          timer_indicator = font.render(str(time_left), True, "BLACK")
          
          if current_mode == "LEVEL_3":
               reset_btn.rect = pygame.Rect(50, 100, reset_btn.width, reset_btn.height)
               screen.blit(timer_indicator, (50, 50))
          elif current_mode == "LEVEL_4":
               screen.blit(timer_indicator, (50, 600))
               reset_btn.rect = pygame.Rect(50, 650, reset_btn.width, reset_btn.height)
          else:
               screen.blit(timer_indicator, (50, 50))

          reset_btn.draw(screen)

          try:
               if current_mode not in ["GAME_OVER_MENU", "START_MENU"]:
                    level_index = lvl_idxs[current_mode]
                    levels[level_index].add_objects(screen)
          except:
               loss_menu.add_buttons(screen)
     elif current_mode == "START_MENU":
          start_menu.add_buttons(screen)
     elif current_mode == "END_MENU":
          end_menu.add_buttons(screen)
     elif current_mode == "GAME_OVER_MENU":
          loss_menu.add_buttons(screen)
     
     pygame.display.update()
     clock.tick(60)
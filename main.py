import pygame #type: ignore
import math
from sys import exit

#Some global variables
grass_loc = "img/grass.png"
wall_col = (121, 125, 13)
friction = 0.9
in_motion = False

#A Ball class
class Ball:
     def __init__(self, x, y, radius):
          self.x = x
          self.y = y
          self.pos = (x, y)
          self.acc = 0
          self.accX = 0
          self.accY = 0
          self.rad = radius
          self.vel_x = 0
          self.vel_y = 0
          self.angle = 0
          self.circle = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

     #Method to draw the ball
     def draw(self, screen):
          pygame.draw.circle(screen, "White", (int(self.x), int(self.y)), self.rad)
          pygame.draw.circle(screen, "Black", (int(self.x), int(self.y)), self.rad, 5)

     def show_dir(self, mouse_pos, screen):
          global m_posA
          #Rotates the current position of the cursor by 180deg
          m_posA = (2 * self.x - mouse_pos[0], 2 * self.y - mouse_pos[1])
          #Draws the line from ball position to cursor_pos'
          pygame.draw.line(screen, "Black", self.pos, m_posA, 3)

     #Method to move the ball
     def move(self):
          if(self.acc == 0):
               distance = math.dist(m_posA, self.pos)
               self.acc = math.log10(distance/100)
               print(self.acc)

               x1, y1 = self.pos[0], self.pos[1]
               x2, y2 = m_posA[0], m_posA[1]
               
               slope = (y2 - y1)/(x2 - x1)
               self.angle = math.atan(slope)

               self.accX = self.acc * math.cos(self.angle)
               self.accY = self.acc * math.sin(self.angle)

          self.vel_x += self.accX
          self.vel_y += self.accY

          self.x += self.vel_x
          self.y += self.vel_y

          self.pos = (self.x, self.y)

#A class for the Walls
class Wall:
     def __init__(self, x, y, width, height):
          self.x = x
          self.y = y
          self.width = width
          self.height = height
          self.wall = pygame.Rect(x, y, width, height)

     #Method to draw the wall
     def draw(self, screen):
          pygame.draw.rect(screen, wall_col, self.wall)
          pygame.draw.rect(screen, "Black", (self.x, self.y, self.width, self.height), 5)

#A class for the Hole
class Hole:
     def __init__(self, x, y, radius):
          self.x = x
          self.y = y
          self.rad = radius
          self.hole = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

     #Method to draw the Hole
     def draw(self, screen):
          pygame.draw.circle(screen, "Black", (self.x, self.y), self.rad)
          

#Initialize the game
pygame.init()

screen = pygame.display.set_mode((1500, 800))
clock = pygame.time.Clock()

cursor_pos = None

sky_img = pygame.image.load("img/sky.png")
sky_img = pygame.transform.scale(sky_img, (1500, 800))

grass1 = pygame.image.load(grass_loc);
grass1 = pygame.transform.scale(grass1, (500, 200))

grass2 = pygame.image.load(grass_loc);
grass2 = pygame.transform.scale(grass2, (200, 400))

walls_1 = [
     Wall(450, 150, 600, 50),
     Wall(1000, 150, 50, 450),
     Wall(800, 600, 250, 50),
     Wall(400, 400, 400, 50),
     Wall(400, 150, 50, 250),
     Wall(750, 450, 50, 200)
]

hole_1 = Hole(900, 500, 20)
ball_1 = Ball(550, 300, 20)

while True:
     for event in pygame.event.get():
          if event.type == pygame.QUIT:
               pygame.quit()
               exit()

          if event.type == pygame.MOUSEBUTTONDOWN and not in_motion:
               ball_1.move()
               in_motion = True
               break

     
     screen.blit(sky_img, (0, 0))
     screen.blit(grass1, (400, 200))
     screen.blit(grass2, (800, 200))
     hole_1.draw(screen)
     ball_1.draw(screen)

     for wall in walls_1:
          wall.draw(screen)

     if in_motion:
          ball_1.move()
     else:
          cursor_pos = pygame.mouse.get_pos()
          ball_1.show_dir(cursor_pos, screen)
          in_motion = False

     if abs(ball_1.vel_x) > 0.01 or abs(ball_1.vel_y) > 0.01:
          ball_1.vel_x *= friction
          ball_1.vel_y *= friction
     else:
          ball_1.acc, ball_1.vel_x, ball_1.vel_y = 0, 0, 0

     pygame.display.update()
     clock.tick(60)
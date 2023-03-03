#write a game of breakout
# 1. import the modules
import pygame
import random
import math
import random
import queue
from pygame.locals import *
# 2. initialize the game
pygame.init()

SCR_width = 640
SCR_height = 480

screen = pygame.display.set_mode((SCR_width, SCR_height))

pygame.display.set_caption("Breakout")
# 3. create the game objects

#elements are pyro (red), hydro (blue), electro (purple), and cryo (cyan)
    
element_color_dict = {'pyro': (255, 0, 0), 'hydro': (0, 0, 255), 'electro': (255, 0, 255), 'cryo': (0, 255, 255)}

lives = 3
gamestarted = False
hitstopQueue = pygame.sprite.Group()

class Background(pygame.sprite.Sprite):
    def __init__(self, image_file):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = 0,0

#broken
class Animation(pygame.sprite.Sprite):
  def __init__(self, spritesheet, framecount, width, height, x, y, callback_list=None):
    pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
    self.image = pygame.image.load(spritesheet)
    self.rect = pygame.Rect(0,0,width,height)
    self.rect.center = (x,y)
    self.rect.left, self.rect.top = 0,0
    self.frames = []
    self.frame = 0
    for i in range(framecount):
      self.frames.append(self.image.subsurface((i * width, 0, width, height)))

  def update(self):
    self.image = self.frames[self.frame]
    self.frame += 1
    if self.frame == len(self.frames):
      for callback in self.callback_list:
        brick, element = callback
        brick.reaction(element)

class CollisionChecker(pygame.sprite.Sprite):
  #this class is a single pixel and its purpose is to check for collisions
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface((1, 1))
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)

def check_collision(x, y, bricks):
  sprite = CollisionChecker(x, y)
  br = pygame.sprite.spritecollide(sprite, bricks, False)
  sprite.kill()
  return br[0] if br else None
 
class Ball(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.element = 'pyro'
    self.image = pygame.Surface((10, 10))
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.speed = 0
    self.angle = random.randint(0, 360)
    self.superconduct = False
  def update(self):
    self.image.fill(element_color_dict[self.element])
    if self.superconduct:
      self.image.fill((255, 255, 255))
    self.rect.centerx += self.speed * math.cos(self.angle * math.pi / 180)
    self.rect.centery += self.speed * math.sin(self.angle * math.pi / 180)
    global gamestarted
    global lives
    if gamestarted:
      self.speed = 5
    else:
      self.speed = 0
      self.rect.centerx = pygame.mouse.get_pos()[0]
      self.rect.centery = 450
      self.element = paddle.element
    if self.rect.left <= 0 or self.rect.right >= 640:
      self.angle = 180 - self.angle
      self.superconduct = False
    if self.rect.top <= 0 or self.rect.bottom >= SCR_height:
      self.angle = -self.angle
      self.superconduct = False
    if self.rect.bottom >= SCR_height:
      if len(balls) > 1:
        self.kill()
      else:
        gamestarted = False
        lives-=1

class Paddle(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.element = 'pyro'
    self.image = pygame.Surface((100, 10))
    self.image.fill((255, 255, 255))
    self.rect = self.image.get_rect()
    self.rect.center = (320, 460)
  def update(self):
    self.image.fill(element_color_dict[self.element])
    self.rect.centerx = pygame.mouse.get_pos()[0]
    if self.rect.left < 0:
      self.rect.left = 0
    if self.rect.right > SCR_width:
      self.rect.right = SCR_width

class Brick(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.element = random.choice(['pyro', 'hydro', 'electro', 'cryo'])
    self.health = 3
    self.frost_timer = 0
    self.image = pygame.Surface((60, 30))
    self.image.fill(element_color_dict[self.element])
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
  def update(self):
    self.image.set_alpha(255 * self.health / 3)
    if self.frost_timer > 0:
      self.frost_timer -= 1
      self.image.fill((0, 255, 255))
    else:
      self.image.fill(element_color_dict[self.element])
    if self.health <= 0:
      self.kill()

  def getElement(self):
    if self.frost_timer > 0:
      return 'cryo'
    else:
      return self.element

  def reaction(self, element:str, ball = None):
    if (element == 'pyro' and self.getElement() == 'hydro') or \
      (element == 'hydro' and self.getElement() == 'pyro'):
      print('vaporize')
      self.kill()
    elif (element == 'cryo' and self.getElement() == 'pyro') or \
      (element == 'pyro' and self.getElement() == 'cryo'):
      print('melt')
      self.kill()
    elif (element == 'hydro' and self.getElement() == 'electro') or \
      (element == 'electro' and self.getElement() == 'hydro'):
      print('electro-charged')
      self.kill()
      for i in [(0,self.rect.height), (self.rect.width,0), (0,-self.rect.height), (-self.rect.width,0)]:
        x = self.rect.centerx + i[0]
        y = self.rect.centery + i[1]
        #get the existing brick at this position
        brick = check_collision(x, y, bricks)
        if brick:
          brick.reaction(element)
    elif (element == 'electro' and self.getElement() == 'cryo') or \
        (element == 'cryo' and self.getElement() == 'electro'):
      print('superconduct')
      self.kill()
      if ball:
        ball.superconduct = True
    elif (element == 'cryo' and self.getElement() == 'hydro') or \
        (element == 'hydro' and self.getElement() == 'cryo'):
      print('freeze')
      self.frost_timer = 60*5
      for i in [(0,self.rect.height), (self.rect.width,0), (0,-self.rect.height), (-self.rect.width,0)]:
        brick = check_collision(self.rect.centerx + i[0], self.rect.centery + i[1], bricks)
        if brick:
          brick.frost_timer = 60*5
    elif (element == 'pyro' and self.getElement() == 'electro') or \
        (element == 'electro' and self.getElement() == 'pyro'):
      print('overload')
      hitstopQueue.add(Animation('assets/overload.png',5,120,120,self.rect.centerx,self.rect.centery))
      self.kill()
      for i in [(0,self.rect.height), (self.rect.width,0), (0,-self.rect.height), (-self.rect.width,0)]:
        x = self.rect.centerx + i[0]
        y = self.rect.centery + i[1]
        #get the existing brick at this position
        brick = check_collision(x, y, bricks)
        if brick:
          brick.health -= 1
          brick.reaction(element)
    else: 
      if self.health == 1:
        self.kill()
      else:
        self.health -= 1

    

      
background = Background('assets/bg.jpg')
balls = [Ball(320, 450)]
paddle = Paddle()
bricks = pygame.sprite.Group()
for x in range(0, SCR_width, 60):
  for y in range(0, 240, 30):
    bricks.add(Brick(x + 30, y + 15))

allsprites = pygame.sprite.OrderedUpdates(paddle, balls[0])
allsprites.add(bricks)
# 4. keep looping through
clock = pygame.time.Clock()
keepGoing = True

# left and right arrows to move paddle
while keepGoing:
  if len(hitstopQueue)!=0:
    for ball in balls:
      #ball.speed = 0
      pass
  else:
    for ball in balls:
      ball.speed = 5

  # 5. clear the screen before drawing it again
  screen.fill((0, 0, 0))
  screen.fill([255, 255, 255])
  screen.blit(background.image, background.rect)
  # 6. draw the screen elements
  allsprites.draw(screen)
  # 7. update the screen
  pygame.display.flip()
  # 8. loop through the events; left arrow to move left, right arrow to move right
  for event in pygame.event.get():
    if event.type == QUIT:
      keepGoing = False
    elif event.type == KEYDOWN:
      if event.key == K_ESCAPE:
        keepGoing = False
      if event.key == K_LEFT:
        paddle.rect.left -= 5
      if event.key == K_RIGHT:
        paddle.rect.right += 5
      if event.key == K_1:
        paddle.element = 'pyro'
      if event.key == K_2:
        paddle.element = 'hydro'
      if event.key == K_3:
        paddle.element = 'electro'
      if event.key == K_4:
        paddle.element = 'cryo'
    #mouse click
    elif event.type == MOUSEBUTTONDOWN and not gamestarted:
      gamestarted = True
      balls[0].angle = -90
  
  # 9. move the objects
  allsprites.update()
  ballsHitList = pygame.sprite.spritecollide(paddle, balls, False)
  if ballsHitList:
    for ball in ballsHitList:
      #the balls's angle depends on where it hits the paddle; center is 0, left is -70, right is 70
      print(ball.rect.centerx-paddle.rect.centerx)
      ball.angle = 180*(ball.rect.centerx - paddle.rect.right)/(paddle.rect.width)
      if ball.angle > -30:
        ball.angle = -30
      if ball.angle < -150:
        ball.angle = -150
      ball.element = paddle.element

  #now check for brick collision; make sure to differentiate which side of the brick the ball hit
  for ball in balls:
    brickHitList = pygame.sprite.spritecollide(ball, bricks, False)
    for brick in brickHitList:
      print('hit')
      brick.reaction(ball.element, ball)
      if ball.superconduct:
        brick.kill()
      else:
        if ball.rect.left <= brick.rect.left or ball.rect.right >= brick.rect.right:
          if ball.angle < 3:
            ball.angle = -ball.angle
          else: ball.angle = 180 - ball.angle
        elif ball.rect.top < brick.rect.top or ball.rect.bottom > brick.rect.bottom:
          ball.angle = -ball.angle
      break
    
    
  if len(bricks) == 0:
    keepGoing = False
  clock.tick(60)

# 10. quit the game
pygame.quit()

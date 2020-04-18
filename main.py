import pygame
from pygame import *
from pygame.math import Vector2
import sys
import math
import random

pygame.init()

WIN_WIDTH = 400
WIN_HEIGHT = 688

CLOCK = pygame.time.Clock()
FPS = 60

SCREEN = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
pygame.display.set_caption('Blob Shooter!')
EYECON = pygame.image.load('eyecon.png')
pygame.display.set_icon(EYECON)

SCORE = 0
COINS = 999
LIFE = 100
#colors
WHITE = (255,255,255)
GRAY = (150,150,150)
TURQUOISE = (0,168,243)
INDIGO = (63,72,204)
CYAN = (0,255,255)

class Base(pygame.sprite.Sprite):
    def __init__(self,base_image,pos):
        super().__init__()
        self.original_image = base_image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (pos)
        
    def rotate(self,angle):
        self.image = pygame.transform.rotate(self.original_image,angle)
        x,y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

class Cannon(pygame.sprite.Sprite):
    def __init__(self, cannon_image, base_image, cannonBall_image,all_sprites, cannonBall_sprites,fire_sound):
        super().__init__()
        self.status_images = cannon_image
        self.original_image = self.status_images[0]
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (200,631)

        self.angle = 0
        self.fireAngle = 90
        self.rotSpeed = 0
        self.fireCooldown = 500
        self.is_aiming = False
        self.is_firing = False
        self.knockbackStrength = 1
        self.lastFire = pygame.time.get_ticks()
        
        self.all_sprites = all_sprites
        self.cannonBall_sprites = cannonBall_sprites
        self.cannonBall_image = cannonBall_image
        self.fire_sound = fire_sound

        self.base = Base(base_image,(200,631))
        self.all_sprites.add(self.base)
        
    def update(self):
        self.rotSpeed = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rotSpeed = 2
            self.is_aiming = True
            if self.is_firing:
                self.original_image = self.status_images[2]
            if self.is_aiming and not self.is_firing:
                self.original_image = self.status_images[1]
        if keys[pygame.K_RIGHT]:
            self.rotSpeed = -2
            self.is_aiming = True
            if self.is_firing:
                self.original_image = self.status_images[2]
            if self.is_aiming and not self.is_firing:
                self.original_image = self.status_images[1]
        if keys[pygame.K_SPACE]:
            self.is_firing = True
            self.original_image = self.status_images[2]
            self.fire()

        self.rotate() #also aim

        if not self.is_aiming and not self.is_firing:
            self.original_image = self.status_images[0]
           
    def rotate(self):
        self.angle += self.rotSpeed % 360
        self.fireAngle += self.rotSpeed
        if self.angle % 360 == 62:
            self.angle = 60
            self.fireAngle = 150
        elif self.angle % 360 == 298:
            self.angle = 300
            self.fireAngle = 30
        self.base.rotate(self.angle)
        self.image = pygame.transform.rotate(self.original_image,self.angle)
        x,y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def fire(self):
        #self.fire_sound.play()
        current_time = pygame.time.get_ticks()
        if current_time - self.lastFire > self.fireCooldown:
            self.lastFire = current_time
            cannonBall = CannonBall(self.cannonBall_image,self.angle,-self.fireAngle)
            self.all_sprites.add(cannonBall)
            self.cannonBall_sprites.add(cannonBall)

    def knockback(self):
        pass #cause of the physics involved and why the base of the cannon is on a separate image

class Blob(pygame.sprite.Sprite):
    def __init__(self,blob_types,hit_sound,all_sprites,blob_sprites):
        super().__init__()
        self.key = random.choice(list(blob_types.keys()))
        self.image = blob_types[self.key][0]
        self.original_image = self.image
        self.rect = self.image.get_rect()     
        self.startingY = -750
        self.posX = random.randint(10,WIN_WIDTH)
        self.posY = random.randint(self.startingY, -100)
        self.posXY = (self.posX,self.posY)
        self.rect = self.image.get_rect(center = (self.posX,self.posY))
        self.pos = Vector2(self.posXY)

        self.popAnimation = blob_types[self.key][1]
        self.popSound = blob_types[self.key][2]
        self.hitPoints = blob_types[self.key][3]
        self.scoreValue = blob_types[self.key][4]
        self.speed = blob_types[self.key][5]
        self.is_hit = False   

        self.hit_sound = hit_sound
        self.blob_types = blob_types
        self.all_sprites = all_sprites
        self.blob_sprites = blob_sprites

    def update(self):
        if self.is_hit:
            self.hit_sound.play()
            self.is_hit = False
            
        self.pos += Vector2(0,self.speed)
        self.rect.center = self.pos

        if self.hitPoints == 0:
            self.kill()
            self.explode_and_spawn()

        if self.rect.bottom >= WIN_HEIGHT - 55:
            global LIFE
            LIFE -= self.hitPoints * 6
            self.scoreValue = 0
            self.kill()
            self.explode_and_spawn()

    def explode_and_spawn(self):
        global SCORE
        self.popSound.play()
        SCORE += self.scoreValue
        pop = Explode(self.rect.center,self.popAnimation)
        self.all_sprites.add(pop)
        new_blob = Blob(self.blob_types,self.hit_sound,self.all_sprites,self.blob_sprites)
        self.all_sprites.add(new_blob)
        self.blob_sprites.add(new_blob)

class CannonBall(pygame.sprite.Sprite):
    def __init__(self,cannonBall_image,rot_angle,fire_angle):
        super().__init__()
        self.original_image = cannonBall_image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.radius = 105
        self.pos_X = 200
        self.pos_Y = 633
        self.cannonBallSpeed = 5
        self.rot_angle = rot_angle
        self.starting_X = self.pos_X + math.cos(math.radians(fire_angle)) * self.radius
        self.starting_Y = self.pos_Y + math.sin(math.radians(fire_angle)) * self.radius
        self.change_in_X = self.cannonBallSpeed * math.cos(math.radians(fire_angle))
        self.change_in_Y = self.cannonBallSpeed * math.sin(math.radians(fire_angle))
        self.rect = self.image.get_rect(center = (self.starting_X,self.starting_Y))
        self.pos = Vector2((self.starting_X,self.starting_Y))

    def rotate(self):
        self.image = pygame.transform.rotate(self.original_image,self.rot_angle)
        x,y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        
    def update(self):
        self.rotate()
        self.pos += (self.change_in_X,self.change_in_Y)
        self.rect.center = self.pos
        if self.rect.bottom <= 0 or self.rect.right <= 0 or self.rect.left >= WIN_WIDTH:
            self.kill()

class Explode(pygame.sprite.Sprite):
    def __init__(self,center, pop_animation):
        super().__init__()
        self.pop_animation = pop_animation
        self.image = pop_animation[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_rate:
            self.last_update = current_time
            self.frame += 1
            if self.frame == len(self.pop_animation):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.pop_animation[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Hit(pygame.sprite.Sprite):
    def __init__(self,center,rot_angle,hit_animation):
        super().__init__()
        self.hit_animation = hit_animation
        self.image = hit_animation[0]
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 25
        self.rot_angle = rot_angle

    def rotate(self):
        self.image = pygame.transform.rotate(self.original_image,self.rot_angle)
        x,y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_rate:
            self.last_update = current_time
            self.frame += 1
            if self.frame == len(self.hit_animation):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.hit_animation[self.frame]
                self.original_image = self.image
                self.rect = self.image.get_rect()
                self.rect.center = center
                self.rotate()

def Button():
    pass

def Text(screen, text, size, pos, font,color, align):
    font = pygame.font.Font(pygame.font.match_font(font),size)
    text_surf = font.render(text,True,color)
    text_rect = text_surf.get_rect()
    if align == 'topleft':
        text_rect.topleft = pos
    elif align == 'midtop':
        text_rect.midtop = pos
    elif align == 'topright':
        text_rect.topright = pos
    else:
        text_rect = pos
    screen.blit(text_surf, text_rect)

def Menu():
    pass
                               
def main():
    global LIFE, COINS
    #Sprite groups
    activeSprites = pygame.sprite.Group()
    playerCannon = pygame.sprite.Group()
    blobs = pygame.sprite.Group()
    cannonBalls = pygame.sprite.Group()
    maxBlob = 10
    Pause = False
    gameOver = False
    
    #Play music on loop and load sounds
    pygame.mixer.music.load('musicSFX/bg_music.mp3')
    pygame.mixer.music.play(-1)
    fireSound = None #pygame.mixer.Sound('musicSFX/fire.wav')

    #Load/create images & sounds
    blobImages = list()
    cannonStatusImages = list()
    hitAnimation = list()
    popSounds = list()
    hitSound = pygame.mixer.Sound('musicSFX/hit0.wav')
    popAnimations = {'smallPop':list(),'mediumPop':list(),'largePop':list()}
    bgImage = pygame.image.load('Background/Background.png')
    pauseBG = pygame.image.load('Background/pauseBG.png')
    textBG = pygame.image.load('Background/TextBG0.png')
    turquoiseBG = pygame.Surface((400,650))
    turquoiseBG.set_alpha(128)
    turquoiseBG.fill(TURQUOISE)
    cannonLifeImage = pygame.image.load('Cannon/Life0.png')
    coinImage = pygame.image.load('Cannon/Coin.png')
    pauseImage = pygame.image.load('Button/Pause.png')
    cannonBaseImage = pygame.image.load("Cannon/Base.png")
    cannonBallImage = pygame.image.load("Cannon/cannonBall0.png")

    for i in range(3):
        cannonPthImg = 'Cannon/cannon ({0}).png'.format(i)
        cannonStatusImages.append(pygame.image.load(cannonPthImg))      
    for i in range(3):
        blobPthImg = 'Enemy/blob{0}.png'.format(i)
        popPthSound = 'musicSFX/pop{0}.wav'.format(i)
        blobImages.append(pygame.image.load(blobPthImg))
        popSounds.append(pygame.mixer.Sound(popPthSound))
        
    for i in range(6):
        smallpopPthImg = 'Enemy/Blob1Pop/smallPop{0}.png'.format(i)
        mediumpopPthImg = 'Enemy/Blob2Pop/mediumPop{0}.png'.format(i)
        largepopPthImg = 'Enemy/Blob3Pop/largePop{0}.png'.format(i)
        ballHitPthImg = 'Cannon/cannonball hit/ballHit{0}.png'.format(i)
        smallPopImg = pygame.image.load(smallpopPthImg)
        mediumPopImg = pygame.image.load(mediumpopPthImg)
        largePopImg = pygame.image.load(largepopPthImg)
        ballHitImg = pygame.image.load(ballHitPthImg)
        popAnimations['smallPop'].append(smallPopImg)
        popAnimations['mediumPop'].append(mediumPopImg)
        popAnimations['largePop'].append(largePopImg)
        hitAnimation.append(ballHitImg)

    #blobs >> type: [image, popAnimation, popSound,hp, scoreValue, speed] 
    blobsType = {'smallBlob' :[blobImages[0], popAnimations['smallPop'], popSounds[0], 1, 3, 1.2],
                 'mediumBlob':[blobImages[1], popAnimations['mediumPop'],popSounds[1], 2, 6, 0.9],
                 'largeBlob' :[blobImages[2], popAnimations['largePop'], popSounds[2], 3, 9, 0.6]}

    cannon = Cannon(cannonStatusImages,cannonBaseImage,cannonBallImage,activeSprites,cannonBalls,fireSound)
    activeSprites.add(cannon)
    
    for b in range(maxBlob):
        blob = Blob(blobsType,hitSound,activeSprites,blobs)
        activeSprites.add(blob)
        blobs.add(blob)

    #mainloop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not gameOver:
                    if event.key == pygame.K_p:
                        if not Pause:
                            Pause = True
                            pygame.mixer.music.pause()
                        else:
                            Pause = False
                            pygame.mixer.music.unpause()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    cannon.is_firing = False
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    cannon.is_aiming = False

        if not Pause and not gameOver:

            SCREEN.blit(bgImage,(0,0))
            activeSprites.update()

            blobCollide = pygame.sprite.groupcollide(blobs,cannonBalls,False,pygame.sprite.collide_circle)
            for collide in blobCollide:
                hit = Hit(blobCollide[collide][0].rect.center, blobCollide[collide][0].rot_angle, hitAnimation)
                activeSprites.add(hit)
                collide.is_hit = True
                collide.hitPoints -= 1

            activeSprites.draw(SCREEN)

            if LIFE <= 0:
                LIFE = 0
                gameOver = True

            SCREEN.blit(textBG,(0,0))
            SCREEN.blit(pauseImage,(345,3))
            
            Text(SCREEN,'{:09}'.format(SCORE), 20, (25,-2),'bevan',CYAN,'topleft')
            SCREEN.blit(coinImage,(165,3))
            Text(SCREEN,str(COINS), 20, (195,-2),'bevan',WHITE,'topleft')
            SCREEN.blit(cannonLifeImage,(255,3))
            Text(SCREEN,str(LIFE), 20,(285,-2),'bevan',WHITE,'topleft')         

        if Pause:
            SCREEN.blit(pauseBG,(0,270))
            Text(SCREEN,"Paused!", 50,(200,270),'bevan',WHITE,'midtop')
            Text(SCREEN,"Press 'p' to continue", 15, (200,340),'bevan',WHITE,'midtop')

        if gameOver:
            Text(SCREEN,"Game Over!", 25, (200,250), 'bevan', WHITE,'midtop')          

        CLOCK.tick(FPS)
        pygame.display.flip()

if __name__ == "__main__":
    main()

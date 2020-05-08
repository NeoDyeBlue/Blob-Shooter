import pygame
from pygame import *
from pygame.math import Vector2
import sys
import math
import random
import pickle

pygame.mixer.pre_init(44100, -16, 1, 512) #frequency, size, channels, buffer (for fixing sound delays)
pygame.init()

WIN_WIDTH = 400
WIN_HEIGHT = 688

CLOCK = pygame.time.Clock()
FPS = 60

SCREEN = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
pygame.display.set_caption('Blob Shooter!')

EYECON = pygame.image.load('eyecon.png')
pygame.display.set_icon(EYECON)
pygame.mouse.set_visible(True)
MOUSE = pygame.image.load('cursor.png').convert_alpha()
MOUSE_rect = MOUSE.get_rect()

bestScore = 0
        
#colors
WHITE = (255,255,255)
GRAY = (150,150,150)
TURQUOISE = (0,168,243)
INDIGO = (63,72,204)
CYAN = (0,255,255)
AQUA = (140,255,251)
BLACK = (0,0,0)
RED = (200,0,40)
YELLOW = (255,242,0)

class Cannon(pygame.sprite.Sprite):
    def __init__(self, cannon_image, cannonBall_image,all_sprites, cannonBall_sprites,fire_sound):
        super().__init__()
        self.status_images = cannon_image
        self.original_image = self.status_images[0]
        self.image = self.original_image
        self.centerPos = (200,631)
        self.rect = self.image.get_rect(center = self.centerPos)
        self.pos = Vector2(self.centerPos)

        self.hitPoints = 100
        self.coins = 0
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
            if self.hitPoints <= 20:
                self.original_image = self.status_images[3]
            else:
                self.original_image = self.status_images[0]
           
    def rotate(self):
        self.angle += self.rotSpeed % 360
        self.fireAngle += self.rotSpeed
        if self.angle % 360 == 82:
            self.angle = 80
            self.fireAngle = 170
        elif self.angle % 360 == 278:
            self.angle = 280
            self.fireAngle = 10
            
        self.image = pygame.transform.rotate(self.original_image,self.angle)
        x,y = self.rect.center
        self.pos = ((x,y))
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos)

    def fire(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.lastFire > self.fireCooldown:
            self.fire_sound.play()
            self.lastFire = current_time
            cannonBall = CannonBall(self.cannonBall_image,self.angle,-self.fireAngle)
            self.all_sprites.add(cannonBall)
            self.cannonBall_sprites.add(cannonBall)

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
        self.rect = self.image.get_rect(center = (self.posX,self.posY))
        self.pos = Vector2((self.posX, self.posY))

        self.popAnimation = blob_types[self.key][1]
        self.hitImg = blob_types[self.key][2]
        self.popSound = blob_types[self.key][3]
        self.popSound.set_volume(0.3)
        self.hitPoints = blob_types[self.key][4]
        self.scoreValue = blob_types[self.key][5]
        self.speed = blob_types[self.key][6]
        self.is_hit = False
        self.hitDuration = 5

        self.hit_sound = hit_sound
        self.hit_sound.set_volume(0.1)
        self.blob_types = blob_types
        self.all_sprites = all_sprites
        self.blob_sprites = blob_sprites

    def update(self):
        if self.is_hit:
            self.flash()
            
        self.pos += Vector2(0,self.speed)
        self.rect.center = self.pos

        if self.hitPoints <= 0:
            self.kill()
            self.popSound.play()

    def flash(self):
        self.image = self.hitImg
        self.hitDuration -= 1
        if self.hitDuration <= 0:
            self.hit_sound.play()
            self.image = self.original_image
            self.is_hit = False
            self.hitDuration = 5

class Boss(pygame.sprite.Sprite):
    def __init__(self,image,all_sprites,blob_sprites):
        super().__init__()

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

class BlobCloud(pygame.sprite.Sprite):
    def __init__(self, image, cloud_sprites):
        super().__init__()
        self.cloud_images = image
        self.original_image = random.choice(self.cloud_images)
        self.image = self.original_image
        self.startingX = 500
        self.posX = random.randint(self.startingX,600)
        self.posY = random.randint(10,300)
        self.rect = self.image.get_rect(center = (self.posX,self.posY))
        self.rotPos = Vector2((self.posX,self.posY))
        self.pos = Vector2((self.posX,self.posY))
        self.angle = random.randint(0,360)

        self.speed = random.uniform(-2,-0.6)
        self.cloud_sprites = cloud_sprites

    def update(self):
        self.angle += 1 % 360
        self.image = pygame.transform.rotate(self.original_image,self.angle)
        x,y = self.rect.center
        self.rect = self.image.get_rect()
        self.rotPos = Vector2(x,y)
        self.rect.center = self.rotPos
        self.pos += Vector2(self.speed,0)
        self.rect.center = self.pos

        if self.rect.right <= 0:
            self.kill()
            cloud = BlobCloud(self.cloud_images, self.cloud_sprites)
            self.cloud_sprites.add(cloud)

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

class Base(pygame.sprite.Sprite):
    def __init__(self,image,pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = pos

    def update(self):
        self.rect.center = self.pos
        
class Button:
    def __init__(self, image,higlight, pos):
        self.image = image
        self.highlight_image = higlight
        self.original_image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.bloopSound = pygame.mixer.Sound('musicSFX/bloop0.wav')

    def draw_and_check(self,screen):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image = self.highlight_image
        else:
            self.image = self.original_image
        screen.blit(self.image,self.rect)

    def is_clicked(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.bloopSound.play()
                    return True

def draw_text(screen, text, size, pos, font,color, align):
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

def yes_or_no(text):
    pass

def pause_menu():
    transparentBG = pygame.Surface((400,688))
    transparentBG.set_alpha(25)
    transparentBG.fill(INDIGO)

    resumeImage = pygame.image.load('Button/Resume.png').convert_alpha()
    resumeHLimage = pygame.image.load('Button/ResumeHL.png').convert_alpha()
    menuImage = pygame.image.load('Button/Menu.png').convert_alpha()
    menuHLimage = pygame.image.load('Button/MenuHL.png').convert_alpha()

    SCREEN.blit(transparentBG,(0,0))

    draw_text(SCREEN,"Pause", 60,(200,240),'bevan',WHITE,'midtop')

    resumeButton = Button(resumeImage,resumeHLimage,(140,365))
    menuButton = Button(menuImage,menuHLimage,(260,365))

    paused = True
    while paused:
        event = pygame.event.poll() #single events only
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False

        if resumeButton.is_clicked(event):
            return False

        if menuButton.is_clicked(event):
            return True

        #SCREEN.fill(CYAN)
        
        resumeButton.draw_and_check(SCREEN)
        menuButton.draw_and_check(SCREEN)

        #MOUSE_rect = pygame.mouse.get_pos()
        #SCREEN.blit(MOUSE,MOUSE_rect)

        CLOCK.tick(FPS)
        pygame.display.flip()

def game_over(score_after, coins_left):
    global bestScore
    restartImg = pygame.image.load('Button/Restart.png').convert_alpha()
    restartImgHL = pygame.image.load('Button/RestartHL.png').convert_alpha()
    menu2Img = pygame.image.load('Button/Menu2.png').convert_alpha()
    menu2ImgHL = pygame.image.load('Button/Menu2HL.png').convert_alpha()
    gameOverBG = pygame.image.load('Background/GameOverBG.png').convert_alpha()
    transparentBG = pygame.Surface((400,688))
    transparentBG.set_alpha(25)
    transparentBG.fill(RED)
    scoreColor = WHITE

    pygame.mixer.music.load('musicSFX/over_music.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)

    restartButton = Button(restartImg,restartImgHL,(140,435))
    menu2Button = Button(menu2Img, menu2ImgHL, (260,435))

    SCREEN.blit(transparentBG,(0,0))
    SCREEN.blit(gameOverBG,(15,145))

    if score_after + coins_left > bestScore:
        bestScore = score_after + coins_left
        draw_text(SCREEN,'New!'.format(coins_left), 20, (100, 280), 'bevan', YELLOW, 'midtop')
        
        with open('bestScore.dat','wb') as file:
            pickle.dump(bestScore,file)

    draw_text(SCREEN,'{:09}'.format(score_after + coins_left),40,(200,290),'bevan',WHITE,'midtop')
    draw_text(SCREEN,'+{0}'.format(coins_left), 35, (200, 340), 'bevan', WHITE, 'midtop')
            
    over = True
    while over:
        event = pygame.event.poll()
        if event.type == QUIT:
            over = False
            pygame.quit()
            sys.exit()

        if restartButton.is_clicked(event):
            pygame.mixer.music.stop()
            over = False
            main_game()

        if menu2Button.is_clicked(event):
            pygame.mixer.music.stop()
            over = False
            main_menu()

        restartButton.draw_and_check(SCREEN)
        menu2Button.draw_and_check(SCREEN)

        CLOCK.tick(FPS)
        pygame.display.flip()
    
def main_menu():
    global bestScore
    cloudSprites = pygame.sprite.Group()
    blobClouds = list()
    
    try:
        with open("bestScore.dat", 'rb') as scoreFile:
            bestScore = pickle.load(scoreFile)
    except:
        pass
    
    pygame.mixer.music.load('musicSFX/menu_music.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)
    menuBG = pygame.image.load('Background/MenuBG.png').convert_alpha()
    titleImg = pygame.image.load('Background/Title.png').convert_alpha()
    playImg = pygame.image.load('Button/Play.png').convert_alpha()
    playImgHL = pygame.image.load('Button/PlayHL.png').convert_alpha()
    quitImg = pygame.image.load('Button/Quit.png').convert_alpha()
    quitImgHL = pygame.image.load('Button/QuitHL.png').convert_alpha()
    
    playButton = Button(playImg,playImgHL,(200,480))
    quitButton = Button(quitImg,quitImgHL,(40,640))

    for i in range(3):
        cloudPthImg = 'Enemy/blob{0}.png'.format(i)
        cloudImg = pygame.image.load(cloudPthImg)
        blobClouds.append(cloudImg)

    for i in range(3):
        blobCloud = BlobCloud(blobClouds,cloudSprites)
        cloudSprites.add(blobCloud)

    in_menu = True
    while in_menu:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            in_menu = False
            pygame.quit()
            sys.exit()
            
        if quitButton.is_clicked(event):
            in_menu = False
            pygame.quit()
            sys.exit()

        if playButton.is_clicked(event):
            pygame.mixer.music.fadeout(1500)
            pygame.time.delay(1500)            
            pygame.mixer.music.stop()
            in_menu = False
            main_game()

        cloudSprites.update()    

        SCREEN.fill(AQUA)

        cloudSprites.draw(SCREEN)
        
        SCREEN.blit(menuBG,(0,0))
        SCREEN.blit(titleImg,(35,30))

        playButton.draw_and_check(SCREEN)
        quitButton.draw_and_check(SCREEN)

        draw_text(SCREEN,"Current Best:", 20, (200,570), 'bevan', WHITE,'midtop')
        draw_text(SCREEN,'{:09}'.format(bestScore), 25, (200,595), 'bevan', WHITE,'midtop')
        #MOUSE_rect = pygame.mouse.get_pos()
        #SCREEN.blit(MOUSE,MOUSE_rect)
        
        CLOCK.tick(FPS)
        pygame.display.flip()

def shop_menu(player):
    shopBG = pygame.image.load('Background/ShopBG.png').convert()

    in_shop = True
    while in_shop:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            in_shop = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                in_shop = False
                return

        SCREEN.blit(shopBG,(0,0))

        CLOCK.tick(FPS)
        pygame.display.flip()

def main_game():
    #Sprite groups
    activeSprites = pygame.sprite.Group()
    blobs = pygame.sprite.Group()
    cannonBalls = pygame.sprite.Group()
    
    #necessary vars
    maxBlob = 10
    score = 0
    killCount = 0
    
    #Play music on loop
    pygame.mixer.music.load('musicSFX/game_music.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)

    #button images
    pauseImage = pygame.image.load('Button/Pause0.png').convert_alpha()
    pauseHLimage = pygame.image.load('Button/PauseHL0.png').convert_alpha()
    shopImage = pygame.image.load('Button/Shop2.png').convert_alpha()
    shopHLimage = pygame.image.load('Button/ShopHL2.png').convert_alpha()

    #Load/create images & sounds
    blobImages = list()
    blobHitImages = list()
    cannonStatusImages = list()
    hitAnimation = list()
    popSounds = list()
    popAnimations = {'smallPop':list(),'mediumPop':list(),'largePop':list()}
    bgImage = pygame.image.load('Background/Background.png').convert_alpha()
    textBG = pygame.image.load('Background/TextBG0.png').convert_alpha()
    cannonLifeImage = pygame.image.load('Cannon/Life0.png').convert_alpha()
    coinImage = pygame.image.load('Cannon/Coin.png').convert_alpha()
    cannonBallImage = pygame.image.load("Cannon/cannonBall0.png").convert_alpha()

    transparentBase = pygame.Surface((400,62))
    transparentBase.set_alpha(0)
    transparentBase.fill(WHITE)

    hitSound = pygame.mixer.Sound('musicSFX/hit0.wav')
    fireSound = pygame.mixer.Sound('musicSFX/fire0.wav')

    #append images to their list
    for i in range(4):
        cannonPthImg = 'Cannon/cannon ({0}).png'.format(i)
        cannonStatusImages.append(pygame.image.load(cannonPthImg).convert_alpha())     
    for i in range(3):
        blobPthImg = 'Enemy/blob{0}.png'.format(i)
        blobHitPthImg = 'Enemy/blob{0}hit.png'.format(i)
        popPthSound = 'musicSFX/pop{0}.wav'.format(i)
        blobImages.append(pygame.image.load(blobPthImg).convert_alpha())
        popSounds.append(pygame.mixer.Sound(popPthSound))
        blobHitImages.append(pygame.image.load(blobHitPthImg).convert_alpha())

    #animations
    for i in range(6):
        smallpopPthImg = 'Enemy/Blob1Pop/smallPop{0}.png'.format(i)
        mediumpopPthImg = 'Enemy/Blob2Pop/mediumPop{0}.png'.format(i)
        largepopPthImg = 'Enemy/Blob3Pop/largePop{0}.png'.format(i)
        ballHitPthImg = 'Cannon/cannonBallHit/ballHit{0}.png'.format(i)
        smallPopImg = pygame.image.load(smallpopPthImg).convert_alpha()
        mediumPopImg = pygame.image.load(mediumpopPthImg).convert_alpha()
        largePopImg = pygame.image.load(largepopPthImg).convert_alpha()
        ballHitImg = pygame.image.load(ballHitPthImg).convert_alpha()
        popAnimations['smallPop'].append(smallPopImg)
        popAnimations['mediumPop'].append(mediumPopImg)
        popAnimations['largePop'].append(largePopImg)
        hitAnimation.append(ballHitImg)

    #blob's Type: [image, popAnimation, popSound,hp, scoreValue, speed] 
    blobsType = {'smallBlob' :[blobImages[0], popAnimations['smallPop'], blobHitImages[0],popSounds[0], 1, 3, 1.2],
                 'mediumBlob':[blobImages[1], popAnimations['mediumPop'],blobHitImages[1],popSounds[1], 2, 6, 0.9],
                 'largeBlob' :[blobImages[2], popAnimations['largePop'], blobHitImages[2],popSounds[2], 3, 9, 0.6]}

    cannon = Cannon(cannonStatusImages,cannonBallImage,activeSprites,cannonBalls,fireSound)
    activeSprites.add(cannon)
    
    for b in range(maxBlob):
        blob = Blob(blobsType,hitSound,activeSprites,blobs)
        activeSprites.add(blob)
        blobs.add(blob)

    base = Base(transparentBase,(200,658))
    activeSprites.add(base)

    pauseButton = Button(pauseImage,pauseHLimage,(360,15))
    shopButton = Button(shopImage,shopHLimage,(335,658))

    pause = False
    gameOver = False
    to_menu = False
    to_shop = False

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
                        pause = True
                        
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    cannon.is_firing = False
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    cannon.is_aiming = False

            if pauseButton.is_clicked(event):
                if not gameOver:
                    pause = True

            if shopButton.is_clicked(event):
                to_shop = True
                

        if not pause and not gameOver:
            SCREEN.blit(bgImage,(0,0))
            activeSprites.update()

            blobCollide = pygame.sprite.groupcollide(blobs,cannonBalls,False,pygame.sprite.collide_circle)
            for collide in blobCollide:
                hit = Hit(blobCollide[collide][0].rect.center, blobCollide[collide][0].rot_angle, hitAnimation)
                activeSprites.add(hit)
                collide.is_hit = True
                collide.hitPoints -= 1
                if collide.hitPoints <= 0:
                    score += collide.scoreValue
                    pop = Explode(collide.rect.center,collide.popAnimation)
                    activeSprites.add(pop)
                    new_blob = Blob(blobsType,hitSound,activeSprites,blobs)
                    activeSprites.add(new_blob)
                    blobs.add(new_blob)

            baseCollide = pygame.sprite.spritecollide(base,blobs,True)
            for collide in baseCollide:
                cannon.hitPoints -= collide.hitPoints * 6
                collide.popSound.play()
                pop = Explode(collide.rect.center,collide.popAnimation)
                activeSprites.add(pop)
                new_blob = Blob(blobsType,hitSound,activeSprites,blobs)
                activeSprites.add(new_blob)
                blobs.add(new_blob)

            activeSprites.draw(SCREEN)

            if cannon.hitPoints <= 0:
                cannon.hitPoints = 0
                if cannon.hitPoints == 0 and not pop.alive():
                    pygame.mixer.music.stop()
                    gameOver = True

            SCREEN.blit(textBG,(0,0))
            pauseButton.draw_and_check(SCREEN)
            shopButton.draw_and_check(SCREEN)
            
            draw_text(SCREEN,'{:09}'.format(score), 20, (25,-2),'bevan',CYAN,'topleft')
            SCREEN.blit(cannonLifeImage,(165,3))
            draw_text(SCREEN,str(cannon.hitPoints), 20, (195,-2),'bevan',WHITE,'topleft')
            SCREEN.blit(coinImage,(255,3))
            draw_text(SCREEN,str(cannon.coins), 20,(285,-2),'bevan',WHITE,'topleft')         

        if pause:
            running = False
            pygame.mixer.music.pause()
            to_menu = pause_menu()
            if to_menu:
                pygame.mixer.music.stop()
                main_menu()
            if not to_menu:
                pause = False
                running = True
                pygame.mixer.music.unpause()

        if gameOver:
            running = False
            game_over(score,cannon.coins)

        if to_shop:
            running = False
            pygame.mixer.music.pause()
            shop_menu(cannon)
            to_shop = False
            running = True
            pygame.mixer.music.unpause()

        #MOUSE_rect = pygame.mouse.get_pos()
        #SCREEN.blit(MOUSE,MOUSE_rect)

        CLOCK.tick(FPS)
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()

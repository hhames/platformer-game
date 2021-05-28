# Imports
import pygame
import random
import json


# Window settings
GRID_SIZE = 64
WIDTH = 24 * GRID_SIZE
HEIGHT = 12 * GRID_SIZE
TITLE = "Game Title"
FPS = 60


# Create window
pygame.init()
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()


# Define colors
WHITE = (255, 255, 255)
TTL_GRAY = (196, 196, 196)
BLACK = (0, 0, 0)
SKY_BLUE = (0, 150, 255)
GRAY = (175,175,175)
#stages
START = 0
PLAYING = 1
LOSE = 2
LEVEL_COMPLETE = 3
WIN = 4
# Load fonts
font_xxs = pygame.font.Font(None, 14)
font_xs = pygame.font.Font('assets/fonts/Dinomouse-Regular.otf', 27)
font_md = pygame.font.Font('assets/fonts/Dinomouse-Regular.otf', 40)
font_xl = pygame.font.Font('assets/fonts/Dinomouse-Regular.otf', 120)
# Load images
hero_idle_imgs_rt = [pygame.image.load('assets/images/characters/player_idle.png').convert_alpha()]
hero_walk_imgs_rt = [pygame.image.load('assets/images/characters/player_walk1.png').convert_alpha(),
                  pygame.image.load('assets/images/characters/player_walk2.png').convert_alpha()]
hero_jump_imgs_rt = [pygame.image.load('assets/images/characters/player_jump.png').convert_alpha()]

hero_idle_imgs_lt = [pygame.transform.flip(img, True, False)for img in hero_idle_imgs_rt]
hero_walk_imgs_lt = [pygame.transform.flip(img, True, False)for img in hero_walk_imgs_rt]
hero_jump_imgs_lt = [pygame.transform.flip(img, True, False)for img in hero_jump_imgs_rt]
grass_dirt_img = pygame.image.load('assets/images/tiles/grass_dirt.png').convert_alpha()
platform_img = pygame.image.load('assets/images/tiles/block.png').convert_alpha()
blockback_img = pygame.image.load('assets/images/tiles/blockback.png').convert_alpha()
bush_img = pygame.image.load('assets/images/tiles/bush.png').convert_alpha()
brick_img = pygame.image.load('assets/images/tiles/brickGrey.png').convert_alpha()
cstl_back_img = pygame.image.load('assets/images/tiles/stone_back.png').convert_alpha()
torch_img = pygame.image.load('assets/images/tiles/torch1.png').convert_alpha()
stone_img = pygame.image.load('assets/images/tiles/stone.png').convert_alpha()
heart_img = pygame.image.load('assets/images/items/heart.png').convert_alpha()
gem_img = pygame.image.load('assets/images/items/gem.png').convert_alpha()
dirt_img = pygame.image.load('assets/images/tiles/dirt.png').convert_alpha()

wasp_imgs_rt = [pygame.image.load('assets/images/characters/bee.png').convert_alpha(),
             pygame.image.load('assets/images/characters/bee_move.png').convert_alpha()]
wasp_imgs_lt = [pygame.transform.flip(img, True, False)for img in wasp_imgs_rt]
enemy_imgs = [pygame.image.load('assets/images/characters/saw.png').convert_alpha(),
              pygame.image.load('assets/images/characters/saw_move.png').convert_alpha()]

background_img = pygame.image.load('assets/images/tiles/colored_grass.png').convert_alpha()
flag_img = pygame.image.load('assets/images/tiles/door.png').convert_alpha()
# Load sounds

# LEVELS
levels = ['assets/levels/world-1.json',
          'assets/levels/world-2.json',
          'assets/levels/world-3.json']

#settings
gravity = 1.0
terminal_velocity = 24

# Game classes


class Entity(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image):
        super().__init__()
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x * GRID_SIZE + GRID_SIZE // 2
        self.rect.centery = y * GRID_SIZE + GRID_SIZE // 2

class AnimatedEntity(Entity):
    def __init__(self, x, y, images):
        super().__init__(x, y, images[0])

        self.images = images
        self.image_index = 0
        self.ticks = 0
        self.animation_speed = 10

    def set_image_list(self):
        self.images = self.images
        
    def animate(self):
        self.set_image_list()
        
        self.ticks += 1

        if self.ticks % self.animation_speed == 0:
            self.image_index += 1

            if self.image_index>= len(self.images):
                self.image_index =0
                
            self.image = self.images[self.image_index]        
class Hero(AnimatedEntity):
    
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.speed = 5
        self.jump_power = 15
        self.vx = 0
        self.vy = 0
        self.facing_right = True
        self.jumping = False

        self.gems = 0
        self.hearts = 3
        self.hurt_timer = 0
        self.score = 0

    def move_to(self, x, y):
        self.rect.centerx = x * GRID_SIZE + GRID_SIZE // 2
        self.rect.centery = y * GRID_SIZE + GRID_SIZE // 2
        
    def move_left(self):
        self.vx = -1 * self.speed
        self.facing_right = False
        
    def move_right(self):
        self.vx = self.speed
        self.facing_right = True    
    def stop(self):
        self.vx = 0 
        
    def jump(self):
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 2

        if len(hits) > 0:
            self.vy = -1 * self.jump_power
            self.jumping = True

    def apply_gravity(self):
        self.vy += gravity
        
    def move_and_check_platforms(self):
        self.rect.x += self.vx
        
        hits = pygame.sprite.spritecollide(self, platforms, False)
        
        for hit in hits:
            if self.vx > 0:
               self.rect.right = hit.rect.left
            if self.vx < 0:
                self.rect.left = hit.rect.right


        self.rect.y += self.vy
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hits:
            if self.vy > 0:
               self.rect.bottom = platform.rect.top
               self.jumping = False
            elif self.vy < 0:
                self.rect.top = platform.rect.bottom
                
            self.vy = 0
            
    def check_world_edges(self):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > world_width:
            self.rect.right = world_width


    def check_items(self):
        hits = pygame.sprite.spritecollide(self, items, True)

        for item in hits:
            item.apply(self)

    def check_enemies(self):
        hits = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in hits:
            if self.hurt_timer == 0:
                self.hearts -=1
                self.hurt_timer = 1.0 * FPS
                print(self.hearts)
                print("Oof!")
            if self.rect.x < enemy.rect.x:
                self.vx = -15
            elif self.rect.x > enemy.rect.x:
                self.vx = 15   
            if self.rect.y < enemy.rect.y:
                self.vy = -15
            elif self.rect.y > enemy.rect.y:
                 self.vy = 15

        if self.hurt_timer > 0:
            self.hurt_timer -=1

            if self.hurt_timer < 0:
                self.hurt_timer = 0
    def reached_goal(self):
        return pygame.sprite.spritecollideany (self, goal)
    
    def set_image_list(self):
        if self.facing_right:
            if self.jumping:
                self.images = hero_jump_imgs_rt
            elif self.vx == 0:
                self.images = hero_idle_imgs_rt
            else:
                self.images = hero_walk_imgs_rt
        else:
            if self.jumping:
                self.images = hero_jump_imgs_lt
            elif self.vx == 0:
                self.images = hero_idle_imgs_lt
            else:
                self.images = hero_walk_imgs_lt

    def update (self):
        self.apply_gravity()
        self.check_world_edges()
        self.check_items()
        self.check_enemies()
        self.move_and_check_platforms()
        self.animate()


        
        
class Platform(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Flag(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)



class Background(Entity):

    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        
class Gem(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        
        
    def apply(self, character):
        character.gems += 1
        character.score +=10
        print(character.gems)

class Life(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        

    def apply(self, character):
        character.hearts += 1
        print(character.hearts)

class Enemy(AnimatedEntity):
    
    def __init__(self, x, y, images):
        super().__init__(x, y, images)
        

        self.speed = 2
        self.vx = -1 * self.speed
        self.vy = 0
    def reverse(self):
        self.vx *= -1
        
    def move_and_check_platforms(self):
        self.rect.x += self.vx
        
        hits = pygame.sprite.spritecollide(self, platforms, False)
        
        for hit in hits:
            if self.vx > 0:
               self.rect.right = hit.rect.left
               self.reverse()
            elif self.vx < 0:
                self.rect.left = hit.rect.right
                self.reverse()


        self.rect.y += self.vy
        
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for hit in hits:
            if self.vy > 0:
               self.rect.bottom = hit.rect.top
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom
            self.vy = 0
            
    def check_world_edges(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.reverse()
        elif self.rect.right > world_width:
            self.rect.right = world_width
            self.reverse()

    def check_platform_edges(self):
        self.rect.y +=2
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -=2

        must_reverse = True

        for platform in hits:
            if self.vx < 0 and platform.rect.left <= self.rect.left:
                must_reverse = False
            elif self.vx > 0 and platform.rect.right >= self.rect.right:
                must_reverse = False

        if must_reverse:
            self.reverse()
    def apply_gravity(self):
        self.vy += gravity
        
    def update(self):
        self.apply_gravity()
        self.move_and_check_platforms()
        self.check_world_edges()
        self.check_platform_edges()

class SawBlade(Enemy):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
    def update(self):
        self.apply_gravity()
        self.move_and_check_platforms()
        self.check_world_edges()
        self.check_platform_edges()
        self.animate()
        
class Wasp(Enemy):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def set_image_list(self):
        if self.vx > 0:
            self.images = wasp_imgs_lt
        else:
            self.images = wasp_imgs_rt
    def update(self):
    
        self.move_and_check_platforms()
        self.check_world_edges()
        self.animate()
        
# Helper functions
def show_start_screen():
    text = font_xl.render(TITLE, True, TTL_GRAY)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)


    text = font_md.render("press any key to start" , True, TTL_GRAY)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)
def show_lose_screen():
    text = font_xl.render('GAME OVER' , True, TTL_GRAY)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)


    text = font_md.render("press 'r' to play again" , True, TTL_GRAY)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)
def show_level_complete_screen():
    text = font_xl.render('Level Complete' , True, TTL_GRAY)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2
    screen.blit(text, rect)



def show_hud():
    text = font_md.render(str(hero.score), True, WHITE)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, 16
    screen.blit(text, rect)

    screen.blit(gem_img, [WIDTH -100, 16])
    text = font_md.render('x' + str(hero.gems), True, WHITE) 
    rect = text.get_rect()
    rect.topleft = WIDTH - 60, 24
    screen.blit(text, rect)

    for i in range(hero.hearts):
        x = i * 36 + 16
        y = 16
        screen.blit(heart_img, [x,y])

def draw_grid(offset_x=0, offset_y=0):
    for x in range(0, WIDTH + GRID_SIZE, GRID_SIZE):
        adj_x = x - offset_x % GRID_SIZE
        pygame.draw.line(screen, GRAY, [adj_x, 0], [adj_x, HEIGHT], 1)

    for y in range(0, HEIGHT + GRID_SIZE, GRID_SIZE):
        adj_y = y - offset_y % GRID_SIZE
        pygame.draw.line(screen, GRAY, [0, adj_y], [WIDTH, adj_y], 1)

    for x in range(0, WIDTH + GRID_SIZE, GRID_SIZE):
        for y in range(0, HEIGHT + GRID_SIZE, GRID_SIZE):
            adj_x = x - offset_x % GRID_SIZE + 4
            adj_y = y - offset_y % GRID_SIZE + 4
            disp_x = x // GRID_SIZE + offset_x // GRID_SIZE
            disp_y = y // GRID_SIZE + offset_y // GRID_SIZE
            
            point = '(' + str(disp_x) + ',' + str(disp_y) + ')'
            text = font_xxs.render(point, True, GRAY)
            screen.blit(text, [adj_x, adj_y])

    
#setup

def start_game():
    global hero, stage, current_level

    hero = Hero( 0, 0, hero_idle_imgs_rt)
    stage = START
    current_level = 0
    
def start_level():
    global player, platforms, items, enemies, stage, backgrounds, all_sprites, goal
    global gravity, terminal_velocity
    global world_width,world_height

    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player = pygame.sprite.GroupSingle()
    items = pygame.sprite.Group()
    backgrounds = pygame.sprite.Group()
    goal = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()




    with open(levels[current_level]) as f:
        data = json.load(f)


    world_width = data['width'] * GRID_SIZE
    world_height = data['height']* GRID_SIZE

    hero.move_to(data['start'][0], data['start'][1])
    player.add(hero)

    

    for i, loc in enumerate(data['flag_locs']):
        if i == 0:
            goal.add(Flag(loc[0], loc[1], flag_img) )
    if 'block_locs' in data:
        for loc in data ['block_locs']:
            platforms.add(Platform(loc[0], loc[1], grass_dirt_img))
    if 'bush_locs' in data:
        for loc in data ['bush_locs']:
            backgrounds.add(Background(loc[0], loc[1], bush_img))


    if 'cstl_back_locs' in data:
        for loc in data ['cstl_back_locs']:
            backgrounds.add(Background(loc[0], loc[1], cstl_back_img))
    if 'blockback_locs' in data:       
        for loc in data ['blockback_locs']:
            backgrounds.add(Background(loc[0], loc[1], blockback_img))
    if 'brick_locs' in data:
        for loc in data ['brick_locs']:
            platforms.add(Platform(loc[0], loc[1], brick_img))
          
    if 'platform_locs' in data:   
        for loc in data ['platform_locs']:
            platforms.add(Platform(loc[0], loc[1], platform_img))
    if 'dirt_locs' in data:
        for loc in data ['dirt_locs']:
            platforms.add(Platform(loc[0], loc[1], dirt_img))

    if 'stone_locs' in data:
        for loc in data ['stone_locs']:
            platforms.add(Platform(loc[0], loc[1], stone_img))
        
    if 'gem_locs' in data:
        for loc in data ['gem_locs']:
            items.add(Gem(loc[0], loc[1], gem_img))

    if 'life_locs' in data:
        for loc in data ['life_locs']:
            items.add(Life(loc[0], loc[1], heart_img))
    if 'sawblade_locs' in data:
        for loc in data ['sawblade_locs']:
            enemies.add(SawBlade(loc[0], loc[1], enemy_imgs))
    if 'wasp_locs' in data:
        for loc in data ['wasp_locs']:
            enemies.add(Wasp(loc[0], loc[1], wasp_imgs_lt))


   
    
    gravity = 0.5
    terminal_velocity = 26

    all_sprites.add( backgrounds, platforms, items, enemies, player, goal)
#others
def show_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, [x, 0], [x, HEIGHT],1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, [0, y], [WIDTH, y],1)

    for x in range(0, WIDTH, GRID_SIZE):
        for y in range(0, HEIGHT, GRID_SIZE):
            point = '('+ str(x//64) + "," +str(y//64) + ')'
            text = font_xs.render(point, True, GRAY)
            screen.blit(text, [x + 4, y + 4])
        
#physics settings
gravity = 0.5
# Game loop

running = True
grid_on = False
start_game()
start_level()

while running:
    # Input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                grid_on = not grid_on


            elif stage == START:
                stage = PLAYING

            elif stage == PLAYING:
                if event.key == pygame.K_SPACE:
                    hero.jump()

            elif stage == LOSE or stage == WIN:
                if event.key == pygame.K_r:
                    start_game()
                    start_level()



                
    pressed = pygame.key.get_pressed()

    if pressed[pygame.K_LEFT]:
        hero.move_left()
    elif pressed[pygame.K_RIGHT]:
        hero.move_right()
    else:
        hero.stop()
    
    
    # Game logic
    if stage == PLAYING:
        all_sprites.update()
        if hero.hearts == 0:
            stage = LOSE
        elif hero.reached_goal():
            stage = LEVEL_COMPLETE
            countdown = 2* FPS
    elif stage == LEVEL_COMPLETE:
        countdown -=1
        if countdown <= 0:
            current_level += 1
            
            start_level()
            stage = PLAYING

            
    if hero.rect.centerx < WIDTH // 2:
        offset_x = 0
    elif hero.rect.centerx > world_width - WIDTH // 2:
        offset_x = world_width - WIDTH
    else:
        offset_x = hero.rect.centerx - WIDTH // 2
    
    # Drawing code
    screen.blit(background_img,[0,0])
   
    for sprite in all_sprites:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
        
        show_hud()
    
    if stage == START:
        show_start_screen()
    elif stage == LOSE:
        show_lose_screen()
    elif stage == LEVEL_COMPLETE:
        show_level_complete_screen()
    if grid_on:
        draw_grid(offset_x)

    # Update screen
    pygame.display.update()


    # Limit refresh rate of game loop 
    clock.tick(FPS)


# Close window and quit
pygame.quit()


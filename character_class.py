import pygame
from random import randint
import level_data

pygame.mixer.init()


# load character spritesheet function
def load_spritesheet(name, frames):
    image = pygame.image.load(f'Resources/Char_sprites/{name}')
    end_lst = []
    width = image.get_width() // frames
    height = image.get_height()
    x = 0
    for frame in range(frames):
        frame_surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        frame_surf.blit(image, (x, 0))
        end_lst.append(frame_surf)
        x -= width
    return end_lst


class PlayerChar(pygame.sprite.Sprite):
    def __init__(self, spawnpoint, upgrade=0):
        # initialization
        super().__init__()
        self.timers = {'dash': pygame.time.get_ticks(), 'on_ground': pygame.time.get_ticks(),
                       'current': pygame.time.get_ticks(), 'air_time': pygame.time.get_ticks()}
        self.interactable = []
        self.movement = [0, 0]

        # animation
        self.frame = 0
        self.idle = load_spritesheet('_Idle.png', 10)
        self.run = load_spritesheet('_Run.png', 10)
        self.dash_anim = load_spritesheet('_Dash.png', 2)
        self.fall = load_spritesheet('_Fall.png', 3)
        self.jump = load_spritesheet('_Jump.png', 3)

        # SFX
        self.run_sound = [pygame.mixer.Sound(f'Resources/Sounds/Character/Walk/Walk ({i}).ogg') for i in range(1, 6)]
        self.jump_sound = [pygame.mixer.Sound(f'Resources/Sounds/Character/Jump/Pre Jump/Pre Jump ({i}).wav') for i in
                           range(1, 6)]
        self.dash_sound = None

        # body collisions
        self.image = pygame.Surface.copy(self.idle[0])
        self.rect = self.image.get_rect(topleft=(spawnpoint[0], spawnpoint[1] - 80))

        # states
        self.on_ground = False
        self.dash = False
        self.interaction = False

        # movement parameters
        self.speed = 2
        self.acceleration = 0
        self.gravity_speed = 0
        self.jump_force = -14

        # ability charges
        self.upgrade = upgrade
        self.dash_charges = 2
        self.double_jump_charge = 1

    # applying gravity on player
    def gravity(self):
        if not self.dash:
            self.gravity_speed += 1
            if self.gravity_speed > 5:
                self.gravity_speed = 5
            if self.on_ground:
                self.gravity_speed = 0
            self.rect.y += self.gravity_speed
            self.movement[1] += self.gravity_speed
            self.prevent_collisions('y')

    # applying momentum on player
    def momentum(self):
        if self.acceleration:
            acceleration_coefficient = int(self.acceleration / abs(self.acceleration))
            self.acceleration = abs(self.acceleration) // 4 * 3
            if self.acceleration < 1:
                self.acceleration = 0
            if self.acceleration > 2 and not self.dash:
                self.acceleration = 2
            self.acceleration *= acceleration_coefficient
        self.rect.x += self.acceleration
        self.movement[0] += self.acceleration
        self.prevent_collisions('x')

    # checking for ground collision
    def ground_check(self):
        if self.on_ground:
            self.timers['on_ground'] = pygame.time.get_ticks()

            # abilities cooldown
            self.double_jump_charge = 1
            if self.timers['on_ground'] >= self.timers['air_time'] + 500 and not self.dash:
                self.dash_charges = 2
        else:
            self.timers['air_time'] = pygame.time.get_ticks()

    # checking for inputs
    def char_inputs(self):
        keys = pygame.key.get_pressed()

        # horizontal movement
        if keys[pygame.K_a] and not self.dash:
            self.rect.x -= self.speed
            self.acceleration -= 2.5
            self.movement[0] -= self.speed
        if keys[pygame.K_d] and not self.dash:
            self.rect.x += self.speed
            self.acceleration += 2.5
            self.movement[0] += self.speed
        if keys[pygame.K_LSHIFT] and self.dash_charges and self.timers['dash'] + 200 <= self.timers['current'] and (
                keys[pygame.K_d] or keys[pygame.K_a]) and self.upgrade > 1:
            self.dash = True
            self.timers['dash'] = pygame.time.get_ticks()
            self.dash_charges -= 1
            if keys[pygame.K_a]:
                self.acceleration = -50
            elif keys[pygame.K_d]:
                self.acceleration = 50
        self.prevent_collisions('x')

        # vertical movement
        if keys[pygame.K_SPACE] and any((self.double_jump_charge, self.on_ground)) and not self.dash:
            if self.on_ground or self.timers['on_ground'] + 150 > self.timers['air_time'] and self.movement[1] >= 0:
                self.gravity_speed = self.jump_force
                self.movement[1] = self.gravity_speed
                if self.on_ground:
                    self.jump_sound[randint(0, 4)].play()
            elif not self.on_ground and self.timers['air_time'] >= self.timers['on_ground'] + 400 and self.upgrade > 0:
                self.double_jump_charge -= 1
                self.gravity_speed = self.jump_force - 4
                self.movement[1] = self.gravity_speed
        self.prevent_collisions('y')

        # interaction
        if keys[pygame.K_e] and not any([self.dash, self.interaction]):
            if self.interactable:
                pass
                # self.interactable[0].interact()

    # preventing collisions with floor and walls
    def prevent_collisions(self, axis):
        rect_cop = self.rect.copy()
        self.rect = pygame.Rect(0, 0, 15, 20)
        self.rect.midbottom = rect_cop.midbottom
        collisions = pygame.sprite.spritecollide(self, level_data.level_tile_group, False)
        for collision_tile in collisions:
            # preventing clipping
            if axis == 'x':
                if self.movement[0] > 0:
                    self.movement[0] = collision_tile.rect.right - (self.rect.x - self.movement[0])
                    self.rect.right = collision_tile.rect.left
                if self.movement[0] < 0:
                    self.movement[0] = collision_tile.rect.left - (self.rect.x - self.movement[0])
                    self.rect.left = collision_tile.rect.right
            if axis == 'y':
                if self.movement[1] > 0:
                    self.movement[1] = collision_tile.rect.y - self.rect.top + self.movement[1] - self.rect.height
                    self.rect.bottom = collision_tile.rect.top
                    self.on_ground = True
                if self.movement[1] < 0:
                    self.movement[1] = self.rect.top + self.movement[1] - collision_tile.rect.y
                    self.rect.top = collision_tile.rect.bottom
                    self.gravity_speed = 0
        rect_cop = self.rect.copy()
        self.rect = self.image.get_rect()
        self.rect.midbottom = rect_cop.midbottom
        self.ground_check()

    def update(self):
        self.movement = [0, 0]
        # current time update
        self.timers['current'] = pygame.time.get_ticks()

        # status update
        self.on_ground = False
        if self.timers['current'] >= self.timers['dash'] + 200:
            self.dash = False

        # check for interactable objects nearby
        if pygame.sprite.spritecollideany(self, level_data.interactive_group):
            self.interactable = pygame.sprite.spritecollide(self, level_data.interactive_group, dokill=False)
        else:
            self.interactable = []

        # position update
        self.gravity()
        self.char_inputs()
        self.momentum()

        # animation update
        x_flip = False
        if self.movement[0] < 0:
            x_flip = True

        if self.dash:
            anim_lst = self.dash_anim
        elif self.movement[1] > 0:
            anim_lst = self.fall
        elif self.movement[1] < 0:
            anim_lst = self.jump
        elif self.movement[0] != 0:
            anim_lst = self.run
        else:
            anim_lst = self.idle

        anim_speed = 6
        if self.frame > len(anim_lst) * anim_speed - 1:
            self.frame = 0
        if self.frame % anim_speed == 0:
            self.image = pygame.transform.flip(pygame.Surface.copy(anim_lst[self.frame // anim_speed]), x_flip, False)
        self.frame += 1

        # SFX update
        if self.movement[0] != 0 and not pygame.mixer.get_busy() and self.on_ground and self.frame % (
                anim_speed * 4) == 0:
            self.run_sound[randint(0, 4)].play()
        elif self.movement[0] == 0 and self.movement[1] == 0:
            pygame.mixer.stop()

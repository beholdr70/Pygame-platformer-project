import pygame
from random import randint
import level_data
from math import ceil

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
        self.interactable = []  # list of objects that can be used and in player's reach
        self.movement = [0, 0]  # distance of player's movement in the current frame

        # Animation
        self.anim_speed = 6
        self.frame = 0
        self.idle = load_spritesheet('_Idle.png', 10)
        self.run = load_spritesheet('_Run.png', 10)
        self.dash_anim = load_spritesheet('_Dash.png', 2)
        self.fall = load_spritesheet('_Fall.png', 3)
        self.jump = load_spritesheet('_Jump.png', 3)

        # SFX
        self.run_sound = [pygame.mixer.Sound(f'Resources/Sounds/Character/Walk/Walk ({i}).wav') for i in range(1, 5)]
        self.jump_sound = [pygame.mixer.Sound(f'Resources/Sounds/Character/Jump/Pre Jump/Pre Jump ({i}).wav') for i in
                           range(1, 6)]
        self.dash_sound = None
        self.SFX = pygame.mixer.Channel(3)

        # Player Collision Boxes and Player Image
        self.image = pygame.Surface.copy(self.idle[0])
        self.rect = self.image.get_rect(topleft=(-self.image.get_width(), spawnpoint[1] - 64))

        # Player States
        self.on_ground = False
        self.dash = False
        self.interaction = False

        # Movement Parameters
        self.speed = 1
        self.acceleration = 0
        self.gravity_speed = 0
        self.jump_force = -14

        # Ability Charges
        self.upgrade = upgrade
        self.dash_charges = 1
        self.double_jump_charge = 1

    # applying gravity on player
    def gravity(self):
        if not self.dash:

            # gravity calculation
            self.gravity_speed += 1
            if self.gravity_speed > 5:
                self.gravity_speed = 5
            if self.on_ground:
                self.gravity_speed = 0

            # applying the gravity
            self.rect.y += self.gravity_speed
            self.movement[1] += self.gravity_speed
            self.prevent_collisions('y')

    # applying momentum on player
    def momentum(self):
        move = 0  # final movement variable
        if self.acceleration:

            # acceleration calculations
            acceleration_coefficient = self.acceleration // abs(self.acceleration)  # defining of horizontal direction
            self.acceleration = abs(self.acceleration) - 0.15 * self.speed
            if self.acceleration < 0.1:
                self.acceleration = 0
            if self.acceleration > 3 and not self.dash:
                self.acceleration = 3

            # The whole system with using 'move' variable is necessary
            # because it ensures that the final speed for left and right directions would be identical
            move = ceil(self.acceleration / 2)
            move *= acceleration_coefficient  # applying horizontal direction

            self.acceleration *= acceleration_coefficient

        # applying the acceleration to the player
        self.rect.x += move
        self.movement[0] += move
        self.prevent_collisions('x')

    # updating the variables that depends on ground collision
    def ground_check(self):
        if self.on_ground:

            self.timers['on_ground'] = pygame.time.get_ticks()

            # abilities' charges reset
            self.double_jump_charge = 1
            if self.timers['on_ground'] >= self.timers['air_time'] + 500 and not self.dash:
                self.dash_charges = 2
        else:

            self.timers['air_time'] = pygame.time.get_ticks()

    # checking for inputs
    def char_inputs(self):
        keys = pygame.key.get_pressed()

        # Horizontal Movement

        #  Walk left
        if keys[pygame.K_a] and not self.dash:
            self.rect.x -= self.speed
            self.acceleration -= 0.25 * self.speed
            self.movement[0] -= self.speed

        #  Walk right
        if keys[pygame.K_d] and not self.dash:
            self.rect.x += self.speed
            self.acceleration += 0.25 * self.speed
            self.movement[0] += self.speed

        #  Dash
        if keys[pygame.K_LSHIFT] and self.dash_charges and self.timers['dash'] + 200 <= self.timers['current'] and (
                keys[pygame.K_d] or keys[pygame.K_a]) and self.upgrade > 2:

            self.dash = True
            self.timers['dash'] = pygame.time.get_ticks()
            self.dash_charges -= 1
            if keys[pygame.K_a]:
                self.acceleration = -20
            elif keys[pygame.K_d]:
                self.acceleration = 20

        self.prevent_collisions('x')

        # Vertical Movement

        #  Jump
        if keys[pygame.K_SPACE] and any((self.double_jump_charge, self.on_ground)) and not self.dash:
            if self.on_ground or self.timers['on_ground'] + 150 > self.timers['air_time'] and self.movement[1] >= 0:

                self.gravity_speed = self.jump_force
                self.movement[1] = self.gravity_speed

                # play the jump sound
                if self.on_ground:
                    self.SFX.play(self.jump_sound[randint(0, 4)], fade_ms=100)

            elif not self.on_ground and self.timers['air_time'] >= self.timers['on_ground'] + 400 and self.upgrade > 1:

                self.double_jump_charge -= 1
                self.gravity_speed = self.jump_force
                self.movement[1] = self.gravity_speed

        self.prevent_collisions('y')

        # Interaction
        if keys[pygame.K_e] and not any([self.dash, self.interaction]) and self.on_ground:
            self.interaction = True
            if self.interactable:
                self.interactable[0].interact()
        if not keys[pygame.K_e]:
            self.interaction = False

    # preventing collisions with floor and walls
    def prevent_collisions(self, axis):

        # checking for the collisions
        collisions = pygame.sprite.spritecollide(self, level_data.level_tile_group, False)
        collisions = list(filter(lambda x: x.is_active, list(collisions)))

        for collision_tile in collisions:

            # preventing clipping
            if axis == 'x':

                # Right Side Collision
                if self.movement[0] > 0:
                    self.movement[0] = collision_tile.rect.right + (self.rect.x - self.movement[0])
                    self.rect.right = collision_tile.rect.left

                # Left Side Collision
                if self.movement[0] < 0:
                    self.movement[0] = collision_tile.rect.right + self.movement[0] - self.rect.x
                    self.rect.left = collision_tile.rect.right
            if axis == 'y':

                # Floor Collision
                if self.movement[1] > 0:
                    self.movement[1] = collision_tile.rect.y - self.rect.top + self.movement[1] - self.rect.height
                    self.rect.bottom = collision_tile.rect.top
                    self.on_ground = True

                # Ceil Collision
                if self.movement[1] < 0:
                    self.movement[1] = self.rect.top + self.movement[1] - collision_tile.rect.y
                    self.rect.top = collision_tile.rect.bottom
                    self.gravity_speed = 0

        # update ground related variables
        self.ground_check()

    def interactions_check(self):

        # search for interactive object nearby
        if pygame.sprite.spritecollideany(self, level_data.interactive_group):
            act_checkboxes = list(pygame.sprite.spritecollide(self, level_data.interactive_group, dokill=False))
            self.interactable = list(filter(lambda x: x.activation_type == 'Interaction', act_checkboxes))
            passive_interaction = list(filter(lambda x: x.activation_type == 'Passive', act_checkboxes))
            if passive_interaction:
                for checkbox in passive_interaction:
                    checkbox.interact(self)
        else:
            self.interactable = []

    def accurate_rect(self, is_turned_on):
        if is_turned_on:
            rect_cop = self.rect.copy()

            # setting collision box relatable to the actual player size
            self.rect = pygame.Rect(0, 0, 15, 25)
            self.rect.midbottom = rect_cop.midbottom
        else:
            # restore initial collision box
            rect_cop = self.rect.copy()
            self.rect = self.image.get_rect()
            self.rect.midbottom = rect_cop.midbottom

    # playing animations of the player
    def animate(self):

        # check if animation should be mirrored
        x_flip = False
        if self.movement[0] < 0:
            x_flip = True

        # check for animation type
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

        # playing the animation and updating 'frame' variable
        if self.frame > len(anim_lst) * self.anim_speed - 1:
            self.frame = 0
        if self.frame % self.anim_speed == 0:
            self.image = pygame.transform.flip(pygame.Surface.copy(anim_lst[self.frame // self.anim_speed]), x_flip,
                                               False)
        self.frame += 1

    # playing sound of the player
    def sound(self):
        if self.movement[0] != 0 and not self.SFX.get_busy() and self.on_ground and self.frame % (
                self.anim_speed * 2) == 0:
            self.SFX.play(self.run_sound[randint(0, 3)])
        elif self.movement[0] == 0 and self.movement[1] == 0:
            self.SFX.stop()

    def update(self):
        self.accurate_rect(True)

        # movement reset
        self.movement = [0, 0]

        # current time update
        self.timers['current'] = pygame.time.get_ticks()

        self.interactions_check()

        # status update
        self.on_ground = False
        if self.timers['current'] >= self.timers['dash'] + 200:
            self.dash = False

        # position update
        self.gravity()
        self.char_inputs()
        self.momentum()

        # animation update
        self.animate()

        # SFX update
        self.sound()

        self.accurate_rect(False)

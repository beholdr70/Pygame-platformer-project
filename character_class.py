import pygame
import level_data


class PlayerChar(pygame.sprite.Sprite):
    def __init__(self):
        # initialization
        super().__init__()
        self.timers = {'dash': pygame.time.get_ticks(), 'on_ground': pygame.time.get_ticks(),
                       'current': pygame.time.get_ticks(), 'air_time': pygame.time.get_ticks()}
        self.interactable = []
        self.movement = [0, 0]

        # body collisions
        self.image = pygame.image.load('char.png')
        self.rect = self.image.get_rect(topleft=(0, 0))

        # states
        self.on_ground = False
        self.dash = False
        self.interaction = False
        self.pushing = False

        # movement parameters
        self.space_down = False
        self.speed = 2
        self.acceleration = 0
        self.gravity_speed = 0
        self.jump_force = -14

        # ability charges
        self.dash_charges = 2
        self.double_jump_charge = 1
        self.launch_charge = 1

    # applying gravity on player
    def gravity(self):
        if not self.dash:
            self.gravity_speed += 1
            if self.gravity_speed > 10:
                self.gravity_speed = 10
            self.rect.y += self.gravity_speed
            self.movement[1] += self.gravity_speed
            self.prevent_collisions('y')

    def momentum(self):
        if self.acceleration:
            acceleration_coefficient = int(self.acceleration / abs(self.acceleration))
            self.acceleration = abs(self.acceleration) * 0.75 - 0.25
            if self.acceleration < 0:
                self.acceleration = 0
            if self.acceleration > 4 and not self.dash:
                self.acceleration = 4
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
            if self.timers['on_ground'] >= self.timers['air_time'] + 1000:
                self.launch_charge = 1
        else:
            self.timers['air_time'] = pygame.time.get_ticks()

    # checking for inputs
    def char_inputs(self):
        keys = pygame.key.get_pressed()

        # horizontal movement
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.acceleration -= 1.5
            self.movement[0] -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.acceleration += 1.5
            self.movement[0] += self.speed
        self.prevent_collisions('x')

        # vertical movement
        if keys[pygame.K_SPACE] and any((self.double_jump_charge, self.on_ground)) and not self.dash:
            if self.on_ground or self.timers['on_ground'] + 100 > self.timers['air_time']:
                self.gravity_speed = self.jump_force
                self.movement[1] += abs(self.gravity_speed)
            elif not self.on_ground and self.timers['air_time'] >= self.timers['on_ground'] + 400:
                self.double_jump_charge -= 1
                self.gravity_speed = self.jump_force - 1
                self.movement[1] += abs(self.jump_force - 1)
        self.prevent_collisions('y')

        # abilities
        if keys[pygame.K_LSHIFT] and self.dash_charges and self.timers['dash'] + 200 <= self.timers['current']:
            self.dash = True
            self.timers['dash'] = pygame.time.get_ticks()
            self.dash_charges -= 1
            if keys[pygame.K_a]:
                self.acceleration = -50
            elif keys[pygame.K_d]:
                self.acceleration = 50
            self.prevent_collisions('x')
        if keys[pygame.K_q] and self.launch_charge:
            pass

        # interaction
        if keys[pygame.K_e] and not any([self.dash, self.interaction, self.pushing]):
            if self.interactable:
                pass
                # self.interactable[0].interact()

    # preventing collisions with floor and walls
    def prevent_collisions(self, axis):
        collisions = pygame.sprite.spritecollide(self, level_data.level_tile_group, dokill=False)
        for collision_tile in collisions:
            # preventing clipping
            if axis == 'x':
                if self.movement[0] > 0:
                    self.rect.right = collision_tile.rect.left
                if self.movement[0] < 0:
                    self.rect.left = collision_tile.rect.right
            if axis == 'y':
                if self.movement[1] > 0:
                    self.rect.bottom = collision_tile.rect.top
                    self.on_ground = True
                if self.movement[1] < 0:
                    self.rect.top = collision_tile.rect.bottom
                    self.gravity_speed = 0
        self.ground_check()

    def update(self):
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
        self.momentum()
        self.char_inputs()
        self.movement = [0, 0]

#

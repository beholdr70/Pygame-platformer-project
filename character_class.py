import pygame
import level_data


class PlayerChar(pygame.sprite.Sprite):
    def __init__(self):
        # initialization
        super().__init__()
        self.cooldown_timers = {'dash': pygame.time.get_ticks(), 'on_ground': pygame.time.get_ticks(),
                                'jump': pygame.time.get_ticks(), 'current': pygame.time.get_ticks(),
                                'air_time': pygame.time.get_ticks()}
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

        # movement params
        self.space_down = False
        self.speed = 5
        self.gravity_speed = 0
        self.jump_force = -20

        # ability charges
        self.dash_charges = 2
        self.double_jump_charge = 1
        self.launch_charge = 1

    # applying gravity on player
    def gravity(self):
        self.gravity_speed += 1
        if self.gravity_speed > 10:
            self.gravity_speed = 10
        self.rect.y += self.gravity_speed
        self.movement[1] += self.gravity_speed
        self.prevent_collisions('y')

    # checking for ground collision
    def ground_check(self):
        if self.on_ground:
            self.cooldown_timers['on_ground'] = pygame.time.get_ticks()

            # abilities cooldown
            self.double_jump_charge = 1
            if self.cooldown_timers['on_ground'] >= self.cooldown_timers[
                'air_time'] + 2000:
                    self.dash_charges = 2
            if self.cooldown_timers['on_ground'] >= self.cooldown_timers[
                'air_time'] + 1000:
                self.launch_charge = 1
        else:
            self.cooldown_timers['air_time'] = pygame.time.get_ticks()

    # checking for inputs
    def char_inputs(self):
        on_ground = self.on_ground * 1
        keys = pygame.key.get_pressed()
        print(self.cooldown_timers['air_time'])
        # general movement
        # horizontal movement
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.movement[0] -= 5
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.movement[0] += 5
        self.prevent_collisions('x')
        # vertical movement
        if keys[pygame.K_SPACE] and any((self.double_jump_charge, on_ground)):
            if not on_ground:
                self.double_jump_charge -= 1
            if on_ground or self.cooldown_timers['air_time'] >= self.cooldown_timers['on_ground'] + 1000:
                print('a')
                self.gravity_speed = self.jump_force
                self.movement[1] += 10
        self.prevent_collisions('y')
        # special cases
        if keys[pygame.KMOD_LSHIFT] and self.dash_charges:
            pass
        if keys[pygame.K_q] and self.launch_charge:
            pass
        if keys[pygame.K_e] and not any([self.dash, self.interaction, self.pushing]):
            if self.interactable:
                pass
                # self.interactable[0].interact()

    # preventing collisions with floor and walls
    def prevent_collisions(self, axis):
        collisions = pygame.sprite.spritecollide(self, level_data.level_tile_group, dokill=False)
        self.ground_check()
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
        if not collisions:
            self.on_ground = False

    def update(self):
        # current time update
        self.cooldown_timers['current'] = pygame.time.get_ticks()

        # momentum update

        # collision check

        # check for interactable objects nearby
        if pygame.sprite.spritecollideany(self, level_data.interactive_group):
            self.interactable = pygame.sprite.spritecollide(self, level_data.interactive_group, dokill=False)
        else:
            self.interactable = []

        # position update
        self.gravity()
        self.char_inputs()
        self.movement = [0, 0]

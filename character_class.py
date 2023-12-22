import pygame
import level_data


class PlayerChar(pygame.sprite.Sprite):
    def __init__(self):
        # initialization
        super().__init__()
        self.cooldown_timers = {'dash': pygame.time.get_ticks(), 'on_ground': pygame.time.get_ticks(),
                                'jump': pygame.time.get_ticks(), 'current': pygame.time.get_ticks()}
        self.interactable = []

        # body collisions
        # self.image = pygame.image.load('').convert_alpha
        # self.rect = self.image.get_rect()

        # states
        self.on_ground = True
        self.dash = False
        self.interaction = False
        self.pushing = False

        # movement params
        self.speed = 10
        self.momentum = 1

        # ability charges
        self.dash_charges = 2
        self.double_jump_charge = 1
        self.launch_charge = 1

    def char_inputs(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            pass
        if keys[pygame.K_d]:
            pass
        if keys[pygame.K_SPACE] and any([self.on_ground, self.double_jump_charge]):
            pass
        if keys[pygame.KMOD_LSHIFT] and self.dash_charges:
            pass
        if keys[pygame.K_q] and self.launch_charge:
            pass
        if keys[pygame.K_e] and not any([self.dash, self.interaction, self.pushing]):
            if self.interactable:
                self.interactable[0].interact()

    def update(self):
        self.cooldown_timers['current'] = pygame.time.get_ticks()

        # floor collision check
        if pygame.sprite.spritecollideany(self, level_data.stable_ground_group):

            # on_ground timer check
            if not self.on_ground:
                self.cooldown_timers['on_ground'] = pygame.time.get_ticks()

            # on_ground status update
            self.on_ground = True

            # abilities cooldown
            self.double_jump_charge = 1
            if not self.dash_charges and self.cooldown_timers['current'] >= self.cooldown_timers['on_ground'] + 2000:
                self.dash_charges = 2
            if not self.launch_charge and self.cooldown_timers['current'] >= self.cooldown_timers['on_ground'] + 1000:
                self.launch_charge = 1

        # check for interactable objects nearby
        if pygame.sprite.spritecollideany(self, level_data.interact_group):
            self.interactable = pygame.sprite.spritecollide(self, level_data.interact_group, dokill=False)
        else:
            self.interactable = []

        self.char_inputs()

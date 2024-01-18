import pygame
import main

pygame.font.init()

menu_state = True
zoom = 26
size = (16 * zoom, 9 * zoom)


class ImageButton:
    def __init__(self, x, y, text, sound_path=None):
        self.x = x
        self.y = y
        self.font = pygame.font.Font('Resources/Font/ElixiR.ttf', 16)
        self.text = text
        self.hover_text = f'> {self.text} <'

        self.image = pygame.transform.scale(self.font.render(self.text, True, "floralwhite"),
                                            (self.font.size(self.text)))
        self.hover_image = pygame.transform.scale(self.font.render(self.hover_text, True, 'mediumturquoise'),
                                                  (self.font.size(self.hover_text)))
        self.rect = self.image.get_rect(center=(x, y))
        self.hover_rect = self.hover_image.get_rect(center=(x, y))
        self.sound = None
        if sound_path:
            self.sound = pygame.mixer.Sound(sound_path)
        self.is_hovered = False

    def draw(self, screen):
        if self.is_hovered:
            self.draw_outline(self.hover_image, self.hover_rect.topleft, screen)
            screen.blit(self.hover_image, self.hover_rect.topleft)
        else:
            self.draw_outline(self.image, self.rect.topleft, screen, color='grey10')
            screen.blit(self.image, self.rect.topleft)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint((mouse_pos[0] * main.size[0] // main.settings['screen_size'][0],
                                                  mouse_pos[1] * main.size[1] // main.settings['screen_size'][1]))

    def handle_event(self, event, purpose):
        global menu_state
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.sound:
                self.sound.play()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))
            if purpose == 'QUIT':
                main.close_game()
            if purpose == "START":
                menu_state = False
                return True
            if purpose == 'OPTIONS':
                pass

    def draw_outline(self, surf, pos, screen, color='White'):
        mask = pygame.mask.from_surface(surf)
        new_surf = mask.to_surface(setcolor=color)
        new_surf.set_colorkey((0, 0, 0))
        for pos_mask in [(pos[0] - 1, pos[1]), (pos[0] + 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)]:
            screen.blit(new_surf, pos_mask)


# Menu elements
#  Background
background = [pygame.transform.scale(pygame.image.load(
    'levels/levels_assets/Grassy_Mountains/layers_fullcolor/sky_fc.png'), size), pygame.transform.scale(
    pygame.image.load('levels/levels_assets/Grassy_Mountains/layers_fullcolor/clouds_bg.png'),
    size),
    pygame.transform.scale(pygame.image.load(
        'levels/levels_assets/Grassy_Mountains/layers_fullcolor/glacial_mountains.png'),
        size), pygame.transform.scale(
        pygame.image.load('levels/levels_assets/Grassy_Mountains/layers_fullcolor/clouds_mid_t_fc.png'),
        size), pygame.transform.scale(
        pygame.image.load(
            'levels/levels_assets/Grassy_Mountains/layers_fullcolor/clouds_front_t_fc.png'),
        size)]

#  Buttons
x_b = 65
y_b = 55
play_button = ImageButton(x_b, y_b + 45, 'Start', '')
options_button = ImageButton(x_b, y_b + 85, 'Options', '')
quit_button = ImageButton(x_b, y_b + 125, 'Quit', '')

#  Logo
logo = pygame.transform.scale(pygame.image.load('Resources/UI_graphics/logo.png'), (100, 64))

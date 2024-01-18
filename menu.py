import pygame
import main

menu_state = True
zoom = 26
size = (16 * zoom, 9 * zoom)


class ImageButton:
    def __init__(self, x, y, width, height, image_path, hover_image_path=None, sound_path=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.image = pygame.transform.scale(pygame.image.load(image_path), (width, height))
        self.hover_image = self.image
        if hover_image_path:
            self.hover_image = pygame.transform.scale(pygame.image.load(hover_image_path), (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.sound = None
        if sound_path:
            self.sound = pygame.mixer.Sound(sound_path)
        self.is_hovered = False

    def draw(self, screen):
        current_image = self.hover_image if self.is_hovered else self.image
        screen.blit(current_image, self.rect.topleft)

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
x_b = 15
y_b = 45
play_button = ImageButton(x_b, y_b + 45, 100, 32, 'Resources/UI_graphics/pl.png', 'Resources/UI_graphics/pl_hv.png',
                          '')
options_button = ImageButton(x_b, y_b + 85, 100, 32, 'Resources/UI_graphics/st.png',
                             'Resources/UI_graphics/st_hv.png',
                             '')
quit_button = ImageButton(x_b, y_b + 125, 100, 32, 'Resources/UI_graphics/qt.png', 'Resources/UI_graphics/qt_hv.png',
                          '')

#  Logo
logo = pygame.transform.scale(pygame.image.load('Resources/UI_graphics/logo.png'), (100, 64))

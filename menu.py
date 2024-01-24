import pygame
import main
from math import floor

pygame.font.init()
pygame.mixer.init()

options_state = False
menu_state = True
zoom = 26
size = (16 * zoom, 9 * zoom)
font = pygame.font.Font('Resources/Font/ElixiR.ttf', 16)

menu_sfx_channel = pygame.mixer.Channel(2)

the_end_title = pygame.transform.scale(font.render('The End', True, "mediumturquoise"),
                                       (font.size('The End' * 2)[0], 32))
the_end_title.set_alpha(0)


def draw_outline(surf, pos, screen, color='White', alpha=255):
    mask = pygame.mask.from_surface(surf)
    new_surf = mask.to_surface(setcolor=color)
    new_surf.set_colorkey((0, 0, 0))
    new_surf.set_alpha(alpha)
    for pos_mask in [(pos[0] - 1, pos[1]), (pos[0] + 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)]:
        screen.blit(new_surf, pos_mask)


class ImageButton:
    def __init__(self, x, y, text=None, sound_path=None, img=None):
        self.x = x
        self.y = y
        self.font = font
        self.text = text
        self.hover_text = f'> {self.text} <'
        if text:
            self.image = pygame.transform.scale(self.font.render(self.text, True, "floralwhite"),
                                                (self.font.size(self.text)))
            self.hover_image = pygame.transform.scale(self.font.render(self.hover_text, True, 'mediumturquoise'),
                                                      (self.font.size(self.hover_text)))
        else:
            self.image = pygame.image.load(img)
            self.hover_image = pygame.mask.from_surface(pygame.image.load(img)).to_surface(setcolor='mediumturquoise')
            self.hover_image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.hover_rect = self.hover_image.get_rect(center=(x, y))
        self.sound = None
        if sound_path:
            self.sound = pygame.mixer.Sound(sound_path)
        self.is_hovered = False

    def draw(self, screen):
        if self.is_hovered:
            draw_outline(self.hover_image, self.hover_rect.topleft, screen)
            screen.blit(self.hover_image, self.hover_rect.topleft)
        else:
            draw_outline(self.image, self.rect.topleft, screen, color='grey10')
            screen.blit(self.image, self.rect.topleft)

    def check_hover(self, mouse_pos, screen_size):
        self.is_hovered = self.rect.collidepoint((mouse_pos[0] * main.size[0] // screen_size[0],
                                                  mouse_pos[1] * main.size[1] // screen_size[1]))

    def text_change(self, new_txt):
        self.text = new_txt
        self.hover_text = f'> {self.text} <'
        self.image = pygame.transform.scale(self.font.render(self.text, True, "floralwhite"),
                                            (self.font.size(self.text)))
        self.hover_image = pygame.transform.scale(self.font.render(self.hover_text, True, 'mediumturquoise'),
                                                  (self.font.size(self.hover_text)))

    def handle_event(self, event, purpose):
        global menu_state, options_state
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.sound:
                menu_sfx_channel.play(self.sound)
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))
            if purpose == 'QUIT':
                main.close_game()
            if purpose == 'OPTIONS':
                options_state = True
            if purpose == 'SWITCH':
                lst = [[1366, 768], [1680, 945], [1680, 1050], [1920, 1080], [1920, 1200], [2560, 1080], [2560, 1440]]
                lst_index = lst.index(eval(self.text)) + 1
                if lst_index == len(lst):
                    lst_index = 0
                self.text_change(f'{lst[lst_index]}')

            if purpose == 'RESET':
                file = open('save_data', 'w')
                file.write(f'current_level = 1')
                file.close()
            if any(purpose == i for i in ['APPLY', 'START', 'RESUME']):
                if purpose == 'START':
                    menu_state = False
                return True
            if purpose == 'BACK':
                options_state = False
            if purpose == 'CHECKBOX':
                if self.text == 'On':
                    self.text_change('Off')
                    return False
                else:
                    self.text_change('On')
                    return True


class Slider(ImageButton):
    def __init__(self, x, y, sound_path=None):
        self.x = x
        self.y = y

        # Slider Path
        self.path = pygame.Surface((100, 5))
        self.path.fill('grey11')
        self.path.set_alpha(200)
        self.path_rect = self.path.get_rect()
        self.path_rect.center = (self.x, self.y)

        # Slider Handle
        self.handle = pygame.Surface((15, 15))
        self.handle.fill('floralwhite')
        self.handle_hover = self.handle.copy()
        self.handle_hover.fill('mediumturquoise')

        self.rect = self.handle.get_rect()
        self.rect.center = self.path_rect.center

        self.sound = None
        if sound_path:
            self.sound = pygame.mixer.Sound(sound_path)

        self.is_hovered = False
        self.drag = False

    def draw(self, screen):
        screen.blit(self.path, self.path_rect.topleft)
        if self.is_hovered:
            draw_outline(self.handle_hover, self.rect.topleft, screen)
            screen.blit(self.handle_hover, self.rect.topleft)
        else:
            draw_outline(self.handle, self.rect.topleft, screen, color='grey10')
            screen.blit(self.handle, self.rect.topleft)

    def handle_event(self, event, mouse_pos, screen_size):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drag = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.sound:
                menu_sfx_channel.play(self.sound)
            self.drag = True
        if self.drag and self.is_hovered:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))
            if self.path_rect.left < mouse_pos[0] * main.size[0] // screen_size[0] < self.path_rect.right:
                self.rect.center = (mouse_pos[0] * main.size[0] // screen_size[0], self.rect.center[1])
        return floor((self.rect.center[0] - self.path_rect.left) * 100 / self.path_rect.width) / 100

    def set_position(self, num):
        self.rect.center = (num * 100 * self.path_rect.width / 100 + self.path_rect.left, self.rect.center[1])


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
level_reset_button = ImageButton(x_b + 40, y_b + 46, img='Resources/UI_graphics/Redo.png',
                                 sound_path='Resources/Sounds/Menu/Ui/Click.wav')

play_button = ImageButton(x_b, y_b + 45, 'Start', sound_path='Resources/Sounds/Menu/Ui/Click.wav')
options_button = ImageButton(x_b, y_b + 85, 'Options', sound_path='Resources/Sounds/Menu/Ui/Click.wav')
quit_button = ImageButton(x_b, y_b + 125, 'Quit', sound_path='Resources/Sounds/Menu/Ui/Click.wav')
menu_buttons_group = [play_button, options_button, quit_button]

#  Logo
logo = pygame.transform.scale(pygame.image.load('Resources/UI_graphics/logo.png'), (100, 64))

# Pause Elements
options_button_pause = ImageButton(26 * 8, 13 * 9, 'Options', sound_path='Resources/Sounds/Menu/Ui/Click.wav')
quit_button_pause = ImageButton(26 * 8, 13 * 9 + 40, 'Quit', sound_path='Resources/Sounds/Menu/Ui/Click.wav')
resume_button_pause = ImageButton(26 * 8, 13 * 9 - 40, 'Resume', sound_path='Resources/Sounds/Menu/Ui/Click.wav')
pause_buttons_group = [options_button_pause, quit_button_pause, resume_button_pause]

# Options Elements
resolution_button = ImageButton(26 * 8 + 25, 13 * 9 - 55, '[1920, 1080]',
                                sound_path='Resources/Sounds/Menu/Ui/Click.wav')
fullscreen_checkbox_button = ImageButton(26 * 8 + 25, 13 * 9 - 30, 'Off',
                                         sound_path='Resources/Sounds/Menu/Ui/Click.wav')
music_slider = Slider(26 * 8 + 25, 13 * 9 - 5, sound_path='Resources/Sounds/Menu/Ui/Click.wav')
sfx_slider = Slider(26 * 8 + 25, 13 * 9 + 20, sound_path='Resources/Sounds/Menu/Ui/Click.wav')
apply_button = ImageButton(26 * 8 - 50, 13 * 9 + 40, 'Apply', sound_path='Resources/Sounds/Menu/Ui/Click.wav')
back_button = ImageButton(26 * 8 + 50, 13 * 9 + 40, 'Back', sound_path='Resources/Sounds/Menu/Ui/Click.wav')

fullscreen_img = pygame.image.load('Resources/UI_graphics/Fullscreen.png')
music_img = pygame.image.load('Resources/UI_graphics/Music.png')
resolution_img = pygame.image.load('Resources/UI_graphics/Screen_res.png')
sfx_img = pygame.image.load('Resources/UI_graphics/SFX.png')

option_buttons_group = [resolution_button, fullscreen_checkbox_button, music_slider, sfx_slider, apply_button,
                        back_button, (music_img, (26 * 8 - music_img.get_width() // 2 - 50,
                                                  music_slider.path_rect.y - music_img.get_height() // 2 + 1)),
                        (sfx_img, (26 * 8 - sfx_img.get_width() // 2 - 50,
                                   sfx_slider.path_rect.y - sfx_img.get_height() // 2 + 1)),
                        (fullscreen_img, (26 * 8 - fullscreen_img.get_width() // 2 - 50,
                                          fullscreen_checkbox_button.rect.top)),
                        (resolution_img, (26 * 8 - resolution_img.get_width() // 2 - 50,
                                          resolution_button.rect.top))]

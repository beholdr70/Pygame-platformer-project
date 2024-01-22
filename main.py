import character_class
import level_data
import menu
import pygame
import sys
from math import floor

pygame.mixer.init()
pygame.display.init()

# Screen Variables
zoom = 26
size = (16 * zoom, 9 * zoom)
camera_rect = pygame.Rect((0, 0), size)
display = pygame.Surface(size)
pygame.display.set_caption('Illios')
pygame.display.set_icon(pygame.image.load(f'Resources/UI_graphics/Icon.png'))
screen = pygame.display.set_mode((0, 0))

# Clock
clock = pygame.time.Clock()
FPS = 60

# Setup Variables
# Menu Related Variables
background = menu.background
pause_surf = pygame.Surface((size[0] * 0.55, size[1] * 0.65))
pause_surf.fill('royalblue4')
pause_surf.set_alpha(75)

#  Level Related Variables
current_level, spawnpoint, platform_group, decor_back_group, decor_front_group = None, None, None, None, None
interactive_group, hint_group, hint_alpha = None, None, None
parallax_background_offset = 0

#  Player Related Variable
player_group = pygame.sprite.GroupSingle()
playerFX_group = pygame.sprite.Group()

# Music Related Variables
music, ambience = pygame.mixer.Sound('Resources/Sounds/Menu/Music/Music.wav'), pygame.mixer.Sound(
    'Resources/Sounds/Menu/Ambience/Ambience.wav')
music_channel, ambience_channel = pygame.mixer.Channel(0), pygame.mixer.Channel(1)

# Cutscene Related Variables
fade_in_out = pygame.surface.Surface(size).convert_alpha()
fade_in_out.fill('Black')
fade_in_alpha = 255
point = None
cutscene = False


# setting up level
def setup():
    global current_level, spawnpoint, platform_group, decor_back_group, background, interactive_group, \
        hint_group, hint_alpha, player_group, decor_front_group, music, ambience, point, parallax_background_offset

    # level setup
    current_level = open('save_data').read()[-1]
    level_data.load(f'level_{current_level}.tmx')
    spawnpoint = level_data.spawnpoint
    platform_group = level_data.level_tile_group
    decor_back_group, decor_front_group = level_data.decor_back_group, level_data.decor_front_group
    background = level_data.background_group
    parallax_background_offset = 0
    interactive_group, hint_group = level_data.interactive_group, level_data.hint_group
    hint_alpha = 0
    point = spawnpoint[0]

    # player setup
    player_group = pygame.sprite.GroupSingle()
    player_group.add(character_class.PlayerChar(spawnpoint, upgrade=int(current_level) - 1))
    playerFX_group.add(character_class.CharacterFX('DASH_UI'))

    # music setup
    music = pygame.mixer.Sound(f'Resources/Sounds/Levels/Music/Music ({current_level}).wav')
    ambience = pygame.mixer.Sound(f'Resources/Sounds/Levels/Ambience/Ambience ({current_level}).wav')


# Settings Variable
settings = {}


# loading the settings from config
def load_settings():
    global screen, music_channel, ambience_channel, player_group, settings

    # reinitialization of screen
    pygame.display.quit()
    del screen
    pygame.display.init()

    # get settings
    settings = {i.split(' = ')[0]: eval(i.split(' = ')[1]) for i in open('config').readlines()}

    # changing the screen settings
    if settings['fullscreen']:
        flags = pygame.FULLSCREEN | pygame.NOFRAME | pygame.SCALED
    else:
        flags = 0
    screen = pygame.display.set_mode(settings['screen_size'], flags, vsync=1)
    if not settings['fullscreen']:
        screen = pygame.display.set_mode(settings['screen_size'], flags, vsync=1)
    pygame.display.set_icon(pygame.image.load('Resources/UI_graphics/Icon.png'))
    pygame.display.set_caption('Illios')

    # changing the sound settings
    for channel in [ambience_channel, music_channel, menu.menu_sfx_channel]:
        channel.stop()
    music_channel.set_volume(settings['music_volume'])
    ambience_channel.set_volume(settings['sfx_volume'])
    menu.menu_sfx_channel.set_volume(settings['sfx_volume'])
    level_data.level_sfx_channel.set_volume(settings['sfx_volume'])
    if player_group:
        list(player_group)[0].SFX.set_volume(settings['sfx_volume'])

    # options sync
    menu.sfx_slider.set_position(settings['sfx_volume'])
    menu.music_slider.set_position(settings['music_volume'])
    if settings['fullscreen']:
        menu.fullscreen_checkbox_button.text_change('On')
    menu.resolution_button.text_change(f'{settings["screen_size"]}')


def save_settings(settings_dict):
    file = open('config', 'w')
    end_res = ''
    for name, value in ([i, list(settings.values())[list(settings.keys()).index(i)]] for i in settings.keys()):
        end_res += f'{name} = {value}\n'
    file.write(end_res.strip())
    file.close()


# Exit Functions
def close_game():
    pygame.quit()
    sys.exit()


# I refuse to elaborate on the matter of this monstrosity
def camera_update(player_c):
    global parallax_background_offset

    level_groups = (decor_front_group, decor_back_group, platform_group, interactive_group, hint_group)

    x_pos_lst = [[tile.rect.x for tile in group] for group in level_groups]
    y_pos_lst = [[tile.rect.y for tile in group] for group in level_groups]
    offset = [player_c.rect.center[0] - camera_rect.center[0], player_c.rect.center[1] - camera_rect.center[1]]

    # x movement
    if (any(any(x - 1 > size[0] for x in group) for group in x_pos_lst) and offset[0] > 0) or (any(
            any(x < -17 for x in group) for group in x_pos_lst) and offset[0] < 0):
        for group in level_groups:
            for tile in group:
                tile.rect.x -= offset[0]
        parallax_background_offset += 0.25 * abs(offset[0]) / offset[0]
        spawnpoint[0] -= offset[0]
        player_c.rect.x -= offset[0]

    # y movement
    if (any(any(y > size[1] for y in group) for group in y_pos_lst) and
        offset[1] > 2) or (
            any(any(y < 0 for y in group) for group in y_pos_lst) and offset[1] < -2):
        for group in level_groups:
            for tile in group:
                tile.rect.y -= offset[1]
        spawnpoint[1] -= offset[1]
        player_c.rect.y -= offset[1]


# drawing the parallax background
def draw_background():
    global parallax_background_offset
    speed = 0
    for i in background:
        speed += 0.5
        for x in range(5):
            mult = speed + 1
            if menu.menu_state:
                pos = x * (size[0] + 0.5) - parallax_background_offset
                if background.index(i) == 4 and (x == 2 and pos == 0):
                    parallax_background_offset = 0
                    pos = x * (size[0] + 0.5) - parallax_background_offset
            else:
                pos = floor(x * size[0] - parallax_background_offset * mult - size[0] * 2)
            if not (menu.menu_state and background.index(i) >= 2):
                display.blit(i, (pos, 0))
    if menu.menu_state:
        for x in range(-2, 3):
            for i in background[2:]:
                pos = x * (size[0] + 0.5) - parallax_background_offset
                if background.index(i) != 2:
                    display.blit(i, (pos, 0))
                else:
                    display.blit(i, (size[0] * x, 0))


# code to run the game
if __name__ == '__main__':
    pause = False
    load_settings()
    while True:
        mouse_pos = pygame.mouse.get_pos()

        # event loop
        for event in pygame.event.get():
            # close the game
            if event.type == pygame.QUIT:
                close_game()
            elif event.type == pygame.KEYDOWN:
                # pause the game
                if event.key == pygame.K_ESCAPE and not menu.menu_state and not menu.options_state:
                    pause = not pause

            if (menu.menu_state or pause) and menu.options_state:
                menu.back_button.handle_event(event, 'BACK')
                boolean = menu.fullscreen_checkbox_button.handle_event(event, 'CHECKBOX')
                settings['fullscreen'] = boolean if boolean != None else settings['fullscreen']
                menu.resolution_button.handle_event(event, 'SWITCH')
                settings['sfx_volume'] = menu.sfx_slider.handle_event(event, mouse_pos, settings['screen_size'])
                settings['music_volume'] = menu.music_slider.handle_event(event, mouse_pos, settings['screen_size'])
                if menu.apply_button.handle_event(event, 'APPLY'):
                    settings['sfx_volume'] = 0 if settings['sfx_volume'] < 0.05 else settings['sfx_volume']
                    settings['music_volume'] = 0 if settings['music_volume'] < 0.05 else settings['music_volume']
                    settings['screen_size'] = eval(menu.resolution_button.text)
                    save_settings(settings)
                    load_settings()

            elif menu.menu_state:

                # activating buttons
                if not menu.options_state:
                    if menu.play_button.handle_event(event, 'START'):
                        music_channel.stop()
                        ambience_channel.stop()
                        setup()
                        cutscene = True
                    menu.quit_button.handle_event(event, 'QUIT')
                    menu.options_button.handle_event(event, 'OPTIONS')
                    menu.level_reset_button.handle_event(event, 'RESET')

            elif pause:
                if menu.resume_button_pause.handle_event(event, 'RESUME'):
                    pause = False
                menu.quit_button_pause.handle_event(event, 'QUIT')
                menu.options_button_pause.handle_event(event, 'OPTIONS')

        if not pause:
            if not menu.menu_state:
                if level_data.level_exit:
                    cutscene = True
                    point = size[0] + 60

                if cutscene:
                    # play cutscene
                    if fade_in_alpha > 255:
                        fade_in_alpha = 255
                    elif fade_in_alpha < 0:
                        fade_in_alpha = 0
                    fade_in_out.set_alpha(fade_in_alpha)
                    if point == spawnpoint[0]:
                        fade_in_alpha -= 1
                    else:
                        fade_in_alpha += 4
                    player = list(player_group)[0]
                    camera_update(player)
                    if player.rect.left < point:
                        player.rect.x += 1
                        player.movement[0] += 1
                        player.animate()
                        player.sound()
                    else:
                        if point == spawnpoint[0]:
                            cutscene = False
                        else:
                            for group in [player_group, decor_front_group, decor_back_group, player_group, hint_group,
                                          background, interactive_group, platform_group]:
                                if group != background:
                                    group.empty()
                                else:
                                    level_data.background_group = []
                            setup()
                            level_data.level_exit = False
                            music_channel.stop()
                            ambience_channel.stop()
                            point = spawnpoint[0]

                else:
                    # player update
                    for player in player_group:
                        camera_update(player)
                        player.update()
                        if player.rect.center[0] not in range(size[0]) or player.rect.center[1] not in range(size[1]):
                            player.rect.topleft = (spawnpoint[0], spawnpoint[1] - 80)
                    for fx in playerFX_group:
                        fx.update(player)

                # changing transparency of objects in hint group to hide/show them
                if not cutscene:
                    player.accurate_rect(True)
                    if list(filter(lambda x: 'GRAPHIC' in x.act_type,
                                   list(pygame.sprite.spritecollide(player, interactive_group, False)))):
                        hint_alpha += 5
                        if hint_alpha > 255:
                            hint_alpha = 255
                    else:
                        hint_alpha -= 5
                        if hint_alpha < 0:
                            hint_alpha = 0
                    player.accurate_rect(False)
                for hint in hint_group:
                    if hint.image:
                        hint.image.set_alpha(hint_alpha)

        # display update

        display.fill((0, 0, 0))
        draw_background()

        if not menu.menu_state:

            decor_back_group.draw(display)
            hint_group.draw(display)
            player_group.draw(display)
            platform_group.draw(display)
            decor_front_group.draw(display)
            if not cutscene:
                playerFX_group.draw(display)
            for fx in list(filter(lambda x: x.fx_type == 'DASH_UI', list(playerFX_group))):
                fx.draw_shine(display)

            # Fading into the level at the start
            if cutscene:
                display.blit(fade_in_out, (0, 0))
        else:
            parallax_background_offset += 0.5
            display.blit(menu.logo, (15, 15))
            if not menu.options_state:
                for button in menu.menu_buttons_group:
                    button.check_hover(mouse_pos, settings['screen_size'])
                    button.draw(display)
                if int(open('save_data').read()[-1]) > 1:
                    menu.level_reset_button.check_hover(mouse_pos, settings['screen_size'])
                    menu.level_reset_button.draw(display)
        if pause:
            display.blit(pause_surf, (camera_rect.center[0] - pause_surf.get_width() // 2,
                                      camera_rect.center[1] - pause_surf.get_height() // 2))
            if not menu.options_state:
                for button in menu.pause_buttons_group:
                    button.check_hover(mouse_pos, settings['screen_size'])
                    button.draw(display)
        if menu.options_state:
            for button in menu.option_buttons_group:
                if type(button) != tuple:
                    button.check_hover(mouse_pos, settings['screen_size'])
                    button.draw(display)
                else:
                    menu.draw_outline(button[0], button[1], display, 'gray10')
                    display.blit(button[0], button[1])
        screen.blit(pygame.transform.scale(display, settings['screen_size']), (0, 0))
        pygame.display.update()

        # sound update
        if not music_channel.get_busy():
            music_channel.play(music, loops=-1, fade_ms=500)
        if not ambience_channel.get_busy():
            ambience_channel.play(ambience, loops=-1, fade_ms=500)

        # clock update
        clock.tick(FPS)

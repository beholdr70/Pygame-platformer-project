import character_class
import level_data
import menu
import pygame
import sys

pygame.mixer.init()
pygame.display.init()

# Screen Variables
zoom = 26
size = (16 * zoom, 9 * zoom)
camera_rect = pygame.Rect((0, 0), size)
display = pygame.Surface(size)
pygame.display.set_caption('Ilios')
pygame.display.set_icon(pygame.image.load(f'Resources/UI_graphics/Icon.png'))
screen = pygame.display.set_mode((0, 0))

# Clock
clock = pygame.time.Clock()
FPS = 60

# Setup Variables
# Menu Related Variables
background = menu.background

#  Level Related Variables
current_level, spawnpoint, platform_group, decor_back_group, decor_front_group = None, None, None, None, None
interactive_group, hint_group, hint_alpha = None, None, None
parallax_background_offset = 0

#  Player Related Variable
player_group = None

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

    # changing the sound settings
    music_channel.set_volume(settings['music_volume'])
    ambience_channel.set_volume(settings['sfx_volume'])
    if player_group:
        list(player_group)[0].SFX.set_volume(settings['sfx_volume'])


load_settings()


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
        offset[1] > 4) or (
            any(any(y < 0 for y in group) for group in y_pos_lst) and offset[1] < 0):
        for group in level_groups:
            for tile in group:
                tile.rect.y -= offset[1]
        spawnpoint[1] -= offset[1]
        player_c.rect.y -= offset[1]


# drawing the parallax background
def draw_background():
    global parallax_background_offset
    for x in range(-2, 3):
        speed = 1
        if x < 0:
            x_coefficient = -1
        else:
            x_coefficient = 1
        for i in background:
            if menu.menu_state:
                if background.index(i) == 4 and ((x == 2 and pos == 0) or (x == -2 and pos == size[0])):
                    parallax_background_offset = 0
                pos = x * (size[0] + 0.5) - parallax_background_offset
            else:
                pos = int(abs(x) * size[0] - parallax_background_offset * speed) * x_coefficient
                speed += 0.4
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
    while True:

        # event loop
        for event in pygame.event.get():
            # close the game
            if event.type == pygame.QUIT:
                close_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    load_settings()
                # pause the game
                if event.key == pygame.K_ESCAPE and not menu.menu_state:
                    pause = not pause

            if menu.menu_state:

                # activating buttons
                if menu.play_button.handle_event(event, 'START'):
                    music_channel.stop()
                    ambience_channel.stop()
                    setup()
                    cutscene = True
                menu.quit_button.handle_event(event, 'QUIT')
                menu.options_button.handle_event(event, 'OPTIONS')

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

            # display update
            display.fill((0, 0, 0))
            draw_background()

            if not menu.menu_state:

                decor_back_group.draw(display)

                # changing transparency of objects in hint group to hide/show them
                if not cutscene:
                    if pygame.sprite.spritecollide(player, hint_group, False):
                        hint_alpha += 5
                        if hint_alpha > 255:
                            hint_alpha = 255
                    else:
                        hint_alpha -= 5
                        if hint_alpha < 0:
                            hint_alpha = 0
                for hint in hint_group:
                    hint.image.set_alpha(hint_alpha)

                hint_group.draw(display)
                player_group.draw(display)
                platform_group.draw(display)
                decor_front_group.draw(display)

                # Fading into the level at the start
                if cutscene:
                    display.blit(fade_in_out, (0, 0))
            else:
                parallax_background_offset += 0.5
                display.blit(menu.logo, (15, 15))
                for button in [menu.options_button, menu.play_button, menu.quit_button]:
                    button.check_hover(pygame.mouse.get_pos())
                    button.draw(display)
            screen.blit(pygame.transform.scale(display, settings['screen_size']), (0, 0))
            pygame.display.update()

        else:
            # !PAUSE MENU CODE GOES HERE (TBA)!
            pass

        # sound update
        if not music_channel.get_busy():
            music_channel.play(music, loops=-1, fade_ms=500)
        if not ambience_channel.get_busy():
            ambience_channel.play(ambience, loops=-1, fade_ms=500)

        # clock update
        clock.tick(FPS)

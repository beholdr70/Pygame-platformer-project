import character_class
import level_data
import pygame
import sys

pygame.mixer.init()

# screen variables
zoom = 26
size = (16 * zoom, 9 * zoom)
camera_rect = pygame.Rect((0, 0), size)
resolution = (1920, 1080)
display = pygame.Surface(size)
pygame.display.set_caption('Ilios')
screen = pygame.display.set_mode(resolution)

# clock
clock = pygame.time.Clock()
FPS = 60

# setup variables
current_level, spawnpoint, platform_group, decor_back_group, decor_front_group = None, None, None, None, None
background, interactive_group, hint_group, hint_alpha = None, None, None, None
parallax_background_offset = 0
player_group = None
music, ambience = None, None
music_channel, ambience_channel = pygame.mixer.Channel(0), pygame.mixer.Channel(1)


# setup function
def setup():
    global current_level, spawnpoint, platform_group, decor_back_group, background, interactive_group, \
        hint_group, hint_alpha, player_group, decor_front_group, music, ambience

    # level setup
    current_level = open('save_data').read()[-1]
    level_data.load(f'level_{current_level}.tmx')
    spawnpoint = level_data.spawnpoint
    platform_group = level_data.level_tile_group
    decor_back_group, decor_front_group = level_data.decor_back_group, level_data.decor_front_group
    background = level_data.background_group
    interactive_group, hint_group = level_data.interactive_group, level_data.hint_group
    hint_alpha = 0

    # player setup
    player_group = pygame.sprite.GroupSingle()
    player_group.add(character_class.PlayerChar(spawnpoint, upgrade=int(current_level) - 1))

    # music setup
    music = pygame.mixer.Sound(f'Resources/Sounds/Levels/Music/Music ({current_level}).wav')
    music.set_volume(0.1)
    ambience = pygame.mixer.Sound(f'Resources/Sounds/Levels/Ambience/Ambience ({current_level}).wav')


# exit functions
def close_game():
    pygame.quit()
    sys.exit()


def camera_update(player_c):
    global parallax_background_offset

    level_groups = (decor_front_group, decor_back_group, platform_group, interactive_group, hint_group)

    x_pos_lst = [[tile.rect.x for tile in group] for group in level_groups]
    y_pos_lst = [[tile.rect.y for tile in group] for group in level_groups]
    offset = [player_c.rect.center[0] - camera_rect.center[0], player_c.rect.center[1] - camera_rect.center[1]]

    # x movement
    if (any(any(x > size[0] for x in group) for group in x_pos_lst) and offset[0] > 0) or (any(
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


def draw_background():
    global parallax_background_offset
    for x in range(4):
        speed = 1
        for i in background:
            display.blit(i, (x * size[0] - parallax_background_offset * speed, 0))
            speed += 0.4


# code to run the game

if __name__ == '__main__':
    setup()
    while True:
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pass

        # player update
        for player in player_group:
            camera_update(player)
            player.update()
            if player.rect.center[0] not in range(size[0]) or player.rect.center[1] not in range(size[1]):
                player.rect.topleft = (spawnpoint[0], spawnpoint[1] - 80)

        # display update
        display.fill((0, 0, 0))
        draw_background()
        decor_back_group.draw(display)
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
        screen.blit(pygame.transform.scale(display, resolution), (0, 0))
        pygame.display.update()

        # sound update
        if not music_channel.get_busy():
            music_channel.play(music, loops=-1, fade_ms=500)
        if not ambience_channel.get_busy():
            ambience_channel.play(ambience, loops=-1, fade_ms=500)

        # clock update
        clock.tick(FPS)

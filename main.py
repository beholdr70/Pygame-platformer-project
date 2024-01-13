import character_class
import level_data
import pygame
import sys

pygame.init()

# variables
size = (960, 540)
resolution = (1920, 1080)
display = pygame.Surface(size)
screen = pygame.display.set_mode(resolution)

clock = pygame.time.Clock()
FPS = 60

# level setup
current_level = open('save_data').read()[-1]
level_data.load(f'level_{current_level}.tmx')
platform_group = level_data.level_tile_group
decor_back_group, decor_front_group = level_data.decor_back_group, level_data.decor_front_group
background = level_data.background_group
interactive_group, hint_group = level_data.interactive_group, level_data.hint_group
hint_alpha = 0

# Player setup
player_group = pygame.sprite.GroupSingle()
player_group.add(character_class.PlayerChar(level_data.spawnpoint, upgrade=int(current_level) - 1))


# functions
def close_game():
    pygame.quit()
    sys.exit()


def camera_update(player_c):
    level_groups = (decor_front_group, decor_back_group, platform_group, background, interactive_group, hint_group)

    # x movement
    x_pos_lst = [[tile.rect.x for tile in group] for group in level_groups]
    if player_c.rect.center[0] in range(size[0] // 2 - 30,
                                        size[0] // 2 + 31) and (
            (any(any(x > size[0] for x in group) for group in x_pos_lst) and
             player_c.movement[0] > 0) or (any(
        any(x < -17 for x in group) for group in x_pos_lst) and player_c.movement[0] < 0)):
        for group in level_groups:
            for tile in group:
                tile.rect.x -= player_c.movement[0]
        player_c.rect.x -= player_c.movement[0]

    # y movement
    y_pos_lst = [[tile.rect.y for tile in group] for group in level_groups]
    if (player_c.rect.y >= size[1] // 2 and any(any(y > size[1] for y in group) for group in y_pos_lst) and
        player_c.movement[1] > 4) or (
            player_c.rect.y <= size[1] // 2 and any(any(y < 0 for y in group) for group in y_pos_lst) and
            player_c.movement[1] < -19):
        for group in level_groups:
            for tile in group:
                tile.rect.y -= player_c.movement[1]
        player_c.rect.y -= player_c.movement[1]


# code to run the game

if __name__ == '__main__':
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pass
        display.fill((0, 0, 0))
        for player in player_group:
            camera_update(player)
            player.update()
            if player.rect.center[0] not in range(size[0]) or player.rect.center[1] not in range(size[1]):
                player.rect.topleft = (level_data.spawnpoint[0], level_data.spawnpoint[1] - 80)
        background.draw(display)
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
        clock.tick(FPS)

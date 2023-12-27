import character_class
import level_data
import pygame
import sys

# variables

player_group = pygame.sprite.GroupSingle()
player_group.add(character_class.PlayerChar())

resolution = (1680, 945)
display = pygame.Surface((960, 540))
screen = pygame.display.set_mode(resolution)

clock = pygame.time.Clock()
FPS = 60

# level
level_data.load([[level_data.LevelTile((480, 400), (960, 10), floor=True), 'title'],
                 [level_data.LevelTile((0, 520), (960, 10), floor=True), 'title']])
level_group = level_data.level_tile_group


# functions
def close_game():
    pygame.quit()
    sys.exit()


# code to run the game

if __name__ == '__main__':
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    pass
        display.fill((0, 0, 0))
        for player in player_group:
            player.update()
        player_group.draw(display)
        level_group.draw(display)
        screen.blit(pygame.transform.scale(display, resolution), (0, 0))
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()

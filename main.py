import character_class
import pygame
import sys

# variables

player_group = pygame.sprite.GroupSingle()
player_group.add(character_class.PlayerChar())

screen = pygame.display.set_mode([1024, 768])
clock = pygame.time.Clock()
FPS = 60


# functions
def close_game():
    pygame.quit()
    sys.exit()


def config_load():
    global screen
    config_params = open('config.txt').readlines()
    screen = pygame.display.set_mode(eval(config_params[0].split('=')[1].strip()))


# code to run the game

if __name__ == '__main__':
    pygame.init()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    config_load()
        screen.fill((0, 0, 0))
        for player in player_group:
            player.update()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

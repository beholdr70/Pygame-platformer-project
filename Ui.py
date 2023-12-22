import pygame


def config_load():
    global screen
    config_params = open('config.txt').readlines()
    screen = pygame.display.set_mode(eval(config_params[0].split('=')[1].strip()))

menu_open = False


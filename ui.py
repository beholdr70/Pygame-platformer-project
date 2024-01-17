import pygame
import sys
from button import ImageButton

wdh, hght = 960, 540
screen = pygame.display.set_mode((wdh, hght))

pygame.init()
pygame.display.set_caption('smty')
param = 50
a = 105

logo = pygame.image.load('logo.png')
log_rect = logo.get_rect(center=(param + 150, a))
screen.blit(logo, log_rect)

play_button = ImageButton(param, a + 85, 300, 100, 'pl.png', 'pl_hv.png', '')
options_button = ImageButton(param, a + 205, 300, 100, 'st.png', 'st_hv.png', '')
quit_button = ImageButton(param, a + 325, 300, 100, 'qt.png', 'qt_hv.png', '')


def main_menu():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            quit_button.handle_event(event, "QUIT")

        quit_button.check_hover(pygame.mouse.get_pos())
        quit_button.draw(screen)

        play_button.check_hover(pygame.mouse.get_pos())
        play_button.draw(screen)

        options_button.check_hover(pygame.mouse.get_pos())
        options_button.draw(screen)
        pygame.display.flip()

main_menu()

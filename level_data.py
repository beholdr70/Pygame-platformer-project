import pygame

# sprite groups
level_tile_group, interactive_group = pygame.sprite.Group(), pygame.sprite.Group()


def load(tile_data):
    for obj in tile_data:
        if obj[1] == 'interactive':
            interactive_group.add(obj[0])
        elif obj[1] == 'title':
            level_tile_group.add(obj[0])


class LevelTile(pygame.sprite.Sprite):

    def __init__(self, pos, size, img=None, floor=False):

        super().__init__()
        self.image = pygame.image.load('char.png')
        # self.rect = self.image.get_rect(lefttop=(pos))
        self.rect = pygame.Rect(pos, size)

        if floor:
            self.is_floor = True
        else:
            self.is_floor = False

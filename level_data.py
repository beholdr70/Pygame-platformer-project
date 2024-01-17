import pygame
from pytmx.util_pygame import load_pygame
import main

# Sprite Groups
level_tile_group, interactive_group = pygame.sprite.Group(), pygame.sprite.Group()
decor_back_group, decor_front_group = pygame.sprite.Group(), pygame.sprite.Group()
background_group = []
hint_group = pygame.sprite.Group()

# Variables
spawnpoint = None
level_exit = False


def load(level_name):
    global spawnpoint

    # load level data
    tile_data = load_pygame('levels/TMX/' + level_name)
    group = []

    # get spawnpoint
    spawnpoint_obj = tile_data.get_object_by_name('Spawn Point')
    spawnpoint = [spawnpoint_obj.x, spawnpoint_obj.y]

    # get tiles
    for layer in tile_data.visible_layers:
        if 'Platforms' in layer.name:
            group = level_tile_group
        elif 'Back' in layer.name:
            group = decor_back_group
        elif 'Front' in layer.name:
            group = decor_front_group
        if hasattr(layer, 'data'):
            for x, y, surface in layer.tiles():
                group.add(LevelTile(((x - 1) * 16, y * 16), surface.convert_alpha()))

    # get objects
    for obj in tile_data.objects:
        if obj.type == 'Background':
            background_group.append(pygame.transform.scale(obj.image.convert_alpha(), main.size))
        if 'Checkbox' in str(obj.type):
            if 'Exit' in str(obj.type):
                o_type = 'Exit'
            else:
                o_type = None
            interactive_group.add(
                InteractiveObj((obj.x - 16, obj.y), pygame.Surface((int(obj.width), int(obj.height))), o_type))
        if obj.type == 'Graphic':
            hint_group.add(LevelTile((obj.x - 16, obj.y),
                                     pygame.transform.scale(obj.image.convert_alpha(), (obj.width, obj.height))))


class LevelTile(pygame.sprite.Sprite):

    def __init__(self, position, surface):
        # initialization
        super().__init__()
        self.image = surface
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=position)


class InteractiveObj(pygame.sprite.Sprite):

    def __init__(self, position, surface, type=None):
        super().__init__()
        self.image = None
        self.rect = surface.get_rect(topleft=position)
        self.type = type

    def interact(self):
        if self.type == 'Exit':
            self.exit_level()

    def exit_level(self):
        global level_exit
        level = int(open('save_data').read()[-1]) + 1
        line = open('save_data').read()[:-1]
        save_file = open('save_data', 'w+')
        if level > 2:
            level = 2
        save_file.write(f'{line[:-1]} {level}')
        save_file.close()
        level_exit = True

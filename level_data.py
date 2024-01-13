import pygame
from pytmx.util_pygame import load_pygame

# sprite groups
level_tile_group, interactive_group = pygame.sprite.Group(), pygame.sprite.Group()
decor_back_group, decor_front_group = pygame.sprite.Group(), pygame.sprite.Group()
background_group = pygame.sprite.Group()
hint_group = pygame.sprite.Group()

# Variables
spawnpoint = None


def load(level_name):
    global spawnpoint
    tile_data = load_pygame('levels/TMX/' + level_name)
    group = []

    # get spawnpoint
    spawnpoint_obj = tile_data.get_object_by_name('Spawn Point')
    spawnpoint = (spawnpoint_obj.x, spawnpoint_obj.y)

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
                group.add(LevelTile(((x - 1) * 16, y * 16), surface))

    # get objects
    for obj in tile_data.objects:
        if obj.type == 'Background':
            background_group.add(LevelTile((obj.x - 16, obj.y), pygame.transform.scale(obj.image, (1120, 640))))
        if obj.type == 'Checkbox':
            interactive_group.add(
                InteractiveObj((obj.x - 16, obj.y), pygame.Surface((int(obj.width), int(obj.height)))))
        if obj.type == 'Graphic':
            hint_group.add(LevelTile((obj.x - 16, obj.y), pygame.transform.scale(obj.image, (obj.width, obj.height))))


class LevelTile(pygame.sprite.Sprite):

    def __init__(self, position, surface):
        super().__init__()
        self.image = surface
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=position)


class InteractiveObj(pygame.sprite.Sprite):

    def __init__(self, position, surface):
        super().__init__()
        self.image = None
        self.rect = surface.get_rect(topleft=position)

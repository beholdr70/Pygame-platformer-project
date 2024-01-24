import pygame
from pytmx.util_pygame import load_pygame
import main

pygame.mixer.init()

# Sprite Groups
level_tile_group, interactive_group = pygame.sprite.Group(), pygame.sprite.Group()
decor_back_group, decor_front_group = pygame.sprite.Group(), pygame.sprite.Group()
background_group = []
hint_group = pygame.sprite.Group()

# Variables
spawnpoint = None
level_exit = False
level_sfx_channel = pygame.mixer.Channel(4)
game_finale = False
final_cutscene_time = 0


class LevelTile(pygame.sprite.Sprite):

    def __init__(self, position, surface, button_id=None, state=False):
        # initialization
        super().__init__()
        self.image = surface
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=position)
        self.id = None
        self.id = button_id
        if button_id:
            self.is_active = False
            self.image.set_alpha(0)
            if state:
                self.change_state()

        else:
            self.is_active = True

    def change_state(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(0)


class InteractiveObj(pygame.sprite.Sprite):

    def __init__(self, position, surface, action_type=None, button_id=None):
        super().__init__()
        self.rect = surface.get_rect(topleft=position)
        self.image = None
        self.act_type = action_type if action_type else ''
        if 'WINDZONE' in self.act_type or 'FINALE' in self.act_type:
            self.activation_type = 'Passive'
        else:
            self.activation_type = 'Interaction'
        if button_id:
            self.button_id = button_id

    def interact(self, player=None):
        global game_finale, final_cutscene_time
        if 'EXIT' in self.act_type:
            self.exit_level()
        if 'FINALE' in self.act_type:
            game_finale = True
            final_cutscene_time = pygame.time.get_ticks()
        if 'PLATFORM_SWITCH' in self.act_type:
            level_sfx_channel.play(pygame.mixer.Sound('Resources/Sounds/SFX/Platform Switch.wav'))
            platforms = list(filter(lambda x: x.id == self.button_id, list(level_tile_group)))
            for platform in platforms:
                platform.change_state()
        if 'WINDZONE' in self.act_type:
            if player and not player.dash:
                if 'R' in self.act_type:
                    player.rect.x += 3
                    player.movement[0] += 3
                    player.prevent_collisions('x')
                elif 'L' in self.act_type:
                    player.rect.x -= 3
                    player.movement[0] = -3
                    player.prevent_collisions('x')
                elif 'UP' in self.act_type:
                    if player.gravity_speed > -4:
                        player.gravity_speed -= 3
                    player.prevent_collisions('y')
                    # player.animate()
                elif 'DOWN' in self.act_type:
                    player.gravity_speed += 2
                    player.prevent_collisions('y')
                    # player.animate()

    def exit_level(self):
        global level_exit
        level = int(open('save_data').read()[-1]) + 1
        line = open('save_data').read()[:-1]
        save_file = open('save_data', 'w+')
        if level > 4:
            level = 4
        save_file.write(f'{line[:-1]} {level}')
        save_file.close()
        level_exit = True


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
        button_id = None
        if 'Platforms' in layer.name:
            group = level_tile_group
            if 'Button' in layer.name:
                button_id = str(layer.name).split(', ')[-1]
        elif 'Back' in layer.name:
            group = decor_back_group
        elif 'Front' in layer.name:
            group = decor_front_group
        if hasattr(layer, 'data'):
            for x, y, surface in layer.tiles():
                group.add(LevelTile(((x - 1) * 16, y * 16), surface.convert_alpha(), button_id=button_id))

    # get objects
    for obj in tile_data.objects:
        button_id = None
        act_type = None
        if 'Background' in str(obj.type):
            if 'Graphic' not in str(obj.type):
                background_group.append(pygame.transform.scale(obj.image.convert_alpha(), main.size))
            else:
                background_group.append('Graphic')
        if 'Checkbox' in str(obj.type):
            if 'Exit' in str(obj.type):
                act_type = 'EXIT'
            elif 'Plat_switch' in str(obj.type):
                act_type = 'PLATFORM_SWITCH'
                button_id = obj.name[-1]
            elif 'Windzone' in str(obj.type):
                act_type = str(obj.type).split(', ')[1].upper()
            elif 'Finale' in str(obj.type):
                act_type = 'FINALE'
            if 'Graphic' in str(obj.type):
                if act_type:
                    act_type += ' GRAPHIC'
                else:
                    act_type = 'GRAPHIC'
            interactive_group.add(
                InteractiveObj((obj.x - 16, obj.y), pygame.Surface((int(obj.width), int(obj.height))), act_type,
                               button_id=button_id))
        elif 'Graphic' in str(obj.type):
            if obj.image:
                hint_group.add(LevelTile((obj.x - 16, obj.y),
                                         pygame.transform.scale(obj.image.convert_alpha(), (obj.width, obj.height))))

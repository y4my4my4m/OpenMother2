import pygame
import sys
import random

from character import Character
from npc import NPC
from camera import Camera
from utils.collision import load_collision_boxes
from dialoguebox import DialogueBox
from battle import BattleSystem, BattleMenu, BattleBackground, BattleLog
from inputcontroller import InputController
from sfx import SoundController
from array import array

import numpy as np
import moderngl


pygame.init()

# Screen Configuration
FULLSCREEN = False


if FULLSCREEN:
    infoObject = pygame.display.Info()
    screen_width = infoObject.current_w
    screen_height = infoObject.current_h
    #make it full screen
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.OPENGL | pygame.DOUBLEBUF)
else:
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height), (pygame.FULLSCREEN if FULLSCREEN else 0) | pygame.OPENGL | pygame.DOUBLEBUF)

ctx = moderngl.create_context()

# Quad covering the viewport
quad_vertices = array('f', [
    -1.0, -1.0, 0.0, 1.0,
     1.0, -1.0, 1.0, 1.0,
    -1.0,  1.0, 0.0, 0.0,
     1.0,  1.0, 1.0, 0.0,
])

# Assuming you have the quad_vertices buffer created
quad_vbo = ctx.buffer(quad_vertices.tobytes())

bright_fs = '''
    #version 330 core
    out vec4 FragColor;
    in vec2 v_texcoord;

    uniform sampler2D scene;

    void main() {
        vec3 color = texture(scene, v_texcoord).rgb;
        float brightness = dot(color, vec3(0.2126, 0.7152, 0.0722));
        if(brightness > 0.9) // Adjust threshold as needed
            FragColor = vec4(color, 1.0);
        else
            FragColor = vec4(0.0, 0.0, 0.0, 1.0);
    }
    '''

blur_fs = '''
    #version 330 core
    out vec4 FragColor;
    in vec2 v_texcoord;

    uniform sampler2D brightText;
    uniform bool horizontal;
    uniform float weight[5] = float[](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

    void main() {
        vec2 tex_offset = 1.0 / textureSize(brightText, 0); // Gets the size of one texel
        vec3 result = texture(brightText, v_texcoord).rgb * weight[0];
        if(horizontal) {
            for(int i = 1; i < 5; ++i) {
                result += texture(brightText, v_texcoord + vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
                result += texture(brightText, v_texcoord - vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
            }
        } else {
            for(int i = 1; i < 5; ++i) {
                result += texture(brightText, v_texcoord + vec2(0.0, tex_offset.y * i)).rgb * weight[i];
                result += texture(brightText, v_texcoord - vec2(0.0, tex_offset.y * i)).rgb * weight[i];
            }
        }
        FragColor = vec4(result, 1.0);
    }
    '''

blend_fs = '''
    #version 330 core
    out vec4 FragColor;
    in vec2 v_texcoord;

    uniform sampler2D scene;
    uniform sampler2D bloomBlur;

    void main() {
        vec3 hdrColor = texture(scene, v_texcoord).rgb;
        vec3 bloomColor = texture(bloomBlur, v_texcoord).rgb;
        FragColor = vec4(hdrColor + bloomColor, 1.0); // Simple additive blending
    }
    '''

vertex_shader = '''
    #version 330
    in vec2 vert;
    in vec2 texcoord;
    out vec2 v_texcoord;
    void main() {
        v_texcoord = texcoord;
        gl_Position = vec4(vert, 0.0, 1.0);
    }
    '''

# Compile shaders and create programs
bright_program = ctx.program(vertex_shader=vertex_shader, fragment_shader=bright_fs)
blur_program = ctx.program(vertex_shader=vertex_shader, fragment_shader=blur_fs)
blend_program = ctx.program(vertex_shader=vertex_shader, fragment_shader=blend_fs)

# Framebuffers for bright parts and blurring steps
bright_fbo = ctx.framebuffer(color_attachments=[ctx.texture((screen_width, screen_height), components=4)])
blur_fbo1 = ctx.framebuffer(color_attachments=[ctx.texture((screen_width, screen_height), components=4)])
blur_fbo2 = ctx.framebuffer(color_attachments=[ctx.texture((screen_width, screen_height), components=4)])  # For two-pass blur


scene_tex = ctx.texture((screen_width, screen_height), components=4)
scene_fbo = ctx.framebuffer(color_attachments=[scene_tex])


# Assuming quad_vbo is already created with 'vert' and 'texcoord' data
bright_vao = ctx.vertex_array(bright_program, [(quad_vbo, '2f 2f', 'vert', 'texcoord')])
blur_vao = ctx.vertex_array(blur_program, [(quad_vbo, '2f 2f', 'vert', 'texcoord')])
blend_vao = ctx.vertex_array(blend_program, [(quad_vbo, '2f 2f', 'vert', 'texcoord')])


# detect screen resolution
# Colors and FPS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 60
clock = pygame.time.Clock()

GAME_STATE_EXPLORATION = "exploration"
GAME_STATE_BATTLE = "battle"
GAME_STATE_GAMEOVER = "gameover"

game_state = GAME_STATE_EXPLORATION
battle_system = None

# Load assets
dialogue_box = DialogueBox('assets/fonts/earthbound-menu-extended.ttf', 24, screen_width, screen_height)

onett_layer0 = pygame.image.load('assets/maps/onett_layer0.png').convert_alpha()
map_layer0_rect = onett_layer0.get_rect()

onett_layer1 = pygame.image.load('assets/maps/onett_layer1.png').convert_alpha()
map_layer1_rect = onett_layer1.get_rect()
# tile_size = 32  # Change this to the size of your tiles
# tiles_layer1 = [[onett_layer1.subsurface(pygame.Rect(x, y, tile_size, tile_size)) for x in range(0, onett_layer1.get_width() // tile_size * tile_size, tile_size)] for y in range(0, onett_layer1.get_height() // tile_size * tile_size, tile_size)]
collision_boxes = load_collision_boxes('assets/maps/onett_layer1_collision_boxes.json')

# Character
ness_stats = [874, 10, 5, 3, 4, 7]
ness = Character("Ness", 1000, 1500, 16, 24, 'assets/sprites/ness_normal.png', collision_boxes, ness_stats)  
velocity = 1

# Initialize Camera
camera = Camera(screen_width, screen_height, map_layer0_rect.width, map_layer0_rect.height)
camera.zoom = 3
# camera.update(ness)  # Force the camera to center on Ness at startup

# Music
ONETT_MUSIC_PATH = 'assets/music/onett_snes.mp3'
BATTLE_MUSIC_PATH = 'assets/music/battle.mp3'

# Load and play exploration music by default
pygame.mixer.music.load(ONETT_MUSIC_PATH)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(1.0)

# Menu
menu_open = False
menu_selection = 0
menu_columns = 2
menu_rows = 3
status_menu_open = False
current_selection = None

menu_font = pygame.font.Font('assets/fonts/earthbound-menu-extended.ttf', 24)
menu_options = ["Talk to", "Goods", "PSI", "Equip", "Check", "Status"]

# Sound
cursor_horizontal_sfx = pygame.mixer.Sound('assets/sounds/curshoriz.wav')
cursor_vertical_sfx = pygame.mixer.Sound('assets/sounds/cursverti.wav')

# Debug
debug_view_collision = True
debug_view_layer0 = False
debug_view_layer1 = False
debug_disable_collision = False
debug_font = pygame.font.Font('assets/fonts/earthbound-menu-extended.ttf', 12)

# NPCs
npcs = [
    NPC("Hotel Manager", 1020, 1500, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "Hello, adventurer!", ness, [45, 10, 53, 3, 2, 2], 99, True, None, 3, 4, "look_at_player", dialogue_box),
    NPC("RandomNPC2", 1620, 1872, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "Have you seen anything weird lately?", ness, [50, 20, 1, 3, 2, 2], 56, True, None, 1, 9, "look_at_player", dialogue_box),
    NPC("RandomNPC3", 1584, 1423, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "It's a beautiful day, isn't it?", ness, [20, 20, 2, 5, 7, 2], 111, True, None, 3, 6, "look_at_player", dialogue_box),
    NPC("RandomNPC4", 2154, 889, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "Beware of crows...", ness, [50, 20, 3, 5, 7, 2], 66, True, None, 3, 2, "look_at_player", dialogue_box),
    NPC("RandomNPC5", 1490, 1157, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "I lost my car, can you help me find it?", ness, [50, 20, 1, 7, 7, 2], 137, True, None, 3, 14, "look_at_player", dialogue_box),
    NPC("Random hoe", 1300, 1700, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "The arcane beckons.", ness, [60, 15, 8, 10, 5, 3], 32, True, None, 3, 16, "look_at_player", dialogue_box),
    NPC("Curious Child", 1810, 1350, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "Have you seen that thing in the sky?", ness, [30, 25, 1, 1, 1, 10], 12, True, None, 3, 18, "look_at_player", dialogue_box),
    NPC("Police Chief", 1900, 1500, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "Move along, punk!", ness, [45, 5, 7, 2, 4, 5], 56, True, None, 3, 22, "follow", dialogue_box),
    NPC("Mysterious Vendor", 1300, 1160, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "Looking for something rare?", ness, [50, 30, 2, 6, 8, 2], 82, True, None, 3, 10, "look_at_player", dialogue_box),
    NPC("Classy Guy", 1900, 1000, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "There's treasure at the arcades.", ness, [55, 20, 4, 3, 6, 4], 43, True, None, 3, 21, "look_at_player", dialogue_box)
]

layer0_npcs = []
layer1_npcs = []

# GUI
swirl_frame_images = [pygame.image.load(f'assets/sprites/swirls/enemy/{i}.png').convert_alpha() for i in range(1, 24)]  # Adjust path and range as needed

# Battle
battle_menu_options = ["Bash", "Goods", "Auto Fight", "PSI", "Defend", "Run"]
battle_menu = BattleMenu(menu_font, battle_menu_options)

# Gameover
gameover_image = pygame.image.load('assets/sprites/gameover.png').convert_alpha()

# Module Controllers
input_controller = InputController()
sound_controller = SoundController()

swirl_animation = False
running = True

ness_sprite_index = 0

def draw_entities_sorted(player, npcs, camera, screen):
    # Combine player and NPCs into one list, assuming they have similar attributes for position
    entities = [player] + npcs
    
    # Sort entities based on the bottom edge of their rectangles (their "feet")
    sorted_entities = sorted(entities, key=lambda x: x.rect.bottom)
    
    # Draw entities in sorted order
    for entity in sorted_entities:

        if entity.stats["hp"] > 0:
            entity.handle_behaviour()
            entity_image = entity.animate()  # Assuming each entity has an animate() method
            entity_pos = (
                (entity.rect.x - camera.camera.x) * camera.zoom, 
                (entity.rect.y - camera.camera.y) * camera.zoom
            )
            scaled_entity_image = pygame.transform.scale(entity_image, (
                int(entity.rect.width * camera.zoom), 
                int(entity.rect.height * camera.zoom)
            ))
            screen.blit(scaled_entity_image, entity_pos)

def draw_everything():
    # Determine the visible area of the map, including a 100px outer bound
    visible_area = pygame.Rect(
        camera.camera.x - 100 / camera.zoom, 
        camera.camera.y - 100 / camera.zoom, 
        screen_width / camera.zoom + 200 / camera.zoom, 
        screen_height / camera.zoom + 200 / camera.zoom
    )
    visible_area.normalize()  # Ensure width and height are positive

    visible_area.clamp_ip(onett_layer0.get_rect())
    # Before creating a subsurface, check if visible_area exceeds the bounds of onett_layer0
    if visible_area.right > onett_layer0.get_width():
        visible_area.right = onett_layer0.get_width()
    if visible_area.bottom > onett_layer0.get_height():
        visible_area.bottom = onett_layer0.get_height()

    # After adjustments, check if visible_area has a valid size to avoid ValueError when creating a subsurface.
    # If not, default to a minimal valid subsurface or handle as needed.
    if visible_area.width <= 0 or visible_area.height <= 0:
        # Default to a minimal subsurface or handle this case as needed, perhaps with a placeholder or error message.
        print("Visible area is outside the surface bounds.")
        return  # Skip rendering or handle as needed.

    try:
        visible_map_segment = onett_layer0.subsurface(visible_area)
    except ValueError:
        # Handle the case when subsurface cannot be created due to invalid rectangle, if necessary.
        print("Error creating subsurface. Visible area might be outside the surface bounds.")
        return


    # Scale the visible portion to the screen size, adjusting for the zoom level
    scaled_map_image = pygame.transform.scale(visible_map_segment, (
        int(visible_area.width * camera.zoom), 
        int(visible_area.height * camera.zoom)
    ))

    # Calculate the position to blit the scaled map on the screen
    blit_position = (
        visible_area.x * camera.zoom - camera.camera.x * camera.zoom, 
        visible_area.y * camera.zoom - camera.camera.y * camera.zoom
    )

    screen.fill(BLACK)
    if not debug_view_layer0:
        screen.blit(scaled_map_image, blit_position)

    # Render Ness (similarly scaled and positioned)
    ness_image = ness.animate()
    ness_pos = (
        (ness.rect.x - camera.camera.x) * camera.zoom, 
        (ness.rect.y - camera.camera.y) * camera.zoom
    )
    scaled_ness_image = pygame.transform.scale(ness_image, (
        int(ness.rect.width * camera.zoom), 
        int(ness.rect.height * camera.zoom)
    ))
    # Extract the visible portion of the layer 1 map

    visible_area.clamp_ip(onett_layer1.get_rect())
    visible_map_segment_layer1 = onett_layer1.subsurface(visible_area)

    # Scale the visible portion to the screen size, adjusting for the zoom level
    scaled_map_image_layer1 = pygame.transform.scale(visible_map_segment_layer1, (
        int(visible_area.width * camera.zoom), 
        int(visible_area.height * camera.zoom)
    ))

    # Calculate the position to blit the scaled map on the screen
    blit_position_layer1 = (
        visible_area.x * camera.zoom - camera.camera.x * camera.zoom, 
        visible_area.y * camera.zoom - camera.camera.y * camera.zoom
    )

    # # Inside your draw_everything() function before rendering entities
    if adjust_z_index(ness, collision_boxes):
        # Draw parts of the environment that are "behind" the character first
        if not debug_view_layer1:
            screen.blit(scaled_map_image_layer1, blit_position_layer1)
        # screen.blit(scaled_ness_image, ness_pos)
        draw_entities_sorted(ness, npcs, camera, screen)
        # After that, draw the remaining parts of the environment
    else:
        # Draw the character first, then overlay parts of the environment
        # screen.blit(scaled_ness_image, ness_pos)
        draw_entities_sorted(ness, npcs, camera, screen)
        if not debug_view_layer1:
            screen.blit(scaled_map_image_layer1, blit_position_layer1)


def draw_debug():
    handle_debug()
    menu_width, menu_height = 175, 45
    # y_offset = 50
    if debug_view_collision:
        # Render collision boxes for debugging
        pygame.draw.rect(screen, BLACK, pygame.Rect(20, 70, menu_width, menu_height))
        debug_view_collision_text = menu_font.render("Collision View", True, (255, 0, 0))
        screen.blit(debug_view_collision_text, (30, 73))
        for index, box in enumerate(collision_boxes):
            # print(box)
            pygame.draw.rect(screen, (255, 0, 0), camera.apply(box), 2)  # Use a thickness of 2 for visibility

            box_id = debug_font.render(str(index), True, (255, 0, 0))  # Convert index to string before rendering
            # Create a Rect for the text at the desired position
            text_rect = pygame.Rect(box.x + 4, box.y + 4, box_id.get_width(), box_id.get_height())

            # Apply the camera transformation to the text Rect
            transformed_text_rect = camera.apply(text_rect)

            # Blit the text at the transformed position
            screen.blit(box_id, transformed_text_rect.topleft)
    if debug_disable_collision:
        pygame.draw.rect(screen, BLACK, pygame.Rect(20, 20, menu_width, menu_height))
        text = menu_font.render("Collision Disabled", True, (255, 0, 0))
        screen.blit(text, (30, 25))

def draw_menu():
    if menu_open:
        # Define menu properties
        menu_width, menu_height = 240, 160
        menu_x, menu_y = (screen_width - menu_width) -20 , 20
        menu_color = BLACK

        # Draw menu
        pygame.draw.rect(screen, menu_color, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 2)


        # Calculate menu item dimensions
        item_width = menu_width // 2
        item_height = menu_height // 3

        # Render menu options
        for i, option in enumerate(menu_options):
            col = i % menu_columns
            row = i // menu_columns

            item_x = menu_x + col * (menu_width // menu_columns)
            item_y = menu_y + row * (menu_height // menu_rows)

            option_text = "> " + option if i == menu_selection else "   " + option
            text = menu_font.render(option_text, True, WHITE)
            screen.blit(text, (item_x + 10, item_y + 10))
        
        if status_menu_open:
            draw_status_panel(screen, ness)

def draw_status_panel(screen, character):
    # Panel dimensions and position
    panel_width = 420
    panel_height = 240
    panel_x = (screen.get_width() - panel_width) // 2
    panel_y = (screen.get_height() - panel_height) // 2

    # Background of the panel
    panel_background = pygame.Surface((panel_width, panel_height))
    panel_background.fill(BLACK)
    panel_background_border = pygame.Surface((panel_width+4, panel_height+4))
    panel_background_border.fill(WHITE)
    # pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2) # Border

    # Character sprite
    sprite_resized = pygame.transform.scale(character.menu_sprite, (character.menu_sprite.get_width() * 3, character.menu_sprite.get_height() * 3))  # Adjust as needed
    character.make_transparent(sprite_resized)
    panel_background.blit(sprite_resized, (panel_width // 2 - sprite_resized.get_width() //2, 64))

    # Character name
    name_surface = menu_font.render(character.name, True, WHITE)
    panel_background.blit(name_surface, (panel_width // 2  - sprite_resized.get_width() //2 + 2, 20))  # Adjust position as needed

    # Display stats
    stat_start_x = 40
    stat_start_y = 150
    stats_per_row = 3
    stat_count = 0
    for stat, value in character.stats.items():
        stat_surface = menu_font.render(f"{stat}: {value}", True, WHITE)
        stat_x = stat_start_x + (stat_count % stats_per_row) * 120
        stat_y = stat_start_y + (stat_count // stats_per_row) * 30
        panel_background.blit(stat_surface, (stat_x, stat_y))
        stat_count += 1

    # Draw the panel on the main screen
    screen.blit(panel_background_border, (panel_x-2, panel_y-2))
    screen.blit(panel_background, (panel_x, panel_y))




def adjust_z_index(character, collision_boxes):
    for box in collision_boxes:
        if character.rect.colliderect(box):
            # Check if character's bottom is within the "allowable" range of the colliding box
            # if box.top < character.rect.bottom <= box.top + 8:  # Allow moving down halfway
            #     return True  # Draw character on top
            # elif box.bottom > character.rect.top >= box.bottom - 8:
            #     return True  # Draw character below

            # half of the character can move up to half of the size of the box
            if box.top < character.rect.bottom <= box.top + (box.height // 2):
                return False
            elif box.bottom > character.rect.top >= box.bottom - (box.height // 2):
                return True
    return False

def adjust_z_index_npc(character, other):
    if character.colliderect(other):
        if other.top < character.bottom <= other.top:
            return False
        elif other.bottom > character.top >= other.bottom:
            return True
    return False

def check_interaction(player, npcs):
    for npc in npcs:
        # Simple distance check for interaction
        if player.rect.colliderect(npc.rect.inflate(20, 20)):  # Inflate the NPC's rect for a larger interaction area
            return npc
    return None


def swirl_draw(frames, opacity=128):
    for frame in frames:
        frame.set_colorkey((248, 248, 248))
        frame.set_alpha(opacity)  # Set frame opacity
        frame_scaled = pygame.transform.scale(frame, (screen_width, screen_height))  # Scale frame
        screen.blit(frame_scaled, (0, 0))  # Draw frame
        pygame.time.wait(1000 // 24)  # Wait to simulate frame rate (24 FPS here)
        pygame.display.update()  # Update display

    # make a transparent black surface
    black_surface = pygame.Surface((screen_width, screen_height))
    black_surface.fill((0, 0, 0))
    # black_surface.set_alpha(opacity)
    screen.blit(black_surface, (0, 0))
    pygame.display.flip()
    # Optionally, pause for a moment before continuing
    pygame.time.wait(1000)  # Wait a second after the animation
    swirl_animation = False

def handle_debug():
    global debug_view_collision, debug_view_layer0, debug_view_layer1, debug_disable_collision
    if input_controller.is_action_pressed_once('debug_1'):
        debug_view_collision = not debug_view_collision
    if input_controller.is_action_pressed_once('debug_2'):
        debug_view_layer0 = not debug_view_layer0
    if input_controller.is_action_pressed_once('debug_3'):
        debug_view_layer1 = not debug_view_layer1
    if input_controller.is_action_pressed_once('debug_4'):
        debug_disable_collision = not debug_disable_collision

def handle_menu_interaction():
    global menu_open, status_menu_open, current_selection, menu_selection, status_menu_open, swirl_animation, game_state, interacting_npc
    interacting_npc = check_interaction(ness, npcs)
    # Menu Input
    if input_controller.is_action_pressed_once('action') and not menu_open:
        menu_open = True
        menu_selection = 0
        current_selection = menu_options[menu_selection]
    elif input_controller.is_action_pressed_once('back') and menu_open:
        menu_open = False
        status_menu_open = False
    elif input_controller.is_action_pressed_once('action') and menu_open:
        current_selection = menu_options[menu_selection]
        if current_selection == "Talk to" and check_interaction(ness, npcs):
            # Handle "Talk to" action
            # Proceed with the interaction logic, which you might encapsulate in a function
            if interacting_npc:
                if dialogue_box.is_visible:
                    dialogue_box.hide()
                else:
                    interacting_npc.interact()
                    cursor_vertical_sfx.play()
                    # dialogue_box.show_text(interacting_npc.dialogue)
            menu_open = False  # Close the menu

        elif current_selection == "Check" and check_interaction(ness, npcs):
            menu_open = False 
            if dialogue_box.is_visible:
                dialogue_box.hide()
            else:
                interacting_npc.check()
                cursor_vertical_sfx.play()
            if interacting_npc:
                if interacting_npc.pending_battle:
                    game_state = GAME_STATE_BATTLE
                    enter_battle_sfx = pygame.mixer.Sound('assets/sounds/enterbattle.wav')
                    enter_battle_sfx.set_volume(0.5)
                    enter_battle_sfx.play()
                    # wait for the sound to finish
                    swirl_animation = True

                    pygame.mixer.music.load(BATTLE_MUSIC_PATH)
                    pygame.mixer.music.play(-1)
                    # interacting_npc.pending_battle = False

        elif current_selection == "Status":
            # menu_open = False
            status_menu_open = True
        else:
            menu_open = False
            status_menu_open = False
            # Reset current_selection after handling the action
            current_selection = None
    elif input_controller.is_any_pressed_once() and status_menu_open:
        menu_open = False
        status_menu_open = False
    # Navigating Menu
    if menu_open:
        col = menu_selection % menu_columns
        row = menu_selection // menu_columns
        if input_controller.is_action_pressed_once('move_left'):
            col = max(col - 1, 0)
            cursor_horizontal_sfx.play()
        elif input_controller.is_action_pressed_once('move_right'):
            col = min(col + 1, menu_columns - 1)
            cursor_horizontal_sfx.play()
        elif input_controller.is_action_pressed_once('move_up'):
            row = max(row - 1, 0)
            cursor_vertical_sfx.play()
        elif input_controller.is_action_pressed_once('move_down'):
            row = min(row + 1, menu_rows - 1)
            cursor_vertical_sfx.play()
        elif input_controller.is_action_pressed_once('move_down'):
            menu_open = False
        # Calculate the new selection index based on the updated row and column
        new_selection = row * menu_columns + col
        # Ensure the new selection is within the bounds of the menu options
        menu_selection = min(new_selection, len(menu_options) - 1)
        current_selection = menu_options[menu_selection]  

def game_exploration():
    global game_state, swirl_animation, menu_open, status_menu_open, interacting_npc, dialogue_box, ness_sprite_index

    # Handle Camerea
    if input_controller.is_action_pressed('bump_r'):
        if input_controller.is_action_pressed_once('move_up'):  # Scroll up
            camera.zoom += 0.25
        elif input_controller.is_action_pressed_once('move_down'):  # Scroll down
            camera.zoom -= 0.25
            camera.zoom = max(0.25, camera.zoom)
    elif input_controller.is_action_pressed_once('zoom_in'):
        camera.zoom += 0.25
    elif input_controller.is_action_pressed_once('zoom_out'):
        camera.zoom -= 0.25
        camera.zoom = max(0.25, camera.zoom)
    # Handle Player Movement
    dx, dy = 0, 0
    velocity = 4 if input_controller.is_action_pressed('shift') else 1  # Example: LSHIFT or corresponding joystick button increases speed

    if input_controller.is_action_pressed('move_left'):
        dx -= velocity
    if input_controller.is_action_pressed('move_right'):
        dx += velocity
    if input_controller.is_action_pressed('move_up') and not input_controller.is_action_pressed('bump_r'):
        dy -= velocity
    if input_controller.is_action_pressed('move_down') and not input_controller.is_action_pressed('bump_r'):
        dy += velocity

    if input_controller.is_action_pressed_once('debug_5'):
        # print("ness_sprite_index", ness_sprite_index)
        ness_sprite_index += 1
        
        if ness_sprite_index == 5:
            ness_sprite_index = 0
        if ness_sprite_index == 0:
            ness.sprite_sheet = pygame.image.load('assets/sprites/ness_normal.png')
        if ness_sprite_index == 1:
            ness.sprite_sheet = pygame.image.load('assets/sprites/ness_naked.png')
        if ness_sprite_index == 2:
            ness.sprite_sheet = pygame.image.load('assets/sprites/ness_pajama.png')
        if ness_sprite_index == 3:
            ness.sprite_sheet = pygame.image.load('assets/sprites/ness_robot.png')
        if ness_sprite_index == 4:
            # missing the in-between idle sprites for lucas
            ness.sprite_sheet = pygame.image.load('assets/sprites/lucas_normal.png')
        ness.make_transparent(ness.sprite_sheet)
        ness.images = ness.load_images()

    # Apply Movement
    if not menu_open:
        ness.move(dx, dy, debug_disable_collision)  # Adjust movement logic as per your game's requirements
        camera.update(ness)  # Make sure the camera updates based on the player's new position

    # Draw Game Elements
    draw_everything()
    draw_debug()
    draw_menu()

    # NPC Interaction and Battle Initiation
    interacting_npc = check_interaction(ness, npcs)
    if interacting_npc:
        # Initiate battle if an NPC has a pending battle
        if interacting_npc.force_battle and interacting_npc.pending_battle:
            game_state = GAME_STATE_BATTLE
            pygame.mixer.Sound('assets/sounds/enterbattle.wav').play()
            swirl_animation = True
            pygame.mixer.music.load(BATTLE_MUSIC_PATH)
            pygame.mixer.music.play(-1)
            interacting_npc.pending_battle = False

    if swirl_animation:
        swirl_draw(swirl_frame_images, 128)

    if not interacting_npc or not dialogue_box.is_visible:
        dialogue_box.hide()
    dialogue_box.draw(screen)


# Game loop
while running:
    events = pygame.event.get()
    input_controller.process_events(events)
    sound_controller.process_events(events)
    
    if game_state == GAME_STATE_EXPLORATION:
        handle_menu_interaction()
        game_exploration()

    elif game_state == GAME_STATE_BATTLE:

        if battle_system is None or not battle_system.battle_active:
            battle_effects = []
            effects = ["horizontal_oscillation", "vertical_oscillation", "interleaved_oscillation", "palette_cycling", "background_scrolling"]
            battle_effects = random.sample(effects, k=random.randint(1, len(effects)))
            scroll_x=random.randint(0,1)
            scroll_y=random.randint(0,1)
            scroll_speed_x=random.randint(-3,3)
            scroll_speed_y=random.randint(-3,3)
            background_id = random.randint(1,327)
            print(battle_effects, scroll_x, scroll_y, scroll_speed_x, scroll_speed_y)
            battle_background = BattleBackground(f'assets/sprites/battle_backgrounds/{background_id}.png', battle_effects, screen_width, screen_height, scroll_x, scroll_y, scroll_speed_x, scroll_speed_y)
            
            battle_background_tfx = None
            if random.randint(0, 100) < 20:
                print("tfx")
                effects = ["horizontal_oscillation", "vertical_oscillation", "palette_cycling", "background_scrolling"]
                battle_effects = random.sample(effects, k=random.randint(1, len(effects)))
                scroll_x=random.randint(0,1)
                scroll_y=random.randint(0,1)
                scroll_speed_x=random.randint(-3,3)
                scroll_speed_y=random.randint(-3,3)
                battle_background_tfx = BattleBackground(f'assets/sprites/battle_backgrounds/{background_id}.png', battle_effects, screen_width, screen_height, scroll_x, scroll_y, scroll_speed_x, scroll_speed_y)

            battle_log = BattleLog(menu_font, screen_width, screen_height)
            battle_system = BattleSystem(screen, ness, [interacting_npc], battle_background, battle_log, screen_width, screen_height, battle_background_tfx)
            battle_system.start_battle()

        if input_controller.is_action_pressed_once('action'):
            if battle_system.is_player_turn:
                action = battle_menu_options[battle_menu.menu_selection]
                if action == "Bash":
                    hit = battle_system.player_command(action)
                    if hit:
                        pygame.mixer.Sound('assets/sounds/attack1.wav').play()
                        # battle_system.player_turn()
                        battle_system.flash_enemy_flag = True
                if action == "Run":
                    battle_system.player_command(action)
                # this is waiting for an action so the timer doesnt work cause its not looped
                if not battle_system.is_player_turn:
                    battle_system.enemy_turn()

        if input_controller.is_action_pressed_once('move_up'):
            battle_menu.handle_input('move_up')
        if input_controller.is_action_pressed_once('move_down'):
            battle_menu.handle_input('move_down')
        if input_controller.is_action_pressed_once('move_left'):
            battle_menu.handle_input('move_left')
        if input_controller.is_action_pressed_once('move_right'):
            battle_menu.handle_input('move_right')

        if input_controller.is_action_pressed_once('back'):
            battle_system.battle_active = False

        if not battle_system.is_player_turn:
            battle_system.handle_enemy_turn()
        battle_system.draw()

        if battle_system.battle_ongoing_flag:
            battle_menu.draw(screen)
        else:
            game_state = GAME_STATE_EXPLORATION
            pygame.mixer.music.load(ONETT_MUSIC_PATH)
            pygame.mixer.music.play(-1)
            battle_system.battle_ongoing_flag = False
            battle_system.end_battle()
            battle_system.battle_active = False
            interacting_npc = None
            swirl_animation = False

        if battle_system.flash_enemy_flag:
            original_sprite = battle_system.enemies[0].battle_sprite
            for _ in range(3):  # Flash 3 times
                battle_system.enemies[0].battle_sprite = pygame.Surface((0, 0))  # Make sprite invisible

                screen.fill((0, 0, 0))  # Clear screen
                battle_system.draw()
                battle_menu.draw(screen)
                battle_system.draw_enemy(battle_system.enemies[0])
                pygame.display.update()
                pygame.time.delay(100 // 3)
                
                battle_system.enemies[0].battle_sprite = original_sprite  # Restore sprite visibility

                screen.fill((0, 0, 0))  # Clear screen
                battle_system.draw()
                battle_menu.draw(screen)
                battle_system.draw_enemy(battle_system.enemies[0])
                pygame.display.update()
                pygame.time.delay(100 // 3)
            battle_system.flash_enemy_flag = False
        else:
            battle_system.draw_enemy(battle_system.enemies[0])

        if not battle_system.battle_ongoing_flag:
            game_state = GAME_STATE_EXPLORATION
            pygame.mixer.music.load(ONETT_MUSIC_PATH)
            pygame.mixer.music.play(-1)
            battle_system.battle_ongoing_flag = False
            battle_system.end_battle()
            battle_system.battle_active = False
            interacting_npc = None
            swirl_animation = False

        if battle_system.check_battle_end():
            battle_system.end_battle()
            interacting_npc = None
            swirl_animation = False
        
        pygame.display.flip()

    elif game_state == GAME_STATE_GAMEOVER:
        scaled_gameover_image = pygame.transform.scale(gameover_image, (screen_width, screen_height))
        screen.blit(scaled_gameover_image, (0, 0))
        pygame.time.wait(1000)

    # Clear the screen
    ctx.clear()

    # 1. Render your scene into scene_fbo
    scene_fbo.use()
    ctx.clear()  # Optionally clear if needed
    draw_everything()

    # Switch back to default framebuffer to draw the final image
    ctx.screen.use()
    ctx.clear()

    # 2. Extract bright parts from the scene
    bright_fbo.use()
    bright_vao.render()

    # 3. Apply Gaussian blur in two passes
    blur_fbo1.use()
    blur_program['horizontal'].value = True
    blur_vao.render()

    blur_fbo2.use()
    blur_program['horizontal'].value = False
    blur_vao.render()

    # 4. Blend the original scene with the blurred bright parts
    ctx.screen.use()
    blend_vao.render()

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
sys.exit()

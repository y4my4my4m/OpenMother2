import pygame
import sys
from character import Character
from npc import NPC
from camera import Camera
from utils.collision import load_collision_boxes
from dialoguebox import DialogueBox
from battle import BattleSystem, BattleMenu, BattleBackground, BattleLog
import random

pygame.init()

# Screen Configuration
FULLSCREEN = False

screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height), (pygame.FULLSCREEN if FULLSCREEN else 0) | pygame.DOUBLEBUF)
# detect screen resolution
# infoObject = pygame.display.Info()
# screen_width = infoObject.current_w
# screen_height = infoObject.current_h
# make it full screen
# screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

# Colors and FPS
BLACK = (0, 0, 0)
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
ness_stats = [20, 10, 5, 3, 4, 5]
ness = Character("Ness", 1000, 1500, 16, 24, 'assets/sprites/ness_normal.png', collision_boxes, ness_stats)  
velocity = 1

# Initialize Camera
camera = Camera(screen_width, screen_height, map_layer0_rect.width, map_layer0_rect.height)
# camera.zoom = 1.0
# camera.update(ness)  # Force the camera to center on Ness at startup

# Music
ONETT_MUSIC_PATH = 'assets/music/onett_snes.mp3'
BATTLE_MUSIC_PATH = 'assets/music/battle.mp3'

# Load and play exploration music by default
pygame.mixer.music.load(ONETT_MUSIC_PATH)
pygame.mixer.music.play(-1)

# Menu
menu_open = False
menu_selection = 0
menu_columns = 2
menu_rows = 3
current_selection = None

menu_font = pygame.font.Font('assets/fonts/earthbound-menu-extended.ttf', 24)
menu_options = ["Talk to", "Goods", "PSI", "Equip", "Check", "Status"]

# Sound
cursor_horizontal_sfx = pygame.mixer.Sound('assets/sounds/curshoriz.wav')
cursor_vertical_sfx = pygame.mixer.Sound('assets/sounds/cursverti.wav')

# Debug
debug_view_collision = False
debug_view_layer0 = False
debug_view_layer1 = False
debug_disable_collision = False
debug_font = pygame.font.Font('assets/fonts/earthbound-menu-extended.ttf', 12)

# NPCs
npcs = [
    NPC("RandomNPC1", 1020, 1500, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "Hello, adventurer!", ness, [15, 10, 3, 3, 2, 2], 149, True, None, 3, 4, "look_at_player", dialogue_box),
    NPC("RandomNPC2", 1620, 1872, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "Have you seen anything weird lately?", ness, [50, 20, 1, 3, 2, 2], 56, True, None, 1, 9, "look_at_player", dialogue_box),
    NPC("RandomNPC3", 1584, 1423, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "It's a beautiful day, isn't it?", ness, [20, 20, 2, 5, 7, 2], 167, True, None, 3, 6, "look_at_player", dialogue_box),
    NPC("RandomNPC4", 2154, 889, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "Beware of crows...", ness, [50, 20, 3, 5, 7, 2], 66, True, None, 3, 2, "look_at_player", dialogue_box),
    NPC("RandomNPC5", 1490, 1157, 16, 24, 'assets/sprites/npc_sprite.png', collision_boxes, "I lost my car, can you help me find it?", ness, [50, 20, 1, 7, 7, 2], 36, True, None, 3, 14, "look_at_player", dialogue_box)
]

# Battle
battle_menu_options = ["Bash", "Goods", "Auto Fight", "PSI", "Defend", "Run"]
battle_menu = BattleMenu(menu_font, battle_menu_options)

# Gameover
gameover_image = pygame.image.load('assets/sprites/gameover.png').convert_alpha()

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
        screen.blit(scaled_ness_image, ness_pos)
        # After that, draw the remaining parts of the environment
    else:
        # Draw the character first, then overlay parts of the environment
        screen.blit(scaled_ness_image, ness_pos)
        if not debug_view_layer1:
            screen.blit(scaled_map_image_layer1, blit_position_layer1)


    for npc in npcs:
        if npc.stats["hp"] > 0:
            npc.handle_behaviour()
            npc_image = npc.animate()
            npc_pos = (
                (npc.rect.x - camera.camera.x) * camera.zoom, 
                (npc.rect.y - camera.camera.y) * camera.zoom
            )
            scaled_npc_image = pygame.transform.scale(npc_image, (
                int(npc.rect.width * camera.zoom), 
                int(npc.rect.height * camera.zoom)
            ))
            
            screen.blit(scaled_npc_image, npc_pos)


def draw_debug():
    if debug_view_collision:
        # Render collision boxes for debugging
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
        menu_width, menu_height = 175, 45
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
        pygame.draw.rect(screen, (255, 255, 255), (menu_x, menu_y, menu_width, menu_height), 2)


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
            text = menu_font.render(option_text, True, (255, 255, 255))
            screen.blit(text, (item_x + 10, item_y + 10))

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

def check_interaction(player, npcs):
    for npc in npcs:
        # Simple distance check for interaction
        if player.rect.colliderect(npc.rect.inflate(20, 20)):  # Inflate the NPC's rect for a larger interaction area
            return npc
    return None

# Game loop
running = True
while running:
    if game_state == GAME_STATE_EXPLORATION:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    camera.zoom += 0.1
                elif event.button == 5:  # Scroll down
                    camera.zoom -= 0.1
                    camera.zoom = max(0.1, camera.zoom)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    velocity = 4
                elif event.key == pygame.K_SPACE:
                    # Toggle menu open/close
                    if menu_open:
                        # If the menu is already open, the Space key now confirms the selection
                        if current_selection == "Talk to" and check_interaction(ness, npcs):
                            # Handle "Talk to" action
                            menu_open = False  # Close the menu
                            # Proceed with the interaction logic, which you might encapsulate in a function
                            if interacting_npc:
                                if dialogue_box.is_visible:
                                    dialogue_box.hide()
                                else:
                                    interacting_npc.interact()
                                    cursor_vertical_sfx.play()

                        elif current_selection == "Check":
                            menu_open = False 
                            if dialogue_box.is_visible:
                                dialogue_box.hide()
                            else:
                                interacting_npc.check()
                                cursor_vertical_sfx.play()
                            if interacting_npc:
                                if interacting_npc.pending_battle:
                                    game_state = GAME_STATE_BATTLE
                                    pygame.mixer.Sound('assets/sounds/enterbattle.wav').play()
                                    # wait for the sound to finish
                                    pygame.time.wait(2000)
                                    pygame.mixer.music.load(BATTLE_MUSIC_PATH)
                                    pygame.mixer.music.play(-1)
                                    interacting_npc.pending_battle = False
                        else:
                            menu_open = False
                            # Reset current_selection after handling the action
                            current_selection = None
                    else:
                        if dialogue_box.is_visible:
                            dialogue_box.hide()
                        # Open the menu if it's not already open
                        menu_open = True
                        menu_selection = 0  # Optionally reset the menu selection index
                        current_selection = menu_options[menu_selection]  # Update current_selection based on menu_selection
                        cursor_vertical_sfx.play()

                elif event.key == pygame.K_1:
                    debug_view_collision = not debug_view_collision
                elif event.key == pygame.K_2:
                    debug_view_layer0 = not debug_view_layer0
                elif event.key == pygame.K_3:
                    debug_view_layer1 = not debug_view_layer1
                elif event.key == pygame.K_4:
                    debug_disable_collision = not debug_disable_collision

                if event.key == pygame.K_e:
                    print(f"{ness.x}, {ness.y}")
                    # interacting_npc = check_interaction(ness, npcs)
                    # cursor_horizontal_sfx.play()
                    # if interacting_npc:
                    #     if dialogue_box.is_visible:
                    #         dialogue_box.hide()
                    #     else:
                    #         interacting_npc.interact()
                    #         cursor_vertical_sfx.play()

                if menu_open:
                    col = menu_selection % menu_columns
                    row = menu_selection // menu_columns

                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        col = max(col - 1, 0)
                        cursor_horizontal_sfx.play()
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        col = min(col + 1, menu_columns - 1)
                        cursor_horizontal_sfx.play()
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        row = max(row - 1, 0)
                        cursor_vertical_sfx.play()
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        row = min(row + 1, menu_rows - 1)
                        cursor_vertical_sfx.play()
                    # Calculate the new selection index based on the updated row and column
                    new_selection = row * menu_columns + col
                    # Ensure the new selection is within the bounds of the menu options
                    menu_selection = min(new_selection, len(menu_options) - 1)
                    current_selection = menu_options[menu_selection]  

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    velocity = 1
        
        # Movement and animation update
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -velocity
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = velocity
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -velocity
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = velocity


        if not menu_open:
            ness.move(dx, dy, debug_disable_collision)
            animated_image = ness.animate()
            camera.update(ness)

        draw_everything()
        draw_debug()
        draw_menu()

        interacting_npc = check_interaction(ness, npcs)
        if not interacting_npc:
            dialogue_box.hide()
        dialogue_box.draw(screen)

    elif game_state == GAME_STATE_BATTLE:

        if battle_system is None or not battle_system.battle_active:
            # battle_system = BattleSystem(screen, ness, [interacting_npc], 51, "background_scrolling")
            battle_effects = []
            effects = ["horizontal_oscillation", "vertical_oscillation", "palette_cycling", "background_scrolling"]
            battle_effects = random.sample(effects, k=random.randint(1, len(effects)))
            scroll_x=random.randint(0,1)
            scroll_y=random.randint(0,1)
            scroll_speed_x=random.randint(-3,3)
            scroll_speed_y=random.randint(-3,3)
            battle_background = BattleBackground(f'assets/sprites/battle_backgrounds/{random.randint(1,327)}.png', battle_effects, scroll_x, scroll_y, scroll_speed_x, scroll_speed_y)
            battle_log = BattleLog(menu_font, screen_width, screen_height)
            battle_system = BattleSystem(screen, ness, [interacting_npc], battle_background, battle_log)
            battle_system.start_battle()

        while battle_system.battle_active:
            screen.fill((0, 0, 0))  # Clear screen
            battle_system.draw()
            if battle_system.battle_ongoing_flag:
                battle_menu.draw(screen)
            if battle_system.flash_enemy_flag:
                original_sprite = battle_system.enemies[0].battle_sprite
                for _ in range(3):  # Flash 3 times
                    battle_system.enemies[0].battle_sprite = pygame.Surface((0, 0))  # Make sprite invisible

                    screen.fill((0, 0, 0))  # Clear screen
                    battle_system.draw()
                    battle_menu.draw(screen)
                    battle_system.draw_enemy(battle_system.enemies[0])
                    pygame.display.flip()
                    clock.tick(FPS)
                    pygame.time.wait(100 // 3)
                    
                    battle_system.enemies[0].battle_sprite = original_sprite  # Restore sprite visibility

                    screen.fill((0, 0, 0))  # Clear screen
                    battle_system.draw()
                    battle_menu.draw(screen)
                    battle_system.draw_enemy(battle_system.enemies[0])
                    pygame.display.flip()
                    clock.tick(FPS)
                    pygame.time.wait(100 // 3)
                battle_system.flash_enemy_flag = False
            else:
                battle_system.draw_enemy(battle_system.enemies[0])
            pygame.display.flip()
            # Handle events specifically for the battle state
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    # battle_system.battle_active = False
                elif event.type == pygame.KEYDOWN:
                    if not battle_system.battle_ongoing_flag:
                        if battle_system.player_alive:
                            game_state = GAME_STATE_EXPLORATION
                            pygame.mixer.music.load(ONETT_MUSIC_PATH)
                            pygame.mixer.music.play(-1)
                            battle_system.battle_active = False
                            break
                        else:
                            game_state = GAME_STATE_GAMEOVER
                            pygame.mixer.music.load('assets/music/gameover.mp3')
                            pygame.mixer.music.play(-1)
                            battle_system.battle_active = False
                            break
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        battle_menu.handle_input(event.key)
                    elif event.key == pygame.K_SPACE:
                        if battle_system.is_player_turn:
                            action = battle_menu_options[battle_menu.menu_selection]
                            if action == "Bash":
                                hit = battle_system.player_command(action)
                                if hit:
                                    pygame.mixer.Sound('assets/sounds/attack1.wav').play()
                                    # battle_system.player_turn()
                                    battle_system.flash_enemy_flag = True
                        elif not battle_system.is_player_turn:
                            battle_system.enemy_turn()

                    elif event.key == pygame.K_ESCAPE:
                        battle_system.battle_active = False

                    battle_menu.handle_input(event.key)

            if battle_system.check_battle_end():
                battle_system.end_battle()
            pygame.time.wait(100)
    
    elif game_state == GAME_STATE_GAMEOVER:
        scaled_gameover_image = pygame.transform.scale(gameover_image, (screen_width, screen_height))
        screen.blit(scaled_gameover_image, (0, 0))
        pygame.time.wait(1000)
    # Update the display
    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
sys.exit()

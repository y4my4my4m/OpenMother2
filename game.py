import pygame
import sys
from character import Character
from camera import Camera

pygame.init()

# Screen Configuration
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors and FPS
BLACK = (0, 0, 0)
FPS = 60
clock = pygame.time.Clock()

# Load assets
onett_layer0 = pygame.image.load('assets/maps/onett_layer0.png')
map_layer0_rect = onett_layer0.get_rect()

onett_layer1 = pygame.image.load('assets/maps/onett_layer1.png')
map_layer1_rect = onett_layer1.get_rect()
# tile_size = 32  # Change this to the size of your tiles
# tiles_layer1 = [[onett_layer1.subsurface(pygame.Rect(x, y, tile_size, tile_size)) for x in range(0, onett_layer1.get_width() // tile_size * tile_size, tile_size)] for y in range(0, onett_layer1.get_height() // tile_size * tile_size, tile_size)]
collision_boxes = load_collision_boxes('assets/maps/onett_layer1_collision_boxes.json')

# Character
ness = Character(1000, 1500, 'assets/sprites/ness_normal.png')  # Adjusted for world position
velocity = 1

# Initialize Camera
camera = Camera(screen_width, screen_height, map_layer0_rect.width, map_layer0_rect.height)
# camera.zoom = 1.0
# camera.update(ness)  # Force the camera to center on Ness at startup

# Music
pygame.mixer.music.load('assets/music/onett.mp3')
pygame.mixer.music.play(-1)

# Menu
menu_open = False
menu_selection = 0
menu_font = pygame.font.Font('assets/fonts/earthbound-menu-extended.ttf', 24)
# Define menu options
menu_options = ["Talk to", "Goods", "PSI", "Equip", "Check", "Status"]

# Sound
cursor_horizontal_sfx = pygame.mixer.Sound('assets/sounds/curshoriz.wav')
cursor_vertical_sfx = pygame.mixer.Sound('assets/sounds/cursverti.wav')

def draw_everything():
    # Determine the visible area of the map, including a 100px outer bound
    visible_area = pygame.Rect(
        camera.camera.x - 100 / camera.zoom, 
        camera.camera.y - 100 / camera.zoom, 
        screen_width / camera.zoom + 200 / camera.zoom, 
        screen_height / camera.zoom + 200 / camera.zoom
    )
    visible_area.normalize()  # Ensure width and height are positive

    # Clamp the visible area to the map's bounds
    visible_area.clamp_ip(map_layer0_rect)

    # Extract the visible portion of the map
    visible_map_segment = onett_layer0.subsurface(visible_area)

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

    # Clear the screen and render the scaled map segment
    screen.fill(BLACK)
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

    # # Render the scaled map segment for layer 1
    if ness.rect.y > visible_area.y:
        # If player's Y-coordinate is greater, draw player on top of layer 1
        screen.blit(scaled_ness_image, ness_pos)
        screen.blit(scaled_map_image_layer1, blit_position_layer1)
    else:
        # If player's Y-coordinate is less, draw player below layer 1
        screen.blit(scaled_map_image_layer1, blit_position_layer1)
        screen.blit(scaled_ness_image, ness_pos)

    # screen.blit(scaled_ness_image, ness_pos)

    # Render collision boxes for debugging
    # for box in collision_boxes:
    #     # Transform box position based on camera view
    #     transformed_box = camera.apply(box)
    #     pygame.draw.rect(screen, (255, 0, 0), transformed_box, 1)  # Draw as red boxes

    # Render the tiles
    # for y, row in enumerate(tiles_layer1):
    #     for x, tile in enumerate(row):
    #         tile_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
    #         if ness.rect.y > tile_rect.y:
    #             # If player's Y-coordinate is greater, draw player on top of tile
    #             screen.blit(scaled_ness_image, ness_pos)
    #             screen.blit(tile, tile_rect.topleft)
    #         else:
    #             # If player's Y-coordinate is less, draw player below tile
    #             screen.blit(tile, tile_rect.topleft)
    #             screen.blit(scaled_ness_image, ness_pos)


# Game loop
running = True
while running:
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
                velocity = 2
            elif event.key == pygame.K_SPACE:
                menu_open = not menu_open
                menu_selection = 0

            if menu_open:
                if event.key == (pygame.K_LEFT or pygame.K_a):
                    menu_selection = (menu_selection - 1) % len(menu_options)
                    cursor_horizontal_sfx.play()
                elif event.key == (pygame.K_RIGHT or pygame.K_d):
                    menu_selection = (menu_selection + 1) % len(menu_options)
                    cursor_horizontal_sfx.play()
                elif event.key == (pygame.K_UP or pygame.K_w):
                    menu_selection = (menu_selection - 1) % len(menu_options)
                    cursor_vertical_sfx.play()
                elif event.key == (pygame.K_DOWN or pygame.K_s):
                    menu_selection = (menu_selection + 1) % len(menu_options)
                    cursor_vertical_sfx.play()
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
        ness.move(dx, dy)
        animated_image = ness.animate()
        camera.update(ness)

    draw_everything()

    if menu_open:
        # Define menu properties
        menu_width, menu_height = 400, 200
        menu_x, menu_y = (screen_width - menu_width) -20 , 20
        menu_color = BLACK

        # Draw menu
        pygame.draw.rect(screen, menu_color, pygame.Rect(menu_x, menu_y, menu_width, menu_height))


        # Calculate menu item dimensions
        item_width = menu_width // 2
        item_height = menu_height // 3

        # Render menu options
        for i, option in enumerate(menu_options):
            col = i % 2
            row = i // 2
            item_x = menu_x + col * item_width
            item_y = menu_y + row * item_height

            option_text = "> " + option if i == menu_selection else "   " + option

            text = menu_font.render(option_text, True, (255, 255, 255))
            screen.blit(text, (item_x + 56, item_y + 16))

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
sys.exit()

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
onett_map = pygame.image.load('assets/maps/onett.png')
map_rect = onett_map.get_rect()

# Character
ness = Character(1000, 1500, 'assets/sprites/ness_normal.png')  # Adjusted for world position
velocity = 1

# Initialize Camera
camera = Camera(screen_width, screen_height, map_rect.width, map_rect.height)
camera.zoom = 1.0
camera.update(ness)  # Force the camera to center on Ness at startup

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
    ness.move(dx, dy)
    animated_image = ness.animate()

    # Update the camera to follow Ness, considering the zoom
    camera.update(ness)

    # Clear the screen
    screen.fill(BLACK)

    # Calculate and apply the scaling and positioning for the world rendering
    visible_area, zoom_factor = camera.apply(map_rect)
    scaled_map_width, scaled_map_height = int(map_rect.width * camera.zoom), int(map_rect.height * camera.zoom)
    scaled_map_image = pygame.transform.scale(onett_map, (scaled_map_width, scaled_map_height))

    # Calculate the offset to center Ness on the screen
    offset_x = screen_width / 2 - (ness.rect.x * camera.zoom)
    offset_y = screen_height / 2 - (ness.rect.y * camera.zoom)

    # Adjust the map's position based on the camera zoom and Ness's position
    map_position = (offset_x - camera.camera.x * camera.zoom, offset_y - camera.camera.y * camera.zoom)

    # Draw the scaled map
    screen.blit(scaled_map_image, map_position)

    # For Ness, scale the sprite and calculate its position to be centered
    scaled_ness_image = pygame.transform.scale(ness.animate(), (int(ness.rect.width * camera.zoom), int(ness.rect.height * camera.zoom)))
    ness_position = (screen_width / 2 - scaled_ness_image.get_width() / 2, screen_height / 2 - scaled_ness_image.get_height() / 2)

    # Draw Ness
    screen.blit(scaled_ness_image, ness_position)
    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

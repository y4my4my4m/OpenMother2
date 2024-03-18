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
# camera.zoom = 1.0
# camera.update(ness)  # Force the camera to center on Ness at startup


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
    camera.update(ness)

    # Determine the visible area of the map, including a 100px outer bound
    visible_area = pygame.Rect(
        camera.camera.x - 100 / camera.zoom, 
        camera.camera.y - 100 / camera.zoom, 
        screen_width / camera.zoom + 200 / camera.zoom, 
        screen_height / camera.zoom + 200 / camera.zoom
    )
    visible_area.normalize()  # Ensure width and height are positive

    # Clamp the visible area to the map's bounds
    visible_area.clamp_ip(map_rect)

    # Extract the visible portion of the map
    visible_map_segment = onett_map.subsurface(visible_area)

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
    # Adjust map rendering to display the scaled map based on the zoom level
    scaled_map = pygame.transform.scale(onett_map, (int(map_rect.width * camera.zoom), int(map_rect.height * camera.zoom)))
    screen.blit(scaled_map, camera.apply(map_rect))
    
    ness_sprite = ness.animate()
    screen.blit(ness_sprite, camera.apply(ness))

    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
sys.exit()

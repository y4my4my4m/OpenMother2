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
    scaled_map_image = pygame.transform.scale(onett_map, (int(map_rect.width * zoom_factor), int(map_rect.height * zoom_factor)))

    # Blit the scaled map image adjusted for camera position
    screen.blit(scaled_map_image, visible_area.topleft)

    # Scale and blit Ness's animated image
    scaled_ness_image = pygame.transform.scale(animated_image, (int(animated_image.get_width() * zoom_factor), int(animated_image.get_height() * zoom_factor)))
    ness_world_pos = pygame.Rect(ness.rect.x - camera.camera.x, ness.rect.y - camera.camera.y, scaled_ness_image.get_width(), scaled_ness_image.get_height())
    screen.blit(scaled_ness_image, ness_world_pos.topleft)

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

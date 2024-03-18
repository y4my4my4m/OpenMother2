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
ness = Character(screen_width / 2, screen_height /2, 'assets/sprites/ness_normal.png')
velocity = 1

# Initialize Camera
camera = Camera(screen_width, screen_height, map_rect.width, map_rect.height)
scaled_map_image = pygame.transform.scale(onett_map, (int(map_rect.width * camera.zoom), int(map_rect.height * camera.zoom)))
last_zoom = camera.zoom
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
                camera.zoom = max(0.1, camera.zoom)  # Prevent zooming out too much
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_LSHIFT :
                velocity = 2
        elif event.type == pygame.KEYUP :
            if event.key == pygame.K_LSHIFT :
                velocity = 1
    # Movement
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

    # When drawing
    if camera.zoom != last_zoom:
        scaled_map_image = pygame.transform.scale(onett_map, (int(map_rect.width * camera.zoom), int(map_rect.height * camera.zoom)))
        last_zoom = camera.zoom
    map_rect_scaled, _ = camera.apply(map_rect)
    visible_area = pygame.Rect(camera.camera.x, camera.camera.y, screen_width / camera.zoom, screen_height / camera.zoom)

    if map_rect_scaled.colliderect(visible_area):
        # Render the map only if it collides with the visible area
        screen.blit(scaled_map_image, map_rect_scaled.topleft - pygame.Vector2(visible_area.topleft))

    scaled_ness_image = pygame.transform.scale(ness.animate(), (int(ness.rect.width * camera.zoom), int(ness.rect.height * camera.zoom)))
    ness_rect_scaled, _ = camera.apply(ness)
    screen.blit(scaled_ness_image, ness_rect_scaled.topleft)

    # Inside the game loop
    camera.update(ness)

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

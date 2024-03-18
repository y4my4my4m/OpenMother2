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

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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

    # Initialize Camera
    camera = Camera(screen_width, screen_height, map_rect.width, map_rect.height)

    # Inside the game loop
    camera.update(ness)

    # When drawing
    screen.blit(onett_map, camera.apply(map_rect))
    screen.blit(ness.animate(), camera.apply(ness))


    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

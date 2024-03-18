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
ness = Character(0, 0, 'assets/sprites/ness_normal.png')
velocity = 2

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_LEFT]:
        dx = -velocity
    if keys[pygame.K_RIGHT]:
        dx = velocity
    if keys[pygame.K_UP]:
        dy = -velocity
    if keys[pygame.K_DOWN]:
        dy = velocity
    ness.move(dx, dy)

    # Fill the screen

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

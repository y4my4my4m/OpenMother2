import pygame
import numpy as np

def create_gradient(width, height, color1, color2):
    """Create a vertical gradient between two colors"""
    gradient = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        blend = y / height
        gradient[y, :, :] = color1 * (1 - blend) + color2 * blend
    return pygame.surfarray.make_surface(gradient.swapaxes(0, 1))

def update_gradient(gradient_surf, tick, color_shift_speed=0.001):
    """Update the gradient colors based on a tick count"""
    color1 = np.array([np.sin(color_shift_speed * tick) * 127 + 128,
                       np.sin(color_shift_speed * tick + 2) * 127 + 128,
                       np.sin(color_shift_speed * tick + 4) * 127 + 128])
    color2 = -color1 + 255
    new_gradient = create_gradient(gradient_surf.get_width(), gradient_surf.get_height(), color1, color2)
    gradient_surf.blit(new_gradient, (0, 0))

pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
running = True
tick = 0

gradient_surf = create_gradient(640, 480, np.array([255, 0, 0]), np.array([0, 0, 255]))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_gradient(gradient_surf, tick)
    screen.blit(gradient_surf, (0, 0))

    pygame.display.flip()
    clock.tick(60)
    tick += 1

pygame.quit()

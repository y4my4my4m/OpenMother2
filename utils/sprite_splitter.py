import pygame
import os

def find_sprites_and_export(image_path, export_path, transparency_threshold=127):
    """
    Find sprites in an image based on non-transparent pixels and export each as a transparent PNG.
    :param image_path: Path to the image file.
    :param export_path: Path to export the PNG files.
    :param transparency_threshold: Alpha value below which pixels are considered transparent.
    """
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    image = pygame.image.load(image_path).convert_alpha()  # Ensure the image supports per-pixel alpha
    width, height = image.get_size()
    visited = set()
    sprite_counter = 0

    def is_transparent(x, y):
        """Check if a pixel is transparent."""
        return image.get_at((x, y))[3] < transparency_threshold

    def flood_fill(x, y):
        """Perform flood fill to find the bounds of a contiguous non-transparent area."""
        queue = [(x, y)]
        bounds = pygame.Rect(x, y, 1, 1)
        while queue:
            cx, cy = queue.pop(0)
            if not (0 <= cx < width and 0 <= cy < height) or (cx, cy) in visited or is_transparent(cx, cy):
                continue
            visited.add((cx, cy))
            bounds.union_ip(pygame.Rect(cx, cy, 1, 1))
            queue.extend([(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)])
        return bounds

    for x in range(width):
        for y in range(height):
            if (x, y) not in visited and not is_transparent(x, y):
                sprite = flood_fill(x, y)
                if sprite.width > 1 and sprite.height > 1:  # Filter out single-pixel "boxes"
                    # Create a new transparent surface for this collision box
                    box_surface = pygame.Surface((sprite.width, sprite.height), pygame.SRCALPHA)
                    box_surface.blit(image, (0, 0), sprite)
                    
                    # Save this surface as a PNG file
                    sprite_counter += 1
                    png_path = os.path.join(export_path, f"{sprite_counter}.png")
                    pygame.image.save(box_surface, png_path)

# Example usage
# Initialize Pygame
pygame.init()

# Set up a dummy display if necessary
pygame.display.set_mode((1, 1))

# Define the image path and where to save the exported PNG files
# image_path = '../assets/sprites/enemies.png'
image_path = '../assets/sprites/battle_backgrounds.png'
export_path = '../assets/sprites/battle_backgrounds/'

find_sprites_and_export(image_path, export_path)

# Cleanup Pygame
pygame.quit()

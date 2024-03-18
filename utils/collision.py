import pygame
import json

def find_collision_boxes(image_path, transparency_threshold=1):
    """
    Find collision boxes in an image based on non-transparent pixels.
    :param image_path: Path to the image file.
    :param transparency_threshold: Alpha value below which pixels are considered transparent.
    :return: List of pygame.Rect objects representing the bounding boxes for non-transparent areas.
    """
    image = pygame.image.load(image_path)
    width, height = image.get_size()
    visited = set()
    collision_boxes = []

    def is_transparent(x, y):
        """Check if a pixel is transparent."""
        return image.get_at((x, y))[3] <= transparency_threshold

    def flood_fill(x, y):
        """Perform flood fill to find the bounds of a contiguous non-transparent area."""
        queue = [(x, y)]
        bounds = pygame.Rect(x, y, 1, 1)
        while queue:
            cx, cy = queue.pop()
            for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited and not is_transparent(nx, ny):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
                    bounds.union_ip(pygame.Rect(nx, ny, 1, 1))
        return bounds

    for x in range(width):
        for y in range(height):
            if (x, y) not in visited and not is_transparent(x, y):
                visited.add((x, y))
                collision_box = flood_fill(x, y)
                collision_boxes.append(collision_box)

    return collision_boxes

def load_collision_boxes(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return [pygame.Rect(box['x'], box['y'], box['width'], box['height']) for box in data]

# Initialize Pygame
pygame.init()

# Example usage
collision_boxes = find_collision_boxes('../assets/maps/onett_layer1_col.png')
print(f"Found {len(collision_boxes)} collision boxes.")
# After finding collision boxes...
collision_boxes_data = [{'x': box.x, 'y': box.y, 'width': box.width, 'height': box.height} for box in collision_boxes]

# Specify the file path to export the data
output_file_path = 'tmp/onett_layer1_collision_boxes.json'

# Exporting to JSON
with open(output_file_path, 'w') as f:
    json.dump(collision_boxes_data, f)

print(f"Collision boxes data exported to {output_file_path}.")
# Cleanup Pygame
pygame.quit()

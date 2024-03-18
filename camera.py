import pygame

class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = map_width
        self.height = map_height

    def apply(self, entity):
        """Applies the camera offset to a game entity."""
        # Assuming 'entity' has a 'rect' attribute for entities
        if hasattr(entity, 'rect'):
            return entity.rect.move(self.camera.topleft)
        # Directly move the Rect if 'entity' is a Rect
        return entity.move(self.camera.topleft)

    def update(self, target):
        """Updates the camera position based on the target entity (e.g., the player character)."""
        x = -target.rect.x + int(self.camera.width / 2)
        y = -target.rect.y + int(self.camera.height / 2)

        # Limit scrolling to map size
        x = min(0, x)  # Left
        y = min(0, y)  # Top
        x = max(-(self.width - self.camera.width), x)  # Right
        y = max(-(self.height - self.camera.height), y)  # Bottom

        self.camera = pygame.Rect(x, y, self.camera.width, self.camera.height)

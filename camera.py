import pygame

class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.camera = pygame.Rect(1000, 1500, width, height)
        self.width = map_width
        self.height = map_height
        self.zoom = 1.0

    # def apply(self, entity):
    #     """Transforms an entity's position according to the camera."""
    #     return entity.rect.move(self.camera.topleft)

    def apply(self, entity):
        """Transforms an entity's or rect's position according to the camera."""
        if hasattr(entity, 'rect'):  # If the entity has a 'rect' attribute
            offset_rect = entity.rect.copy()
        else:  # If the entity is directly a Rect object
            offset_rect = entity.copy()

        # Adjust for camera position and zoom
        offset_rect.x = int((offset_rect.x - self.camera.x) * self.zoom)
        offset_rect.y = int((offset_rect.y - self.camera.y) * self.zoom)
        offset_rect.width = int(offset_rect.width * self.zoom)
        offset_rect.height = int(offset_rect.height * self.zoom)

        return offset_rect
    def update(self, target):
        """Centers the camera on the target, adjusted for zoom."""
        self.camera.x = target.rect.x + target.rect.w / 2 - self.camera.width / 2 / self.zoom
        self.camera.y = target.rect.y + target.rect.h / 2 - self.camera.height / 2 / self.zoom
        
        # Clamp the camera to ensure it doesn't move outside the map boundaries
        self.camera.x = max(min(self.camera.x, self.width - self.camera.width / self.zoom), 0)
        self.camera.y = max(min(self.camera.y, self.height - self.camera.height / self.zoom), 0)

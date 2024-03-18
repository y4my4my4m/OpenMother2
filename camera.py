import pygame
class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.camera = pygame.Rect(1000, 1500, width, height)  # Updated initial position
        self.width = map_width
        self.height = map_height
        self.zoom = 1.0  # Initial zoom level

    def apply(self, entity):
        """Applies the camera offset and zoom to a game entity or a Rect."""
        if hasattr(entity, 'rect'):  # If the entity has a 'rect' attribute
            rect = entity.rect
        else:  # If the entity is directly a Rect object
            rect = entity

        # Determine the entity's offset from the camera center
        center_offset_x = rect.x - self.camera.centerx
        center_offset_y = rect.y - self.camera.centery

        # Scale the offset by the zoom
        scaled_offset_x = center_offset_x * self.zoom
        scaled_offset_y = center_offset_y * self.zoom

        # Calculate the new position based on the scaled offset
        new_x = self.camera.centerx + scaled_offset_x
        new_y = self.camera.centery + scaled_offset_y

        # Adjust the position by the top left of the camera (for drawing relative to the screen)
        new_x -= self.camera.width / 2 * self.zoom
        new_y -= self.camera.height / 2 * self.zoom

        # Inflate the rect by the zoom level
        new_rect = rect.inflate(rect.width * (self.zoom - 1), rect.height * (self.zoom - 1))

        # Set the inflated rect's top-left to the new position
        new_rect.topleft = (new_x, new_y)

        return new_rect


    def update(self, target):
        """Updates the camera position based on the target entity (e.g., the player character)."""
        x = -target.rect.centerx + int(self.camera.width / 2 / self.zoom)
        y = -target.rect.centery + int(self.camera.height / 2 / self.zoom)
        
        # Limit scrolling to map size, adjusted by zoom
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width * self.zoom - self.camera.width), x)
        y = max(-(self.height * self.zoom - self.camera.height), y)

        self.camera = pygame.Rect(x, y, self.camera.width, self.camera.height)

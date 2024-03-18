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

        # Calculate scaled position based on the camera position and zoom level
        scaled_x = (rect.x - self.camera.x) * self.zoom
        scaled_y = (rect.y - self.camera.y) * self.zoom

        # Return the new position as a Rect, and the zoom as the scale factor
        return pygame.Rect(scaled_x, scaled_y, rect.width * self.zoom, rect.height * self.zoom), self.zoom



    def update(self, target):
        target_center = (target.rect.x + target.rect.w // 2, target.rect.y + target.rect.h // 2)
        camera_center = (self.camera.x + self.camera.width // 2, self.camera.y + self.camera.height // 2)

        # Calculate the difference
        dx = (target_center[0] - camera_center[0]) // 10  # Divide by 10 for a smoother transition
        dy = (target_center[1] - camera_center[1]) // 10

        # Update the camera's position gradually
        self.camera.x += dx
        self.camera.y += dy

        # Adjust bounds as before
        self.camera.x = min(max(self.camera.x, 0), self.width * self.zoom - self.camera.width)
        self.camera.y = min(max(self.camera.y, 0), self.height * self.zoom - self.camera.height)

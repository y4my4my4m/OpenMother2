import pygame

class Character:
    def __init__(self, x, y, filename, collision_boxes):
        self.x = x
        self.y = y
        # Load the sprite sheet, making non-transparent via color key
        self.sprite_sheet = pygame.image.load(filename)
        self.make_transparent(self.sprite_sheet)
        self.direction = 0  # 8 directions
        self.current_frame = 0
        self.images = self.load_images()
        self.rect = self.images[0][0].get_rect(topleft=(x, y))
        # Animation control
        self.last_update_time = pygame.time.get_ticks()
        self.frame_rate = 150  # milliseconds
        self.moving = False
        self.collision_boxes = collision_boxes  # Store collision data

    def make_transparent(self, image):
        # Set the color key to the top-left pixel's color, assuming it's the background
        transparent_color = image.get_at((0, 0))
        image.set_colorkey(transparent_color)

    def load_images(self):
        images = []
        frame_width, frame_height = 16, 24  # Adjust for your sprite size
        for i in range(8):  # 8 directions
            # Calculate the X position, considering 1px spacing and two frames per direction
            x_pos = i * (frame_width * 2)
            frames = []
            for j in range(2):  # 2 frames per direction
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                # Account for 1px space between frames
                frame.blit(self.sprite_sheet, (0, 0), (x_pos + j * frame_width, 0, frame_width, frame_height))
                frames.append(frame)
            images.append(frames)
        return images


    def animate(self):
        now = pygame.time.get_ticks()
        if self.moving:
            if now - self.last_update_time > self.frame_rate:
                self.last_update_time = now
                self.current_frame = (self.current_frame + 1) % 2
        else:
            self.current_frame = 0  # Reset to first frame if not moving

        return self.images[self.direction][self.current_frame]

    def move(self, dx, dy):
        # Proposed new position
        new_rect = self.rect.move(dx, dy)
        collision_happened = False

        for box in self.collision_boxes:
            if new_rect.colliderect(box):
                collision_happened = True
                if dy > 0 and self.rect.bottom <= box.top:  # Moving down
                    dy = max(0, box.top - self.rect.bottom)
                elif dy < 0 and self.rect.top >= box.bottom:  # Moving up
                    dy = min(0, box.bottom - self.rect.top)
                
                if dx > 0 and self.rect.right <= box.left:  # Moving right
                    dx = max(0, box.left - self.rect.right)
                elif dx < 0 and self.rect.left >= box.right:  # Moving left
                    dx = min(0, box.right - self.rect.left)

        # Check if the character is inside any collision box at the start
        if not collision_happened:
            inside_collision = any(self.rect.colliderect(box) for box in self.collision_boxes)
            if inside_collision:
                dx, dy = 0, 0  # Optionally, allow movement inside collisions

        # Apply movement
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        self.moving = dx != 0 or dy != 0

        # Determine direction based on movement, using adjusted dx and dy
        if dx > 0 and dy < 0:
            self.direction = 5  # Up-right
        elif dx > 0 and dy > 0:
            self.direction = 7  # Down-right
        elif dx < 0 and dy < 0:
            self.direction = 3  # Up-left
        elif dx < 0 and dy > 0:
            self.direction = 1  # Down-left
        elif dx > 0:
            self.direction = 6  # Right
        elif dx < 0:
            self.direction = 2  # Left
        elif dy < 0:
            self.direction = 4  # Up
        elif dy > 0:
            self.direction = 0  # Down
    # def move(self, dx, dy):
    #     self.x += dx
    #     self.y += dy
    #     self.rect.topleft = (self.x, self.y)
    #     self.moving = dx != 0 or dy != 0
    #     # Determine direction based on movement
    #     if dx > 0 and dy < 0:
    #         self.direction = 5  # Up-right
    #     elif dx > 0 and dy > 0:
    #         self.direction = 7  # Down-right
    #     elif dx < 0 and dy < 0:
    #         self.direction = 3  # Up-left
    #     elif dx < 0 and dy > 0:
    #         self.direction = 1  # Down-left
    #     elif dx > 0:
    #         self.direction = 6  # Right
    #     elif dx < 0:
    #         self.direction = 2  # Left
    #     elif dy < 0:
    #         self.direction = 4  # Up
    #     elif dy > 0:
    #         self.direction = 0  # Down

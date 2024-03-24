import pygame

class Character:
    def __init__(self, name, x, y, width, height, filename, collision_boxes, stats, inventory=None):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
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
        self.collision_from_top = False
        self.collision_from_bottom = False
        # Battle
        self.stats = {
            "hp": stats[0],
            "psi": stats[1],
            "attack": stats[2],
            "defense": stats[3],
            "speed": stats[4],
            "luck": stats[5],
        }
        # Menu
        self.menu_sprite = pygame.image.load('assets/sprites/menu/ness_menu_sprite.png')
        self.inventory = inventory if inventory is not None else {}
      
    def handle_behaviour(self):
        pass
    
    def make_transparent(self, image):
        # Set the color key to the top-left pixel's color, assuming it's the background
        transparent_color = image.get_at((0, 0))
        image.set_colorkey(transparent_color)

    def load_images(self):
        images = []
        frame_width, frame_height = self.width, self.height  # Adjust for your sprite size
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

    def move(self, dx, dy, debug_disable_collision):
        # Proposed new position
        character_rect = self.rect.move(dx, dy)
        collision_detected = False

        if not debug_disable_collision:
            for box in self.collision_boxes:
                if character_rect.colliderect(box):
                    collision_detected = True

                    # Handle vertical collisions
                    if dy > 0:  # Moving down
                        self.collision_from_top = True
                        dy = min(dy, box.top - self.rect.bottom)
                    elif dy < 0:  # Moving up
                        self.collision_from_bottom = True
                        dy = max(dy, box.bottom - self.rect.top)

            # If no collision was detected and player is moving away from the collision, reset flags
            if not collision_detected:
                if dy > 0 and self.collision_from_bottom:  # Moving down, was colliding from bottom
                    # Check if sufficiently moved away
                    if all(self.rect.bottom <= box.top for box in self.collision_boxes):
                        self.collision_from_bottom = False
                elif dy < 0 and self.collision_from_top:  # Moving up, was colliding from top
                    if all(self.rect.top >= box.bottom for box in self.collision_boxes):
                        self.collision_from_top = False

        # Apply the calculated movement
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        self.moving = dx != 0 or dy != 0

        # Update direction based on the final movement
        self.update_direction(dx, dy)


    def update_direction(self, dx, dy):
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

    def use_item(self, item):
        # Item usage logic
        pass

    def cast_psi(self, psi_power):
        # PSI power usage logic
        pass
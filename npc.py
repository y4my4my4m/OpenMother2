import pygame
from character import Character

class NPC(Character):
    def __init__(self, x, y, width, height, filename, collision_boxes, dialogue, direction=3, npc_index=0):
        super().__init__(x, y, width, height, filename, collision_boxes)
        self.dialogue = dialogue
        self.npc_index = npc_index  # This determines which NPC block to use
        self.direction = direction  # 0: up, 1: right, 2: down, 3: left
        self.images = self.load_images_for_npc()

    def interact(self):
        # This method is called when the player interacts with the NPC
        print(self.dialogue)

    def load_images_for_npc(self):
        images = [[] for _ in range(4)]  # Four directions
        frame_width, frame_height = self.width, self.height

        # Assuming the sprite sheet layout and spacings
        npcs_per_row = 4
        direction_spacing_col = 1
        direction_spacing_row = 0
        npc_spacing_row = 2
        npc_spacing_col = 2
        frame_spacing = 1

        # Calculate starting position for the NPC
        row_start = (self.npc_index // npcs_per_row) * (frame_height * 2 + direction_spacing_row + npc_spacing_row)
        col_start = (self.npc_index % npcs_per_row) * (frame_width * 4 + frame_spacing * 3 + npc_spacing_col)

        # Load images for each direction
        for dir_idx in range(4):  # 0: up, 1: right, 2: down, 3: left
            frames = []
            for frame_idx in range(2):  # Two frames per direction
                x_offset = frame_idx * (frame_width + frame_spacing)
                y_offset = 0
                if dir_idx > 1:  # Adjust for down and left directions
                    y_offset += frame_height + direction_spacing_row
                if dir_idx % 2 == 1:  # Adjust for right and left directions
                    x_offset += 2 * (frame_width + frame_spacing) + direction_spacing_col
                
                x = col_start + x_offset
                y = row_start + y_offset + (dir_idx // 2) * (direction_spacing_row + npc_spacing_row)
                frame = self.sprite_sheet.subsurface(x, y, frame_width, frame_height).convert_alpha()
                frames.append(frame)
            images[dir_idx] = frames

        return images

    def animate(self):
        # Animation logic remains unchanged
        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.frame_rate:
            self.last_update_time = now
            self.current_frame = (self.current_frame + 1) % len(self.images[self.direction])
        return self.images[self.direction][self.current_frame]

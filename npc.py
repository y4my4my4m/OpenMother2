import pygame
from character import Character
from dialoguebox import DialogueBox
from battle import BattleSystem
import math
class NPC(Character):
    def __init__(self, name, x, y, width, height, filename, collision_boxes, dialogue, player, stats, battle_sprite_id, is_enemy=False, inventory=None, direction=3, npc_index=0, behaviour="idle", dialogue_box=None):
        super().__init__(name, x, y, width, height, filename, collision_boxes, stats, inventory)
        self.dialogue = dialogue
        self.npc_index = npc_index  # This determines which NPC block to use
        self.direction = direction  # 0: up, 1: right, 2: down, 3: left
        self.images = self.load_images_for_npc()
        self.behaviour = behaviour
        self.player = player
        self.dialogue_box = dialogue_box
        self.is_enemy = is_enemy 
        self.battle_sprite_filename = f'assets/sprites/enemies/{battle_sprite_id}.png'
        self.battle_sprite = pygame.image.load(self.battle_sprite_filename).convert_alpha()
        self.pending_battle = False
        self.force_battle = False

    # def interact(self):
    #     # This method is called when the player interacts with the NPC
    #     # print(self.dialogue)

    #     if self.dialogue_box:
    #         self.dialogue_box.show_text(self.dialogue)

    def interact(self):
        # Standard NPC interaction
        if self.stats["hp"] <= 0:
            return
        print(self.dialogue)
        if self.dialogue_box:
            self.dialogue_box.show_text(self.dialogue)

    def check(self):
        if self.stats["hp"] <= 0:
            return
        if self.is_enemy:
            # Trigger battle sequence
            print("Encountered an enemy! Starting battle...")
            self.pending_battle = True
        else:
            # Standard NPC interaction
            print(self.dialogue)

    def handle_behaviour(self):
        if self.behaviour == "idle":
            # NPC does nothing
            pass
        # ...

        elif self.behaviour == "follow":
            # follows player
            if self.rect.inflate(300, 200).colliderect(self.player.rect):
                target_x = self.player.x
                target_y = self.player.y
                speed = 1.2 #self.stats["speed"]  # Adjust the speed as needed

                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx ** 2 + dy ** 2)

                if distance > speed:
                    ratio = speed / distance
                    x = dx * ratio
                    y = dy * ratio
                else:
                    x = dx
                    y = dy

                self.move(x, y, True)  # Ignore Collision
                self.direction = self.get_direction_to_player()
                # if touches player
                if self.rect.colliderect(self.player.rect):
                    self.check()
                    self.force_battle = True

        elif self.behaviour == "patrol":
            pass
        elif self.behaviour == "random":
            pass
        elif self.behaviour == "look_at_player":
            # Update direction to look at the player only if the player is within a certain range (inflate a copy of the rect box)
            if self.rect.inflate(100, 100).colliderect(self.player.rect):
                self.direction = self.get_direction_to_player()

    def get_direction_to_player(self):
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        if abs(dx) > abs(dy):
            if dx > 0:
                return 1  # Right
            else:
                return 3
        else:
            if dy > 0:
                return 2
            else:
                return 0

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

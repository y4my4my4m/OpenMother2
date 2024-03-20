import pygame
import random
import numpy as np
import math

pygame.init()
# fixme
screen_width = 1280
screen_height = 720
cursor_horizontal_sfx = pygame.mixer.Sound('assets/sounds/curshoriz.wav')
cursor_vertical_sfx = pygame.mixer.Sound('assets/sounds/cursverti.wav')
class BattleSystem:
    def __init__(self, screen, player, enemies, bg_image_id=25, bg_type='palette_cycling'):
        self.screen = screen
        self.player = player
        self.enemies = enemies
        # self.gui = BattleGUI(player, enemies)
        self.current_turn = 'player'
        self.battle_active = False
        self.bg_image_id = bg_image_id
        self.bg_type = bg_type
        self.bg = None

    def start_battle(self):
        self.battle_active = True
        self.bg = BattleBackground(f'assets/sprites/battle_backgrounds/{self.bg_image_id}.png', self.bg_type)
        self.bg.prepare()

    def draw(self, enemy):
        # Draw the enemy
        self.bg.draw(self.screen)
        self.bg.update()
        self.screen.blit(pygame.transform.scale(enemy.battle_sprite, (enemy.battle_sprite.get_width() * 3, enemy.battle_sprite.get_height() * 3)), (screen_width // 2 - enemy.battle_sprite.get_width() // 2, (screen_height // 2 - enemy.battle_sprite.get_height() // 2) - enemy.battle_sprite.get_height() // 2))
       
        # self.screen.blit(pygame.transform.scale(enemy.battle_sprite, (enemy.battle_sprite.get_width() * 3, enemy.battle_sprite.get_height() * 3)), (screen_width // 2 - enemy.battle_sprite.get_width() // 2, (screen_height // 2 - enemy.battle_sprite.get_height() // 2) - 140))

    def calculate_damage(self, attacker, defender):
        # Calculate critical hits and misses based on luck
        critical_chance = attacker.stats["luck"] - defender.stats["luck"] 
        if random.randint(1, 20) <= critical_chance + 1:
            damage = attacker.stats["attack"] * 2  # Critical hit
            print("Critical hit!")
        else:
            damage = attacker.stats["attack"] - random.randint(0, defender.stats["defense"])

        return max(damage, 1)  # Ensure minimum damage

    def player_turn(self):
        print("Player's turn.")
        # Implement player action choice here (attack, use item, PSI)
        # For simplicity, let's assume an attack action
        damage = self.calculate_damage(self.player, self.enemies[0])
        self.enemies[0].stats["hp"] -= damage
        print(f"Player dealt {damage} damage!")

    def enemy_turn(self):
        print("Enemy's turn.")
        # Simple enemy behavior for demonstration
        damage = self.calculate_damage(self.enemies[0], self.player)
        self.player.stats["hp"] -= damage
        print(f"Enemy dealt {damage} damage!")

    def check_battle_end(self):
        if self.player.stats["hp"] <= 0:
            print("Player defeated!")
            return True
        elif all(enemy.stats["hp"] <= 0 for enemy in self.enemies):
            print("Enemies defeated!")
            return True
        return False

    def end_battle(self):
        self.battle_active = False
        print("Battle ended.")

class BattleMenu:
    def __init__(self, font, menu_options):
        self.menu_options = menu_options
        self.current_selection = 0
        self.font = font
        self.menu_open = False
        self.menu_selection = 0
        self.menu_columns = 2
        self.menu_rows = 3
        self.menu_width, self.menu_height = 240, 160
        self.menu_x, self.menu_y = 20, 20

    def draw(self, screen):
        # Draw menu
        pygame.draw.rect(screen, (0, 0, 0), (self.menu_x, self.menu_y, self.menu_width, self.menu_height))
        pygame.draw.rect(screen, (255, 255, 255), (self.menu_x, self.menu_y, self.menu_width, self.menu_height), 2)


        # Calculate menu item dimensions
        item_width = self.menu_width // 2
        item_height = self.menu_height // 3

        # Render menu options
        for i, option in enumerate(self.menu_options):
            col = i % self.menu_columns
            row = i // self.menu_columns

            item_x = self.menu_x + col * (self.menu_width // self.menu_columns)
            item_y = self.menu_y + row * (self.menu_height // self.menu_rows)

            option_text = "> " + option if i == self.menu_selection else "   " + option
            text = self.font.render(option_text, True, (255, 255, 255))
            screen.blit(text, (item_x + 10, item_y + 10))

    def handle_input(self, key):
        # if self.menu_open:
        col = self.menu_selection % self.menu_columns
        row = self.menu_selection // self.menu_columns

        if key == pygame.K_LEFT or key == pygame.K_a:
            col = max(col - 1, 0)
            cursor_horizontal_sfx.play()
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            col = min(col + 1, self.menu_columns - 1)
            cursor_horizontal_sfx.play()
        elif key == pygame.K_UP or key == pygame.K_w:
            row = max(row - 1, 0)
            cursor_vertical_sfx.play()
        elif key == pygame.K_DOWN or key == pygame.K_s:
            row = min(row + 1, self.menu_rows - 1)
            cursor_vertical_sfx.play()
        # Calculate the new selection index based on the updated row and column
        new_selection = row * self.menu_columns + col
        # Ensure the new selection is within the bounds of the menu options
        self.menu_selection = min(new_selection, len(self.menu_options) - 1)
        self.current_selection = self.menu_options[self.menu_selection]
        return self.menu_selection
        # cursor_vertical_sfx.play()
        # if key == pygame.K_UP or key == pygame.K_w:
        #     self.current_selection = (self.current_selection - 1) % len(self.menu_options)
        # elif key == pygame.K_DOWN or key == pygame.K_s:
        #     self.current_selection = (self.current_selection + 1) % len(self.menu_options)
        # return self.current_selection


background_types = [
    "palette_cycling",
    "background_scrolling",
    "horizontal_oscillation",
    "vertical_oscillation",
    "interleaved_oscillation",
    "transparency"
]


class BattleBackground:
    def __init__(self, filename, effect_types):
        self.original_image = pygame.image.load(filename)
        self.image = self.original_image.copy()  # Work on a copy for manipulation
        self.effect_types = effect_types
        self.palette = None
        self.palette_index = 0

        # For scrolling effect
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_speed_x = 2
        self.scroll_speed_y = 0

        # For oscillation effect
        self.oscillation_phase = 0

    def prepare(self):
        arr = pygame.surfarray.array3d(self.original_image)
        self.palette = np.unique(arr.reshape(-1, arr.shape[2]), axis=0)
    
    def update(self):
        # Update the oscillation phase for oscillation effects
        self.oscillation_phase += 0.2

    def draw(self, screen):
        # Reset the image to the original before applying effects
        image_for_frame = self.original_image.copy()
        
        # Apply each effect in sequence
        for effect_type in self.effect_types:
            if effect_type == "palette_cycling":
                self.apply_palette_cycling(image_for_frame)
            elif effect_type == "horizontal_oscillation":
                image_for_frame = self.apply_horizontal_oscillation(image_for_frame)
            elif effect_type == "vertical_oscillation":
                image_for_frame = self.apply_vertical_oscillation(image_for_frame)
        
        # After applying effects, scale and blit to the screen
        screen.blit(pygame.transform.scale(image_for_frame, (screen_width, screen_height)), (0, 0))


    def apply_palette_cycling(self, image):
        # Direct pixel manipulation to simulate palette cycling
        arr = pygame.surfarray.array3d(self.original_image)
        result_arr = arr.copy()
        for i, color in enumerate(self.palette[:-1]):  # Skip the last color to avoid index out of range
            result_arr[(arr == self.palette[i]).all(axis=-1)] = self.palette[i + 1]
        pygame.surfarray.blit_array(self.image, result_arr)

    def apply_horizontal_oscillation(self, image):
        arr = pygame.surfarray.array3d(image)
        oscillated_arr = np.zeros_like(arr)

        wave_amplitude = 10  # How far we want our wave to move
        wave_frequency = 0.1  # How frequent the waves are

        for y in range(arr.shape[1]):  # Iterate over each row
            shift = int(wave_amplitude * math.sin(wave_frequency * y + self.oscillation_phase))
            oscillated_arr[:, y, :] = np.roll(arr[:, y, :], shift, axis=0)

        pygame.surfarray.blit_array(image, oscillated_arr)
        return image


    def apply_vertical_oscillation(self, image):
        arr = pygame.surfarray.array3d(image)
        oscillated_arr = np.zeros_like(arr)

        wave_amplitude = 10  # How far we want our wave to move
        wave_frequency = 0.025  # How frequent the waves are

        for x in range(arr.shape[0]):  # Iterate over each column
            shift = int(wave_amplitude * math.sin(wave_frequency * x + self.oscillation_phase))
            oscillated_arr[x, :, :] = np.roll(arr[x, :, :], shift, axis=0)

        pygame.surfarray.blit_array(image, oscillated_arr)
        return image

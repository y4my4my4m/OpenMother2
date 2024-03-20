import pygame
import random
import numpy as np

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

        # Main battle loop
        # while self.battle_active:
        #     self.screen.fill((0, 0, 0))  # Clear screen
        #     self.draw(self.enemies[0])
        #     # pygame.display.flip()  # Update the display
            
        #     # Event handling simplified for demonstration
        #     for event in pygame.event.get():
        #         if event.type == pygame.KEYDOWN:
        #             # Example key bindings for demo purposes
        #             if event.key == pygame.K_SPACE:
        #                 self.player_turn()
        #                 self.enemy_turn()
        #             elif event.key == pygame.K_ESCAPE:
        #                 self.battle_active = False

        #     # # Additional game loop logic here
        #     self.check_battle_end()
        #     pygame.time.wait(100)  # Short delay for demonstration

    def draw(self, enemy):
        # Draw the enemy
        self.bg.draw(self.screen)
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
        # for i, option in enumerate(self.menu_options):
        #     color = (255, 255, 255) if i == self.current_selection else (100, 100, 100)
        #     text_surf = self.font.render(option, True, color)
        #     screen.blit(text_surf, (50, 50 + i * 30))
        # Define menu properties
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
    def __init__(self, filename, effect_type):
        self.original_image = pygame.image.load(filename)
        self.image = self.original_image.copy()  # Work on a copy for manipulation
        self.effect_type = effect_type
        self.palette = None
        self.palette_index = 0

        # For scrolling effect
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_speed_x = 2
        self.scroll_speed_y = 0

    def prepare(self):
        if self.effect_type == "palette_cycling":
            # Extract unique colors
            arr = pygame.surfarray.array3d(self.original_image)
            self.palette = np.unique(arr.reshape(-1, arr.shape[2]), axis=0)
        elif self.effect_type == "background_scrolling":
            arr = pygame.surfarray.array3d(self.original_image)
            self.palette = np.unique(arr.reshape(-1, arr.shape[2]), axis=0)
            self.scroll_x = 0
            self.scroll_y = 0
    
    def draw(self, screen):
        if self.effect_type == "palette_cycling":
            # Cycle the palette
            self.palette = np.roll(self.palette, shift=-1, axis=0)
            self.apply_palette_cycling()
        elif self.effect_type == "background_scrolling":
            self.palette = np.roll(self.palette, shift=-1, axis=0)
            self.apply_palette_cycling()
            # self.apply_background_scrolling(screen)
        screen.blit(pygame.transform.scale(self.image, (screen_width, screen_height)), (0, 0))


    def apply_palette_cycling(self):
        # Direct pixel manipulation to simulate palette cycling
        arr = pygame.surfarray.array3d(self.original_image)
        result_arr = arr.copy()
        for i, color in enumerate(self.palette[:-1]):  # Skip the last color to avoid index out of range
            result_arr[(arr == self.palette[i]).all(axis=-1)] = self.palette[i + 1]
        pygame.surfarray.blit_array(self.image, result_arr)

    def apply_background_scrolling(self, screen):
        # Scroll the background
        self.scroll_x = (self.scroll_x + self.scroll_speed_x) % self.image.get_width()
        self.scroll_y = (self.scroll_y + self.scroll_speed_y) % self.image.get_height()
        # Calculate the rectangle areas for the split
        rect1 = pygame.Rect(self.scroll_x, self.scroll_y, self.image.get_width() - self.scroll_x, self.image.get_height() - self.scroll_y)
        rect2 = pygame.Rect(0, 0, self.scroll_x, self.scroll_y)
        # Blit the scrolled sections
        screen.blit(self.image.subsurface(rect1), (0, 0))
        screen.blit(self.image.subsurface(rect2), (rect1.width, rect1.height))
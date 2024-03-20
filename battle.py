import pygame
import random
import numpy as np

pygame.init()
# fixme
screen_width = 1280
screen_height = 720
cursor_vertical_sfx = pygame.mixer.Sound('assets/sounds/cursverti.wav')
class BattleSystem:
    def __init__(self, screen, player, enemies):
        self.screen = screen
        self.player = player
        self.enemies = enemies
        # self.gui = BattleGUI(player, enemies)
        self.current_turn = 'player'
        self.battle_active = False
        self.bg = None

    def start_battle(self):
        self.battle_active = True
        self.bg = BattleBackground('assets/sprites/battle_backgrounds/25.png', 'palette_cycling')
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

    def draw(self, screen):
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 255) if i == self.current_selection else (100, 100, 100)
            text_surf = self.font.render(option, True, color)
            screen.blit(text_surf, (50, 50 + i * 30))

    def handle_input(self, key):
        cursor_vertical_sfx.play()
        if key == pygame.K_UP or key == pygame.K_w:
            self.current_selection = (self.current_selection - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.current_selection = (self.current_selection + 1) % len(self.menu_options)
        return self.current_selection


background_types = [
    "palette_cycling",
    "background_scrolling",
    "horizonttal_oscillation",
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

    def prepare(self):
        if self.effect_type == "palette_cycling":
            # Extract unique colors
            arr = pygame.surfarray.array3d(self.original_image)
            self.palette = np.unique(arr.reshape(-1, arr.shape[2]), axis=0)
    
    def draw(self, screen):
        if self.effect_type == "palette_cycling":
            # Cycle the palette
            self.palette = np.roll(self.palette, shift=-1, axis=0)
            self.apply_palette_cycling()
        # mod_bg = pygame.transform.scale(self.image, (screen_width, screen_height), screen)
        # screen.blit(mod_bg, (0, 0))
        screen.blit(pygame.transform.scale(self.image, (screen_width, screen_height)), (0, 0))
       

    def apply_palette_cycling(self):
        # Direct pixel manipulation to simulate palette cycling
        arr = pygame.surfarray.array3d(self.original_image)
        result_arr = arr.copy()
        for i, color in enumerate(self.palette[:-1]):  # Skip the last color to avoid index out of range
            result_arr[(arr == self.palette[i]).all(axis=-1)] = self.palette[i + 1]
        pygame.surfarray.blit_array(self.image, result_arr)
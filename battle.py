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
battle_hud_box = pygame.image.load('assets/sprites/battle_hud_box.png')
class BattleSystem:
    def __init__(self, screen, player, enemies, bg, log):
        self.screen = screen
        self.player = player
        self.enemies = enemies
        # self.gui = BattleGUI(player, enemies)
        self.current_turn = 'player'
        self.battle_active = False
        self.bg = bg
        self.battle_log = log
        self.is_player_turn = True
        self.flash_enemy_flag = False
        self.player_alive = True
        self.battle_ongoing_flag = True

    def start_battle(self):
        self.battle_active = True
        self.bg.prepare()

    def draw_enemy(self, enemy):
        if self.battle_ongoing_flag:
            self.screen.blit(pygame.transform.scale(enemy.battle_sprite, (enemy.battle_sprite.get_width() * 3, enemy.battle_sprite.get_height() * 3)), (screen_width // 2 - enemy.battle_sprite.get_width() // 2, (screen_height // 2 - enemy.battle_sprite.get_height() // 2) - enemy.battle_sprite.get_height() // 2))
   
    def draw(self):
        self.bg.draw(self.screen)
        self.bg.update()
        self.battle_log.draw(self.screen)
        self.draw_hud()

    def draw_hud(self):
        self.screen.blit(pygame.transform.scale(battle_hud_box, (battle_hud_box.get_width() * 2, battle_hud_box.get_height() * 2)), (screen_width // 2 - battle_hud_box.get_width() // 2, (screen_height - battle_hud_box.get_height()) - battle_hud_box.get_height() - 40 ))
        # display player's name
        player_name_text = pygame.font.Font('assets/fonts/earthbound-menu-extended.ttf', 24).render(f"{self.player.name}", True, (0, 0, 0))
        self.screen.blit(player_name_text, (screen_width // 2 - battle_hud_box.get_width() // 2 + 20, (screen_height - battle_hud_box.get_height()) - battle_hud_box.get_height() - 40 + 15))
        # display player HP
        player_hp_text = pygame.font.Font('assets/fonts/earthbound-menu-extended.ttf', 24).render(f"{self.player.stats['hp']}", True, (0, 0, 0))
        self.screen.blit(player_hp_text, (screen_width // 2 - battle_hud_box.get_width() // 2 + 70, (screen_height - battle_hud_box.get_height()) - battle_hud_box.get_height() - 40 + 45))
        # display player PSI
        player_psi_text = pygame.font.Font('assets/fonts/earthbound-menu-extended.ttf', 24).render(f"{self.player.stats['psi']}", True, (0, 0, 0))
        self.screen.blit(player_psi_text, (screen_width // 2 - battle_hud_box.get_width() // 2 + 70, (screen_height - battle_hud_box.get_height()) - battle_hud_box.get_height() - 40 + 75))


    def calculate_damage(self, attacker, defender):
        # Calculate critical hits and misses based on luck
        critical_hit = False
        critical_chance = attacker.stats["luck"] - defender.stats["luck"] 
        if random.randint(1, 20) <= critical_chance + 1:
            pygame.mixer.Sound('assets/sounds/smaaash.wav').play()
            damage = attacker.stats["attack"] * 2  # Critical hit
            critical_hit = True
        else:
            pygame.mixer.Sound('assets/sounds/bash.wav').play()
            damage = attacker.stats["attack"] - random.randint(0, defender.stats["defense"])
    
        damage = max(damage, 0)  # Ensure minimum damage
        if damage > 0:
            if critical_hit:
                self.battle_log.add_message(f"{attacker.name} dealt {damage} critical damage!")
                self.battle_log.add_message("Smaaash!")
            else:
                self.battle_log.add_message(f"{attacker.name} dealt {damage} damage!")
        else:
            pygame.mixer.Sound('assets/sounds/miss.wav').play()
            self.battle_log.add_message(f"{attacker.name} missed!")

        return damage


    def calculate_damage_enemy(self, attacker, defender):
        # Calculate critical hits and misses based on luck
        critical_hit = False
        critical_chance = attacker.stats["luck"] - defender.stats["luck"] 
        if random.randint(1, 20) <= critical_chance + 1:
            pygame.mixer.Sound('assets/sounds/smaaash.wav').play()
            damage = attacker.stats["attack"] * 2  # Critical hit
            critical_hit = True
        else:
            pygame.mixer.Sound('assets/sounds/enemyhit.wav').play()
            damage = attacker.stats["attack"] - random.randint(0, defender.stats["defense"])
    
        damage = max(damage, 0)  # Ensure minimum damage
        if damage > 0:
            if critical_hit:
                self.battle_log.add_message(f"{attacker.name} dealt {damage} critical damage!")
                self.battle_log.add_message("Smaaash!")
            else:
                self.battle_log.add_message(f"{attacker.name} dealt {damage} damage!")
        else:
            pygame.mixer.Sound('assets/sounds/miss.wav').play()
            self.battle_log.add_message(f"{attacker.name} missed!")

        return damage

    def player_command(self, action):
        # attacks by default
        self.battle_log.add_message(f"{self.player.name} attacks!")
        damage = self.calculate_damage(self.player, self.enemies[0])
        self.enemies[0].stats["hp"] -= damage
        self.is_player_turn = False
        return True

    def player_turn(self):
        if not self.is_player_turn:
            return 
        self.battle_log.add_message(f"{self.player.name}'s turn")

    def enemy_turn(self):
        if self.is_player_turn:
            return
        pygame.mixer.Sound('assets/sounds/enemyattack.wav').play()
        self.battle_log.add_message(f"{self.enemies[0].name}'s turn.")
        # attacks by default
        self.battle_log.add_message(f"{self.enemies[0].name} attacks!")
        damage = self.calculate_damage_enemy(self.enemies[0], self.player)
        self.player.stats["hp"] -= damage
        self.is_player_turn = True

    def check_battle_end(self):
        if self.player.stats["hp"] <= 0:
            return True
        elif all(enemy.stats["hp"] <= 0 for enemy in self.enemies):
            return True
        return False

    def end_battle(self):
        if self.battle_ongoing_flag:
            if self.player_alive:
                self.battle_log.add_message(f"{self.enemies[0].name} defeated!")
                pygame.mixer.Sound('assets/sounds/enemydie.wav').play()
                pygame.time.delay(200)
                pygame.mixer.music.load('assets/music/win.mp3')
                pygame.mixer.music.play(-1)
                self.battle_log.add_message("You won!")
                self.battle_ongoing_flag = False

            else:
                self.battle_log.add_message(f"{player.name} passed out!")
                self.player_alive = False
                pygame.mixer.Sound('assets/sounds/die.wav').play()
                self.battle_ongoing_flag = False


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

        new_selection = row * self.menu_columns + col
        self.menu_selection = min(new_selection, len(self.menu_options) - 1)


class BattleLog:
    def __init__(self, font, screen_width, screen_height):
        self.font = font
        self.messages = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.log_height = 230  # Height of the log area
        self.message_limit = 6  # Max number of messages to display at once

    def add_message(self, message):
        """Add a message to the battle log queue."""
        print(message)
        self.messages.append(message)
        # self.log_height += 20
        if len(self.messages) > self.message_limit:
            self.messages.pop(0)  # Remove the oldest message

    def draw(self, screen):
        if len(self.messages) == 0:
            return
        """Draw the battle log messages to the screen."""
        y_offset = self.screen_height - self.log_height # Start drawing from the bottom
        # draw the log box
        pygame.draw.rect(screen, (16, 16, 16), (20, y_offset - 180, 350, self.log_height))
        pygame.draw.rect(screen, (255,255,255), (20, y_offset - 180, 350, self.log_height), 2)
        for message in reversed(self.messages):
            if message == "Smaaash!":
                smash_image = pygame.image.load('assets/sprites/smash.png')
                screen.blit(smash_image, (40, y_offset + 10))
                y_offset -= smash_image.get_height() + 10
            elif message == "You won!":
                victory_image = pygame.image.load('assets/sprites/you_won.png')
                screen.blit(victory_image, (40, y_offset + 16))
                y_offset -= victory_image.get_height() + 10
            else:
                text_surface = self.font.render(message, True, (255, 255, 255))
                screen.blit(text_surface, (40, y_offset))
                y_offset -= text_surface.get_height()  # Move up for the next message


class BattleBackground:
    def __init__(self, filename, effect_types, scroll_x=0, scroll_y=0, scroll_speed_x=2, scroll_speed_y=0):
        self.original_image = pygame.image.load(filename)
        self.image = self.original_image.copy()  # Work on a copy for manipulation
        self.effect_types = effect_types
        self.palette = None
        self.palette_index = 0

        # For scrolling effect
        self.scroll_x = scroll_x
        self.scroll_y = scroll_y
        self.scroll_speed_x = scroll_speed_x
        self.scroll_speed_y = scroll_speed_y

        # For oscillation effect
        self.oscillation_vertical_phase = 0
        self.oscillation_horizontal_phase = 0

    def prepare(self):
        arr = pygame.surfarray.array3d(self.original_image)
        self.palette = np.unique(arr.reshape(-1, arr.shape[2]), axis=0)
    
    def update(self):
        # Update the oscillation phase for oscillation effects
        self.oscillation_vertical_phase += 0.2
        self.oscillation_horizontal_phase += 0.4

    def draw(self, screen):
        # Reset the image to the original before applying effects
        image_for_frame = self.original_image.copy()
        
        # Apply each effect in sequence
        for effect_type in self.effect_types:
            if effect_type == "palette_cycling":
                image_for_frame = self.apply_palette_cycling(image_for_frame)
            elif effect_type == "horizontal_oscillation":
                image_for_frame = self.apply_horizontal_oscillation(image_for_frame)
            elif effect_type == "vertical_oscillation":
                image_for_frame = self.apply_vertical_oscillation(image_for_frame)
            elif effect_type == "background_scrolling":
                image_for_frame = self.apply_background_scrolling(image_for_frame)

        # After applying effects, scale and blit to the screen
        screen.blit(pygame.transform.scale(image_for_frame, (screen_width, screen_height)), (0, 0))


    def apply_palette_cycling(self, image):
        # Direct pixel manipulation to simulate palette cycling
        arr = pygame.surfarray.array3d(image)
        result_arr = arr.copy()
        for i, color in enumerate(self.palette[:-1]):  # Skip the last color to avoid index out of range
            result_arr[(arr == self.palette[i]).all(axis=-1)] = self.palette[i + 1]
        pygame.surfarray.blit_array(image, result_arr)
        return image

    def apply_horizontal_oscillation(self, image):
        arr = pygame.surfarray.array3d(image)
        oscillated_arr = np.zeros_like(arr)

        wave_amplitude = 10  # How far we want our wave to move
        wave_frequency = 0.1  # How frequent the waves are

        for y in range(arr.shape[1]):  # Iterate over each row
            shift = int(wave_amplitude * math.sin(wave_frequency * y + self.oscillation_horizontal_phase))
            oscillated_arr[:, y, :] = np.roll(arr[:, y, :], shift, axis=0)

        pygame.surfarray.blit_array(image, oscillated_arr)
        return image


    def apply_vertical_oscillation(self, image):
        arr = pygame.surfarray.array3d(image)
        oscillated_arr = np.zeros_like(arr)

        wave_amplitude = 10  # How far we want our wave to move
        wave_frequency = 0.025  # How frequent the waves are

        for x in range(arr.shape[0]):  # Iterate over each column
            shift = int(wave_amplitude * math.sin(wave_frequency * x + self.oscillation_vertical_phase))
            oscillated_arr[x, :, :] = np.roll(arr[x, :, :], shift, axis=0)

        pygame.surfarray.blit_array(image, oscillated_arr)
        return image

    def apply_background_scrolling(self, image):
        arr = pygame.surfarray.array3d(image)
        scrolled_arr = np.zeros_like(arr)

        self.scroll_x = (self.scroll_x + self.scroll_speed_x * self.scroll_x) % arr.shape[0]
        self.scroll_y = (self.scroll_y + self.scroll_speed_y * self.scroll_y) % arr.shape[1]

        # Horizontal Scrolling
        if self.scroll_x != 0:
            part1_x = self.scroll_x
            part2_x = arr.shape[0] - self.scroll_x
            scrolled_arr[:part2_x] = arr[part1_x:]
            scrolled_arr[part2_x:] = arr[:part1_x]

        # Vertical Scrolling
        if self.scroll_y != 0:
            part1_y = self.scroll_y
            part2_y = arr.shape[1] - self.scroll_y
            scrolled_arr[:, :part2_y] = scrolled_arr[:, part1_y:]
            scrolled_arr[:, part2_y:] = scrolled_arr[:, :part1_y]

        pygame.surfarray.blit_array(image, scrolled_arr)
        return image

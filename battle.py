import pygame
import random
import numpy as np
import math
import time
from sfx import ENEMY_ATTACK_SOUND_EVENT

pygame.init()
# fixme
# screen_width = 1280
# screen_height = 720
cursor_horizontal_sfx = pygame.mixer.Sound('assets/sounds/curshoriz.wav')
cursor_vertical_sfx = pygame.mixer.Sound('assets/sounds/cursverti.wav')
battle_hud_box = pygame.image.load('assets/sprites/battle_hud_box.png')

class BattleSystem:
    def __init__(self, screen, player, enemies, bg, log, screen_width, screen_height, bg_tfx=None):
        self.screen = screen
        self.player = player
        self.enemies = enemies
        # self.gui = BattleGUI(player, enemies)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_turn = 'player'
        self.battle_active = False
        self.bg = bg
        self.bg_tfx = bg_tfx
        self.battle_log = log
        self.is_player_turn = True
        self.flash_enemy_flag = False
        self.player_alive = True
        self.battle_ongoing_flag = True
        self.hp_roulette = NumberRoulette('assets/sprites/battle_numbers.png', self.player.stats["hp"])
        self.pp_roulette = NumberRoulette('assets/sprites/battle_numbers.png', self.player.stats["psi"])

        #  this should be per NPC, not per battle
        self.last_update_time = time.time()
        self.attack_interval = 2 #time in seconds?

    def start_battle(self):
        self.battle_active = True
        self.bg.prepare()
        if (self.bg_tfx):
            self.bg_tfx.prepare()

    def draw_enemy(self, enemy):
        if self.battle_ongoing_flag:
            self.screen.blit(pygame.transform.scale(enemy.battle_sprite, (enemy.battle_sprite.get_width() * 3, enemy.battle_sprite.get_height() * 3)), (self.screen_width // 2 - enemy.battle_sprite.get_width() // 2, (self.screen_height // 2 - enemy.battle_sprite.get_height() // 2) - enemy.battle_sprite.get_height() // 2))
   
    def draw(self):
        self.bg.draw(self.screen)
        self.bg.update()
        if (self.bg_tfx):
            self.bg_tfx.draw(self.screen, True)
            self.bg_tfx.update()
        self.battle_log.draw(self.screen)
        self.draw_hud()

    def draw_hud(self):
        self.screen.blit(pygame.transform.scale(battle_hud_box, (battle_hud_box.get_width() * 2, battle_hud_box.get_height() * 2)), (self.screen_width // 2 - battle_hud_box.get_width() // 2, (self.screen_height - battle_hud_box.get_height()) - battle_hud_box.get_height() - 40 ))

        # display player's name
        player_name_image = pygame.image.load('assets/sprites/battle_name_ness.png')
        player_name_image = pygame.transform.scale(player_name_image, (player_name_image.get_width() * 2, player_name_image.get_height() * 2))
        self.screen.blit(player_name_image, (self.screen_width // 2 - battle_hud_box.get_width() // 2 + 20, (self.screen_height - battle_hud_box.get_height()) - battle_hud_box.get_height() - 40 + 25))
        
        # display player HP
        player_hp_text = pygame.font.Font('assets/fonts/earthbound-menu-extended.ttf', 24).render(f"{self.player.stats['hp']}", True, (0, 0, 0))
        self.screen.blit(player_hp_text, (self.screen_width // 2 - battle_hud_box.get_width() // 2 + 170, (self.screen_height - battle_hud_box.get_height()) - battle_hud_box.get_height() - 40 + 45))
        # display player PSI
        player_psi_text = pygame.font.Font('assets/fonts/earthbound-menu-extended.ttf', 24).render(f"{self.player.stats['psi']}", True, (0, 0, 0))
        self.screen.blit(player_psi_text, (self.screen_width // 2 - battle_hud_box.get_width() // 2 + 170, (self.screen_height - battle_hud_box.get_height()) - battle_hud_box.get_height() - 40 + 75))

        # Draw the roulettes
        self.hp_roulette.draw(self.screen, (self.screen_width // 2) + 22, self.screen_height - 118)
        self.pp_roulette.draw(self.screen, (self.screen_width // 2) + 38, self.screen_height - 86)


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

        self.hp_roulette.set_target_value(defender.stats["hp"] - damage)
        # self.hp_roulette.update()

        return damage

    def player_command(self, action):
        if action == "Run": 
            if self.enemies[0].force_battle == True:
                self.battle_log.add_message("You can't run from this battle!")
                return
            elif random.randint(1, 10) > 5:
                self.battle_log.add_message("You ran away!")
                # wait for user input
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        self.battle_ongoing_flag = False
                        return
                return
            else:
                self.battle_log.add_message("You couldn't escape!")
                self.is_player_turn = False
                return
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
        self.battle_log.add_message(f"{self.enemies[0].name}'s turn.")
        pygame.time.set_timer(ENEMY_ATTACK_SOUND_EVENT, 600, True)
    
    def handle_enemy_turn(self):
        if self.is_player_turn:
            return
        current_time = time.time()
        # print(current_time, self.last_update_time, current_time - self.last_update_time, self.attack_interval)
        if current_time - self.last_update_time > random.uniform(self.attack_interval, self.attack_interval * 2):
            # attacks by default
            self.battle_log.add_message(f"{self.enemies[0].name} attacks!")
            damage = self.calculate_damage_enemy(self.enemies[0], self.player)
            self.player.stats["hp"] -= damage
            self.is_player_turn = True
            self.last_update_time = current_time
            return

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

    def handle_input(self, command):
        col = self.menu_selection % self.menu_columns
        row = self.menu_selection // self.menu_columns

        if command == "move_left":
            col = max(col - 1, 0)
            cursor_horizontal_sfx.play()
        elif command == "move_right":
            col = min(col + 1, self.menu_columns - 1)
            cursor_horizontal_sfx.play()
        elif command == "move_up":
            row = max(row - 1, 0)
            cursor_vertical_sfx.play()
        elif command == "move_down":
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
        self.log_height = 30  # Height of the log area
        self.message_limit = 6  # Max number of messages to display at once
        self.last_update_time = time.time()
        self.fade_interval = 2 #time in seconds?

    def add_message(self, message):
        """Add a message to the battle log queue."""
        print(message)
        self.messages.append(message)
        self.log_height += 33
        if len(self.messages) > self.message_limit:
            self.log_height -= 33
            self.messages.pop(0)  # Remove the oldest message

    def draw(self, screen):
        if len(self.messages) == 0:
            return
        """Draw the battle log messages to the screen."""
        y_offset_box = self.screen_height - self.log_height - 20
        y_offset = self.screen_height - 65
        # draw the log box
        pygame.draw.rect(screen, (16, 16, 16), (20, y_offset_box, 350, self.log_height))
        pygame.draw.rect(screen, (255,255,255), (20, y_offset_box, 350, self.log_height), 2)
        for message in reversed(self.messages):
            if message == "Smaaash!":
                smash_image = pygame.image.load('assets/sprites/smash.png')
                transparent_color = smash_image.get_at((0, 0))
                smash_image.set_colorkey(transparent_color)
                smash_image = pygame.transform.scale(smash_image, (smash_image.get_width() * 2, smash_image.get_height() * 2))
                screen.blit(smash_image, (36, y_offset))
                y_offset -= smash_image.get_height()
            elif message == "You won!":
                victory_image = pygame.image.load('assets/sprites/you_won.png')
                transparent_color = victory_image.get_at((0, 0))
                victory_image.set_colorkey(transparent_color)
                victory_image = pygame.transform.scale(victory_image, (victory_image.get_width() * 2, victory_image.get_height() * 2))
                screen.blit(victory_image, (36, y_offset))
                y_offset -= victory_image.get_height() + 4
            else:
                text_surface = self.font.render(message, True, (255, 255, 255))
                screen.blit(text_surface, (40, y_offset))
                y_offset -= text_surface.get_height()  # Move up for the next message

            now = time.time()
            if now - self.last_update_time > self.fade_interval:
                self.log_height -= 33
                self.messages.pop(0)
                self.last_update_time = now

class NumberRoulette:
    def __init__(self, spritesheet_path, current_value):
        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        self.current_value = current_value
        self.target_value = current_value
        self.frame_width = 8
        self.frame_height = 12
        self.frames = self.load_frames()
        self.animation_state = []
        self.frame_duration = 50
        self.last_update_time = pygame.time.get_ticks()
        self.prepare_animation_state()

    def load_frames(self):
        frames = {str(n): [] for n in range(10)}
        for n in range(10):
            for frame in range(4):  # Assuming 4 frames per digit for the animation
                x = frame * self.frame_width + n * (self.frame_width * 4)
                y = 0
                frames[str(n)].append(self.spritesheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height)))
        return frames

    def set_target_value(self, value):
        self.target_value = value
        self.prepare_animation_state()

    def prepare_animation_state(self):
        target_str = str(self.target_value).zfill(len(str(self.current_value)))
        self.current_value_str = str(self.current_value).zfill(len(target_str))
        self.animation_state = [{
            'digit': int(self.current_value_str[i]),
            'target': int(target_str[i]),
            'frame': 0,
            'animating': False
        } for i in range(len(target_str))]

    def animate_digits(self):
        self.current_value = self.target_value
        for i in range(len(self.animation_state) - 1, -1, -1):  # Start from the rightmost digit
            digit_info = self.animation_state[i]
            if digit_info['digit'] != digit_info['target']:
                if not any(d['animating'] for d in self.animation_state[i+1:]):  # No right-hand digit is animating
                    digit_info['animating'] = True
                    digit_info['frame'] = (digit_info['frame'] - 1) % 4
                    if digit_info['frame'] == 0:  # Full cycle completed
                        next_digit = (digit_info['digit'] - 1) % 10
                        if next_digit > digit_info['digit']:  # Rolled over
                            if i > 0:  # Prevent index error
                                self.animation_state[i - 1]['animating'] = True  # Trigger left-hand digit animation
                        digit_info['digit'] = next_digit
                        if digit_info['digit'] == digit_info['target']:
                            digit_info['animating'] = False  # Stop animating when target reached
                    break  # Ensure only one digit updates per cycle

    # def check_completion(self):
    #     if all(digit_info['digit'] == digit_info['target'] for digit_info in self.animation_state):
    #         self.current_value = self.target_value
    #         for digit_info in self.animation_state:  # Stop all animations
    #             digit_info['animating'] = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.frame_duration:
            self.last_update_time = now
            self.animate_digits()
            # self.check_completion()

    def draw(self, screen, x, y):
        self.update()
        for i, anim in enumerate(self.animation_state):
            digit_frame = self.frames[str(anim['digit'])][anim['frame']]
            scaled_digit_frame = pygame.transform.scale(digit_frame, (self.frame_width * 2, self.frame_height * 2))
            screen.blit(scaled_digit_frame, (x + i * self.frame_width * 2, y))


class BattleBackground:
    def __init__(self, filename, effect_types, screen_width, screen_height, scroll_x=0, scroll_y=0, scroll_speed_x=2, scroll_speed_y=0):
        self.original_image = pygame.image.load(filename)

        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # background_scrolling will be fullscreen
        # self.image = pygame.transform.scale(self.original_image.copy(), (screen_width, screen_height))
        # background_scrolling with be HD
        # self.image = self.original_image.copy()

        self.image = pygame.transform.scale(self.original_image.copy(), (self.screen_width//1.6, self.screen_height//.9))
        self.effect_types = effect_types

        # For palette cycling effect
        self.palette = None
        self.palette_index = 0
        self.last_palette_update_time = time.time()
        self.palette_update_interval = 0.05

        # For scrolling effect
        self.scroll_x = scroll_x
        self.scroll_y = scroll_y
        self.scroll_speed_x = scroll_speed_x
        self.scroll_speed_y = scroll_speed_y

        # For oscillation effect
        self.oscillation_vertical_phase = 0
        self.oscillation_horizontal_phase = 0
        self.oscillation_phase = 0

    def prepare(self):
        arr = pygame.surfarray.array3d(self.original_image)
        self.palette = np.unique(arr.reshape(-1, arr.shape[2]), axis=0)
        self.prepare_palette(self.original_image)
    
    def update(self):

        current_time = time.time()
        if current_time - self.last_palette_update_time > self.palette_update_interval:
            self.shift_palette()
            self.last_palette_update_time = current_time
        self.oscillation_vertical_phase += 0.1
        self.oscillation_horizontal_phase += 0.2
        self.oscillation_phase += 0.1

    def draw(self, screen, transparent=False):
        # Start with the original image for each frame to ensure effects don't permanently alter it
        image_for_frame = self.original_image.copy()

        # Apply effects in sequence. Instead of transforming image_for_frame directly,
        # consider applying effects that produce a new surface each time.
        if "palette_cycling" in self.effect_types:
            image_for_frame = self.apply_shifted_palette(image_for_frame)
        if "background_scrolling" in self.effect_types:
            image_for_frame = self.apply_background_scrolling(image_for_frame)
        if "horizontal_oscillation" in self.effect_types:
            image_for_frame = self.apply_horizontal_oscillation(image_for_frame)
        if "vertical_oscillation" in self.effect_types:
            image_for_frame = self.apply_vertical_oscillation(image_for_frame)
        if "interleaved_oscillation" in self.effect_types:
            image_for_frame = self.apply_interleaved_oscillation(image_for_frame)

        # Scale and blit the final image to the screen
        if (transparent):
            image_for_frame.set_colorkey((0, 0, 0))
            image_for_frame.set_alpha(128)
        screen.blit(pygame.transform.scale(image_for_frame, (self.screen_width, self.screen_height)), (0, 0))
        

    def prepare_palette(self, image):
        # Convert image to an array and flatten the array
        arr = pygame.surfarray.array3d(image).reshape((-1, 3))
        # Find unique colors and their indices in the original image
        palette, inverse = np.unique(arr, axis=0, return_inverse=True)
        self.palette = palette
        self.inverse_palette_indices = inverse.reshape(image.get_size()[1], image.get_size()[0])
        self.palette_size = len(palette)

    def shift_palette(self):
        # Shift the palette indices to cycle colors
        self.palette = np.roll(self.palette, shift=-1, axis=0)

    def apply_shifted_palette(self, image):
        # only apply shift it palette has more than 4 colors
        if self.palette_size < 4:
            self.palette_update_interval = 0.2
        # Ensure the operation is compatible with the image size
        original_size = image.get_size()
        # Assuming the inverse palette indices map directly corresponds to the image pixels
        # Make sure the array operations are consistent with image dimensions
        reshaped_arr = np.take(self.palette, self.inverse_palette_indices, axis=0)
        # Reshape to match the original image dimensions, with 3 color channels
        reshaped_arr_correct = reshaped_arr.reshape(original_size[1], original_size[0], 3)

        # Now, use pygame.surfarray.blit_array to update the image with the reshaped array
        pygame.surfarray.blit_array(image, reshaped_arr_correct)
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
        # Create a new surface to hold the tiled background
        tiled_surface = pygame.Surface((self.screen_width, self.screen_height))

        # Calculate the number of times the image needs to be drawn to cover the screen
        num_tiles_x = int(np.ceil(self.screen_width / image.get_width())) + 1
        num_tiles_y = int(np.ceil(self.screen_height / image.get_height())) + 1

        # Update the scroll position
        self.scroll_x += self.scroll_speed_x
        self.scroll_y += self.scroll_speed_y

        # Ensure scroll wraps correctly
        self.scroll_x %= image.get_width()
        self.scroll_y %= image.get_height()

        # Draw the image at each tile position to cover the screen
        for x_tile in range(num_tiles_x):
            for y_tile in range(num_tiles_y):
                draw_x = x_tile * image.get_width() - self.scroll_x
                draw_y = y_tile * image.get_height() - self.scroll_y
                tiled_surface.blit(image, (draw_x, draw_y))

        # Instead of converting to an array and back, simply return the tiled surface
        return tiled_surface

    def apply_interleaved_oscillation(self, image, amplitude=10, frequency=0.1):
        # Convert the image into a pixel array for manipulation
        arr = pygame.surfarray.array3d(image)
        oscillated_arr = np.zeros_like(arr)

        height = arr.shape[1]

        for y in range(height):
            # Calculate the oscillation offset for this row
            # Alternate the direction of the oscillation based on the row number
            direction = 1 if y % 2 == 0 else -1
            shift = int(amplitude * math.sin(frequency * y + self.oscillation_phase) * direction)
            
            # Apply the shift to this row
            oscillated_arr[:, y, :] = np.roll(arr[:, y, :], shift, axis=0)

        # Convert the manipulated pixel array back into an image
        pygame.surfarray.blit_array(image, oscillated_arr)
        return image
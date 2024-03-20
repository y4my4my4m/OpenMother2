import pygame
import random

# fixme
screen_width = 1280
screen_height = 720
class BattleSystem:
    def __init__(self, screen, player, enemies):
        self.screen = screen
        self.player = player
        self.enemies = enemies
        # self.gui = BattleGUI(player, enemies)
        self.current_turn = 'player'
        self.battle_active = False

    def start_battle(self):
        self.battle_active = True
        # Main battle loop
        while self.battle_active:
            self.screen.fill((0, 0, 0))  # Clear screen
            self.draw(self.enemies[0]) 
            # self.gui.draw(self.screen)  # Draw the GUI
            pygame.display.flip()  # Update the display
            
            # Event handling simplified for demonstration
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # Example key bindings for demo purposes
                    if event.key == pygame.K_SPACE:
                        self.player_turn()
                        self.enemy_turn()
                    elif event.key == pygame.K_ESCAPE:
                        self.battle_active = False

            # Additional game loop logic here
            self.check_battle_end()
            pygame.time.wait(100)  # Short delay for demonstration

    def draw(self, enemy):
        # Draw the enemy
        # scale up the battle sprite to make it more visible
        # then center it in the screen
        self.screen.blit(pygame.transform.scale(enemy.battle_sprite, (enemy.battle_sprite.get_width() * 3, enemy.battle_sprite.get_height() * 3)), (screen_width // 2 - enemy.battle_sprite.get_width() // 2, (screen_height // 2 - enemy.battle_sprite.get_height() // 2) - 140))
        # self.screen.blit(self.enemies[0].battle_sprite, (400, 200))
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
        print("Battle ended.")


class BattleEnvironment:
    def __init__(self, background, player, enemies):
        self.background = background
        self.player = player
        self.enemies = enemies
        # self.background = pygame.image.load(background_image_path)

    def draw(self, screen):
        # screen.blit(self.background, (0, 0))
        # draw a black rectangle to represent the background
        # screen.fill((0, 0, 0))
        pass

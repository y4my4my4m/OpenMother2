class Enemy:
    def __init__(self, name, exploration_sprite_path, battle_sprite_path, hp, attack, defense):
        self.name = name
        self.exploration_sprite = pygame.image.load(exploration_sprite_path).convert_alpha()
        self.battle_sprite = pygame.image.load(battle_sprite_path).convert_alpha()
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.alive = True

    def draw_exploration(self, screen, position):
        if self.alive:
            screen.blit(self.exploration_sprite, position)

    def draw_battle(self, screen, position):
        if self.alive:
            screen.blit(self.battle_sprite, position)

import pygame

ENEMY_ATTACK_SOUND_EVENT = pygame.USEREVENT + 1

class SoundController:
    def __init__(self):
        pass

    def process_events(self, events):
        for event in events:
            if event.type == ENEMY_ATTACK_SOUND_EVENT:
                self.play_sfx(event.type)
                    
    def play_sfx(self, event):
        if event == ENEMY_ATTACK_SOUND_EVENT:
            enemy_attack_sfx = pygame.mixer.Sound('assets/sounds/enemyattack.wav')
            enemy_attack_sfx.set_volume(1.0)
            enemy_attack_sfx.play()

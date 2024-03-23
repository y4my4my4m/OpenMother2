import pygame
import sys

class InputController:
    def __init__(self):
        self.joystick_enabled = False
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_enabled = True

        self.action_states = {
            'move_left': False,
            'move_right': False,
            'move_up': False,
            'move_down': False,
            'action': False,
            'back': False,
            'shift': False,  # Assuming 'shift' is for running or similar continuous action
        }

        self.keys_pressed = set()
        self.joystick_buttons_pressed = set()

    def process_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            elif event.type == pygame.JOYBUTTONDOWN:
                self.joystick_buttons_pressed.add(event.button)
            elif event.type == pygame.JOYBUTTONUP:
                self.joystick_buttons_pressed.discard(event.button)

        self.update_action_states()

    def update_action_states(self):
        # Update action states based on keyboard
        self.action_states['move_left'] = pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed
        self.action_states['move_right'] = pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed
        self.action_states['move_up'] = pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed
        self.action_states['move_down'] = pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed
        self.action_states['action'] = pygame.K_SPACE in self.keys_pressed
        self.action_states['back'] = pygame.K_ESCAPE in self.keys_pressed
        self.action_states['shift'] = pygame.K_LSHIFT in self.keys_pressed or pygame.K_RSHIFT in self.keys_pressed

        # Update action states based on joystick axes
        if self.joystick_enabled:
            self.action_states['move_left'] = self.joystick.get_axis(0) < -0.5 or self.action_states['move_left']
            self.action_states['move_right'] = self.joystick.get_axis(0) > 0.5 or self.action_states['move_right']
            self.action_states['move_up'] = self.joystick.get_axis(1) < -0.5 or self.action_states['move_up']
            self.action_states['move_down'] = self.joystick.get_axis(1) > 0.5 or self.action_states['move_down']

        # Update action states based on joystick buttons
        if self.joystick_enabled:
            self.action_states['action'] = 0 in self.joystick_buttons_pressed or self.action_states['action']
            self.action_states['back'] = 1 in self.joystick_buttons_pressed or self.action_states['back']
            # Assuming button 3 (Y on Xbox controller) is used for 'shift' action
            self.action_states['shift'] = 3 in self.joystick_buttons_pressed or self.action_states['shift']

    def is_action_pressed(self, action_name):
        return self.action_states.get(action_name, False)
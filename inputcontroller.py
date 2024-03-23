import pygame
import sys

class InputController:
    def __init__(self):
        self.joystick_enabled = False
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_enabled = True

        # Action states for continuous actions
        self.action_states = {
            'move_left': False, 'move_right': False, 'move_up': False, 'move_down': False,
            'action': False, 'back': False, 'shift': False, 'special': False,
            'select': False, 'start': False, 'bump_l': False, 'bump_r': False,
            'debug_1': False, 'debug_2': False, 'debug_3': False, 'debug_4': False,
        }

        # Tracks buttons/keys pressed to handle single-press actions
        self.pressed_states = {key: False for key in self.action_states.keys()}
        self.previous_states = self.action_states.copy()

        self.keys_mapping = {
            pygame.K_LEFT: 'move_left', pygame.K_a: 'move_left',
            pygame.K_RIGHT: 'move_right', pygame.K_d: 'move_right',
            pygame.K_UP: 'move_up', pygame.K_w: 'move_up',
            pygame.K_DOWN: 'move_down', pygame.K_s: 'move_down',
            pygame.K_SPACE: 'action', pygame.K_ESCAPE: 'back',
            pygame.K_LSHIFT: 'shift', pygame.K_RSHIFT: 'shift',
            pygame.K_BACKSPACE: 'select', pygame.K_RETURN: 'start',
            pygame.K_1: 'debug_1', pygame.K_2: 'debug_2',
            pygame.K_3: 'debug_3', pygame.K_4: 'debug_4',
        }

        self.joystick_buttons_mapping = {
            0: 'special', 1: 'back', 2: 'action', 3: 'shift',
            4: 'bump_l', 5: 'bump_r', 8: 'select', 9: 'start',
        }

    def process_events(self, events):
        # Reset states for single-press actions
        for action in self.pressed_states.keys():
            self.pressed_states[action] = False

        # Process each event
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                pressed = event.type == pygame.KEYDOWN
                action = self.keys_mapping.get(event.key)
                if action:
                    self.action_states[action] = pressed
                    if pressed:
                        self.pressed_states[action] = not self.previous_states[action]
            elif event.type == pygame.JOYAXISMOTION:
                self.handle_joy_axis_motion()
            elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                pressed = event.type == pygame.JOYBUTTONDOWN
                action = self.joystick_buttons_mapping.get(event.button)
                if action:
                    self.action_states[action] = pressed
                    if pressed:
                        self.pressed_states[action] = not self.previous_states[action]

        # Update previous states for next frame comparison
        self.previous_states = self.action_states.copy()

    def handle_joy_axis_motion(self):
        if self.joystick_enabled:
            self.action_states['move_left'] = self.joystick.get_axis(0) < -0.5
            self.action_states['move_right'] = self.joystick.get_axis(0) > 0.5
            self.action_states['move_up'] = self.joystick.get_axis(1) < -0.5
            self.action_states['move_down'] = self.joystick.get_axis(1) > 0.5

    def is_action_pressed(self, action_name):
        return self.action_states.get(action_name, False)

    def is_action_pressed_once(self, action_name):
        return self.pressed_states.get(action_name, False)

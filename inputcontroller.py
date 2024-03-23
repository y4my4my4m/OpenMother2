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
            'back': False
        }

        # Tracks if a key/joystick input has explicitly set an action state
        self.explicit_states = {
            'move_left': False,
            'move_right': False,
            'move_up': False,
            'move_down': False,
            'action': False,
            'back': False
        }

        self.keys_pressed = set()

    def process_events(self, events):
        # Reset explicit states to track which actions have been explicitly set this frame
        self.explicit_states = {action: False for action in self.action_states}

        if self.joystick_enabled:
            self.update_joystick_axis_actions()

        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            elif self.joystick_enabled and event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
                pressed = event.type == pygame.JOYBUTTONDOWN
                self.handle_joy_button_event(event.button, pressed)

        # Update action states based on the keys that are currently pressed
        self.update_key_action_states()

        # Finalize action states, considering both keyboard and joystick inputs
        self.finalize_action_states()

    def handle_joy_button_event(self, button, pressed):
        if button == 1:  # JOY_A
            self.action_states['action'] = self.explicit_states['action'] = pressed
        elif button == 2:  # JOY_B
            self.action_states['back'] = self.explicit_states['back'] = pressed

    def update_joystick_axis_actions(self):
        # Directly update action states from joystick input
        self.set_action_state('move_left', self.joystick.get_axis(0) < -0.5)
        self.set_action_state('move_right', self.joystick.get_axis(0) > 0.5)
        self.set_action_state('move_up', self.joystick.get_axis(1) < -0.5)
        self.set_action_state('move_down', self.joystick.get_axis(1) > 0.5)

    def update_key_action_states(self):
        # Use keys_pressed to set action states, similar to joystick handling
        self.set_action_state('move_left', pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed)
        self.set_action_state('move_right', pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed)
        self.set_action_state('move_up', pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed)
        self.set_action_state('move_down', pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed)
        self.set_action_state('action', pygame.K_SPACE in self.keys_pressed)
        self.set_action_state('back', pygame.K_ESCAPE in self.keys_pressed)

    def set_action_state(self, action, state):
        if not self.explicit_states[action]:
            self.action_states[action] = state
            if state:  # Only mark as explicitly set if state is True
                self.explicit_states[action] = True

    def finalize_action_states(self):
        # Any additional logic to combine or finalize action states can go here
        pass

    def is_action_pressed(self, action_name):
        return self.action_states.get(action_name, False)

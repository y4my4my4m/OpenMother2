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

        # Continuous action states and single press detections
        self.action_states = {
            'move_left': False, 'move_right': False, 'move_up': False, 'move_down': False,
            'action': False, 'back': False, 'shift': False, 'special': False,
            'select': False, 'start': False, 'bump_l': False, 'bump_r': False,
            'zoom_out': False, 'zoom_in': False,
            'debug_1': False, 'debug_2': False, 'debug_3': False, 'debug_4': False,
            'debug_5': False,
        }

        # Resettable states for detecting single press or release events
        self.pressed_states = {key: False for key in self.action_states.keys()}
        self.previous_states = self.action_states.copy()

        # Previous values for joystick axes to detect changes
        self.previous_axis_values = {'x': 0, 'y': 0}

        # Mapping of keyboard keys to actions
        self.keys_mapping = {
            pygame.K_LEFT: 'move_left', pygame.K_a: 'move_left',
            pygame.K_RIGHT: 'move_right', pygame.K_d: 'move_right',
            pygame.K_UP: 'move_up', pygame.K_w: 'move_up',
            pygame.K_DOWN: 'move_down', pygame.K_s: 'move_down',
            pygame.K_SPACE: 'action', pygame.K_ESCAPE: 'back',
            pygame.K_LSHIFT: 'shift', pygame.K_RSHIFT: 'shift',
            pygame.K_BACKSPACE: 'select', pygame.K_RETURN: 'start',
            pygame.K_MINUS: 'zoom_out', pygame.K_EQUALS: 'zoom_in',
            pygame.K_1: 'debug_1', pygame.K_2: 'debug_2',
            pygame.K_3: 'debug_3', pygame.K_4: 'debug_4',
            pygame.K_5: 'debug_5'
        }

        # Mapping of joystick button IDs to actions
        self.joystick_buttons_mapping = {
            0: 'special', 1: 'back', 2: 'action', 3: 'shift',
            4: 'bump_l', 5: 'bump_r', 8: 'select', 9: 'start',
        }

    def process_events(self, events):
        # Reset pressed_states for new event processing cycle
        self.pressed_states = {key: False for key in self.pressed_states.keys()}

        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.process_keyboard_event(event)
            elif event.type == pygame.JOYAXISMOTION:
                self.process_joy_axis_motion(event)
            elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                self.process_joy_button_event(event)

        # Update previous states for next frame's comparison
        self.previous_states = self.action_states.copy()

    def process_keyboard_event(self, event):
        action = self.keys_mapping.get(event.key)
        if action:
            pressed = event.type == pygame.KEYDOWN
            self.action_states[action] = pressed
            if pressed:
                self.pressed_states[action] = not self.previous_states[action]

    def process_joy_axis_motion(self, event):
        if self.joystick_enabled:
            x_axis = self.joystick.get_axis(0)
            y_axis = self.joystick.get_axis(1)
            axis_threshold = 0.5

            # Determine if there's a change in the axis beyond the threshold, indicating a new press
            new_press_x = (abs(x_axis) > axis_threshold and abs(self.previous_axis_values['x']) <= axis_threshold)
            new_press_y = (abs(y_axis) > axis_threshold and abs(self.previous_axis_values['y']) <= axis_threshold)

            # Update the "pressed once" state for axis directions based on new press detection
            if new_press_x:
                if x_axis < -axis_threshold:
                    self.pressed_states['move_left'] = True
                elif x_axis > axis_threshold:
                    self.pressed_states['move_right'] = True
            if new_press_y:
                if y_axis < -axis_threshold:
                    self.pressed_states['move_up'] = True
                elif y_axis > axis_threshold:
                    self.pressed_states['move_down'] = True

            # Reset "pressed once" state when the axis returns to neutral
            if abs(x_axis) <= axis_threshold:
                self.pressed_states['move_left'] = False
                self.pressed_states['move_right'] = False
            if abs(y_axis) <= axis_threshold:
                self.pressed_states['move_up'] = False
                self.pressed_states['move_down'] = False

            # Update continuous action states
            self.action_states['move_left'] = x_axis < -axis_threshold
            self.action_states['move_right'] = x_axis > axis_threshold
            self.action_states['move_up'] = y_axis < -axis_threshold
            self.action_states['move_down'] = y_axis > axis_threshold

            # Save the current axis values for comparison in the next frame
            self.previous_axis_values['x'] = x_axis
            self.previous_axis_values['y'] = y_axis

    def process_joy_button_event(self, event):
        action = self.joystick_buttons_mapping.get(event.button)
        if action:
            pressed = event.type == pygame.JOYBUTTONDOWN
            self.action_states[action] = pressed
            if pressed:
                self.pressed_states[action] = not self.previous_states[action]

    def is_action_pressed(self, action_name):
        # Returns True if the action is currently active
        return self.action_states.get(action_name, False)

    def is_action_pressed_once(self, action_name):
        # Returns True only if the action was explicitly set in this frame
        return self.pressed_states.get(action_name, False)

    def is_any_pressed_once(self):
        return any(self.pressed_states.values())

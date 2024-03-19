import pygame

class DialogueBox:
    def __init__(self, font_path, font_size, screen_width, screen_height):
        self.font = pygame.font.Font(font_path, font_size)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.text = ""
        self.is_visible = False

    def show_text(self, text):
        self.text = text
        self.is_visible = True

    def hide(self):
        self.is_visible = False

    def draw(self, screen):
        if self.is_visible:
            # Calculate box size and position
            box_width = self.screen_width * 0.8
            box_height = 100  # Adjust as needed
            box_x = (self.screen_width - box_width) / 2
            box_y = self.screen_height - box_height - 20  # Padding from the bottom

            # Background box
            pygame.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)

            # Rendered text
            wrapped_text = self.wrap_text(self.text, box_width - 20)
            for i, line in enumerate(wrapped_text):
                text_surface = self.font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (box_x + 10, box_y + 10 + i * 22))

    def wrap_text(self, text, max_width):
        """Wrap text based on the font size and box width."""
        words = text.split(' ')
        wrapped_lines = []
        line = ""
        for word in words:
            test_line = line + word + ' '
            # Check the width of the line with the new word added
            if self.font.size(test_line)[0] <= max_width:
                line = test_line
            else:
                wrapped_lines.append(line)
                line = word + ' '
        wrapped_lines.append(line)
        return wrapped_lines

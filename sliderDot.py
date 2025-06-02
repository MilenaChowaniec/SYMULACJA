import pygame as p
import math as m

class SliderDot:
    def __init__(self, text, screen, y, min, max):
        """
        Initialize the slider dot control.

        :param text: Label text displayed above the slider.
        :param screen: Pygame screen surface to draw on.
        :param y: Y-coordinate for the slider line and dot.
        :param min: Minimum value (string) shown at the slider start.
        :param max: Maximum value (string) shown at the slider end.
        """
        self.LINE_LENGTH = 400 # Total length of the slider line
        self.CIRCLE_RADIUS = 15 # Radius of the draggable dot
        self.dragging = False # Indicates if the dot is currently being dragged
        self.screen = screen
        self.line_y = y # Y-coordinate for the line and dot
        self.dot_y = y
        self.text_y = y - 60 # Position of the text label above the slider

        self.range_limits_text(min, max)

        self.offset = int(min)
        self.range = int(max) - int(min) # Range of values
        self.pixels = self.LINE_LENGTH / self.range # Pixels per unit value
        self.number = 0

        self._init_shapes(text)
        self.calculate_number()

    def _init_shapes(self, text):
        """
        Initialize the text and shapes used for the slider.

        :param text: Label text to display above the slider.
        """
        self.text = p.font.SysFont('Tahoma', 20).render(text, True, (0, 0, 0))
        self.line = p.Rect(self.screen.get_width() / 2 - self.LINE_LENGTH / 2, self.line_y, self.LINE_LENGTH, 3)
        self.dot = p.Rect(self.screen.get_width() / 2, self.dot_y - self.CIRCLE_RADIUS / 2, self.CIRCLE_RADIUS, self.CIRCLE_RADIUS)

    def range_limits_text(self, min, max):
        """
        Render the min and max value labels for the slider.

        :param min: Minimum value label (string).
        :param max: Maximum value label (string).
        """
        self.min = p.font.SysFont('Tahoma', 20).render(min, True, (0, 0, 0))
        self.max = p.font.SysFont('Tahoma', 20).render(max, True, (0, 0, 0))

    def draw(self):
        """
        Draw the slider components: label, min/max labels, slider line, and draggable dot.
        """
        # Draw label text
        self.screen.blit(self.text, (self.screen.get_width() / 2 - self.text.get_width() / 2, self.text_y))

        # Draw min/max labels
        self.screen.blit(self.min, (self.screen.get_width() / 2 - self.LINE_LENGTH / 2 - 35, self.line_y - self.min.get_height() / 2))
        self.screen.blit(self.max, (self.screen.get_width() / 2 + self.LINE_LENGTH / 2 + 10, self.line_y - self.max.get_height() / 2))

        # Draw current number label above the dot
        self.num_text = p.font.SysFont('Tahoma', 15).render(str(self.number), True, (0, 0, 0))
        self.screen.blit(self.num_text, (self.dot.x + 1, self.dot.y - 18))

        # Draw text bounding box
        p.draw.rect(self.screen, (0,0,0), (self.screen.get_width() / 2 - self.text.get_width() / 2 - 10, self.text_y - 3, self.text.get_width() + 20, self.text.get_height() + 6), 1)

        # Draw slider line and dot
        p.draw.rect(self.screen, (0,0,0), self.line)
        p.draw.rect(self.screen, (0,0,0), self.dot, border_radius=self.CIRCLE_RADIUS)
    
    def drag(self, mouse_x):
        """
        Toggle dragging state and record drag offset.

        :param mouse_x: Current X-coordinate of the mouse.
        """
        self.dragging = not self.dragging
        self.drag_offset = mouse_x - self.dot.x
    
    def calculate_number(self):
        """
        Calculate the current slider value based on dot position relative to line start.
        """
        self.dot_center = self.dot.x + self.dot.width / 2
        dist = self.dot_center - self.line.x
        self.number = m.floor(dist / self.pixels) + self.offset
    
    def move(self, x):
        """
        Move the dot horizontally while respecting slider boundaries.

        :param x: New X-coordinate to move the dot (mouse position).
        """
        new_x = x - self.drag_offset
        # Clamp position within slider bounds
        new_x = max(self.line.left - self.dot.width / 2, min(self.line.right - self.dot.width / 2, new_x))
        self.dot.x = new_x
        self.calculate_number()
    
    def get_dot_rect(self):
        """
        Get the rectangle representing the draggable dot.

        :return: pygame.Rect of the dot.
        """
        return self.dot

    def get_if_drag(self):
        """
        Check if the dot is currently being dragged.

        :return: True if dragging, False otherwise.
        """
        return self.dragging
    
    def get_settings(self):
        """
        Get the current integer value of the slider.

        :return: Current slider value (int).
        """
        return m.floor(self.number)
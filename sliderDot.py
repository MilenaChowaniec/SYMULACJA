import pygame as p
import math as m

class SliderDot:
    """
    A class representing a draggable slider dot used for selecting numeric values 
    within a specified range.
    """
    def __init__(self, text, screen, y, min, max):
        """
        Initializes the slider with the provided parameters.

        Parameters:
        - text (str): The label displayed above the slider.
        - screen (pygame.Surface): The surface to draw the slider on.
        - y (int): The vertical position of the slider.
        - min (int/str): The minimum value of the slider.
        - max (int/str): The maximum value of the slider.
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
        Initializes the visual components of the slider:
        - Text label
        - Slider line
        - Draggable dot
        """
        self.text = p.font.SysFont('Tahoma', 20).render(text, True, (0, 0, 0))
        self.line = p.Rect(self.screen.get_width() / 2 - self.LINE_LENGTH / 2, self.line_y, self.LINE_LENGTH, 3)
        self.dot = p.Rect(self.screen.get_width() / 2, self.dot_y - self.CIRCLE_RADIUS / 2, self.CIRCLE_RADIUS, self.CIRCLE_RADIUS)

    def range_limits_text(self, min, max):
        """
        Renders the minimum and maximum value labels.
        """
        self.min = p.font.SysFont('Tahoma', 20).render(min, True, (0, 0, 0))
        self.max = p.font.SysFont('Tahoma', 20).render(max, True, (0, 0, 0))

    def draw(self):
        """
        Draws all components of the slider on the screen.
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
        Enables dragging mode and stores offset between mouse and dot position.
        """
        self.dragging = not self.dragging
        self.drag_offset = mouse_x - self.dot.x
    
    def calculate_number(self):
        """
        Calculates the slider value based on the current position of the dot.
        """
        self.dot_center = self.dot.x + self.dot.width / 2
        dist = self.dot_center - self.line.x
        self.number = m.floor(dist / self.pixels) + self.offset
    
    def move(self, x):
        """
        Moves the dot to a new position, constrained within the line limits.
        """
        new_x = x - self.drag_offset
        # Clamp position within slider bounds
        new_x = max(self.line.left - self.dot.width / 2, min(self.line.right - self.dot.width / 2, new_x))
        self.dot.x = new_x
        self.calculate_number()
    
    def get_dot_rect(self):
        """
        Returns the current rectangle of the dot (useful for collision checks).
        """
        return self.dot

    def get_if_drag(self):
        """
        Returns whether the slider is currently being dragged.
        """
        return self.dragging
    
    def get_settings(self):
        """
        Returns the current value selected by the slider.
        """
        return m.floor(self.number)
import pygame as p

class LivePlot:
    """
    Class responsible for drawing a live-updating line plot in Pygame.
    The plot visualizes changing values over time.
    """
    def __init__(self, screen, rect, text, max_points=100, update_interval=500, color=(0, 0, 255)):
        """
        Initializes the LivePlot instance.

        :param screen: Pygame surface to draw on
        :param rect: pygame.Rect defining the plot area (x, y, width, height)
        :param text: label text displayed above the plot
        :param max_points: maximum number of points shown on the X-axis (buffer size)
        :param update_interval: time interval (in milliseconds) between data updates
        :param color: line color of the plot
        """
        self.screen = screen
        self.rect = rect
        self.max_points = max_points
        self.update_interval = update_interval
        self.color = color     
        self.step_x = self.rect.width / self.max_points  # X step between data points
        self._init_var()
        self._init_colors()
        self._init_text(text)

    def _init_var(self):
        """Initializes internal variables and the data buffer."""
        self.points = []  
        self.last_update = p.time.get_ticks()
        self.min_val = 0
        self.max_val = 100
        self.paused = False # pause flag; when True, the plot does not update
    
    def _init_colors(self):
        """Initializes additional colors."""
        self.GREY = (80,80,80)

    def _init_text(self, text):
        self.graph_text = p.font.SysFont('Tahoma', 15).render(text, True, self.GREY)

    def add_value(self, val):
        """
        Adds a new value to the plot, scaling it to fit the plot area.

        :param val: new value to add (e.g., battery level, sensor reading)
        """
         # Clamp and normalize value to plot height (Y axis is inverted in screen coordinates)
        val_clamped = max(self.min_val, min(val, self.max_val))
        norm_y = self.rect.bottom - ((val_clamped - self.min_val) / (self.max_val - self.min_val)) * self.rect.height

        self.points.append(norm_y)
        if len(self.points) > self.max_points:
            self.points.pop(0)

    def update(self, new_val=None):
        """
        Updates the plot by adding a new value at regular time intervals.

        :param new_val: new value to add, if available
        """
        if self.paused:
            return  # Do not update if paused
        
        now = p.time.get_ticks()
        if now - self.last_update >= self.update_interval:
            if new_val is not None:
                self.add_value(new_val)
            self.last_update = now # Update timestamp

    def draw(self):
        """
        Draws the entire plot including background, grid, labels, and the data line.
        """
        # Draw background
        p.draw.rect(self.screen, (230, 230, 230), self.rect)
        self.screen.blit(self.graph_text, (self.rect.x, self.rect.y - 17, self.rect.width, self.rect.height))

        # Draw Y-axis labels and horizontal grid lines
        font = p.font.SysFont("Tahoma", 11)
        steps = 5
        label_margin = 5  # margin from the left side
        for i in range(steps + 1):
            percent = 100 - (i * 100 // steps)
            y = self.rect.top + i * (self.rect.height // steps)
            label = font.render(f"{percent}%", True, self.GREY)
            
            label_width = label.get_width()
            label_x = self.rect.left - label_margin - label_width

            self.screen.blit(label, (label_x, y - label.get_height() // 2))

            # Draw horizontal grid lines
            p.draw.line(self.screen, (200, 200, 200), (self.rect.left, y), (self.rect.right, y), 1)


        if len(self.points) < 2:
            return

        # Draw line plot by connecting points
        points_to_draw = []
        for i, y in enumerate(self.points):
            x = self.rect.left + i * self.step_x
            points_to_draw.append((x, y))

        p.draw.lines(self.screen, self.color, False, points_to_draw, 2)
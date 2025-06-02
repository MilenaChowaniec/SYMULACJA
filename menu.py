import pygame as p
import game
import simulationSettings as settings
import sliderDot as slider
import tkinter
import tkinter.filedialog

class Menu:
    """
    The Menu class handles the initial user interface for the simulation application.
    It provides buttons to generate a new simulation or load settings from a file,
    as well as sliders to configure simulation parameters.
    """
    def __init__(self, screen, game):
        """
        Initializes the Menu with references to the screen and game instance,
        and sets up all necessary UI components.
        """
        self.screen = screen
        self.game = game
        self._init_text()
        self._init_buttons()
        self._init_colors()
        self._init_var()
        self._init_sliders()

    def _init_var(self):
        """
        Initializes state variables and default simulation settings.
        """
        self.GEN_HOVERED = False
        self.FILE_HOVERED = False
        self.curr_slider = None    
        self.LINE_LENGTH = 400
        self.CIRCLE_RADIUS = 15
        self.settings = settings.SimulationSettings()

    def _init_text(self):
        """
        Initializes the rendered text surfaces for buttons.
        """
        self.generate = p.font.SysFont('Tahoma', 30).render('GENERATE', True, (0, 0, 0))
        self.load_file = p.font.SysFont('Tahoma', 30).render('LOAD FROM FILE', True, (0, 0, 0))

    def _init_colors(self):
        """
        Defines color constants used in the menu UI.
        """
        self.BLACK = (0,0,0)
        self.GREY = (170,170,170)
        self.WHITE = (255, 255, 255)

    def _init_buttons(self):
        """
        Sets up rectangles for the "Generate" and "Load from File" buttons.
        """
        self.generate_button = p.Rect(self.screen.get_width() / 2 - self.generate.get_width() / 2 - 10, 500 - 3, self.generate.get_width() + 20, self.generate.get_height() + 6)
        self.load_file_button = p.Rect(self.screen.get_width() / 2 - self.load_file.get_width() / 2 - 10, 450 - 3, self.load_file.get_width() + 20, self.load_file.get_height() + 6)
    
    def _init_sliders(self):
        """
        Initializes the sliders for adjusting simulation parameters.
        """
        self.sliders = {
            "snum": slider.SliderDot('number of sensors', self.screen, 70, '60', '120'),
            "pnum": slider.SliderDot('number of POIs', self.screen, 170, '10', '20'),
            "srange": slider.SliderDot('sensors range', self.screen, 270, '200', '300'),
        }

    def prompt_file(self):
        """
        Opens a file dialog to select a file using tkinter.
        Returns the selected file path.
        """
        top = tkinter.Tk()
        top.withdraw() # Hide root window
        file_name = tkinter.filedialog.askopenfilename(parent=top)
        top.destroy()
        return file_name

    def read_from_file(self):
        """
        Reads simulation settings from a selected text file and updates settings.
        Returns True if successful, False otherwise.
        """
        file_name = self.prompt_file()
        if not file_name or not file_name.endswith('.txt'):
            return False
        
        try:
            with open(file_name, "r") as file:
                lines = file.readlines()
            
            # The file must contain exactly one line
            if len(lines) != 1:
                print("Invalid file format.")
                return False
            
            parts = lines[0].strip().split()
            if len(parts) != 3:
                print("Invalid file format.")
                return False     

            numbers = list(map(int, parts))
            self.settings.set_snum(numbers[0])
            self.settings.set_pnum(numbers[1])
            self.settings.set_srange(numbers[2])
            return True
        
        except (ValueError, OSError):
            return False

    def handle_mouse_hovered(self):
        """
        Updates button hover states and cursor appearance based on mouse position.
        """
        if self.generate_button.collidepoint(p.mouse.get_pos()): 
            self.GEN_HOVERED = True
            p.mouse.set_cursor(p.SYSTEM_CURSOR_HAND)       
        elif self.load_file_button.collidepoint(p.mouse.get_pos()):
            self.FILE_HOVERED = True
            p.mouse.set_cursor(p.SYSTEM_CURSOR_HAND)
        else:
            # Reset hover state if mouse is not over any button
            self.FILE_HOVERED = False
            self.GEN_HOVERED = False
            p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)

    
    def handle_mouse_pressed(self, event, x):
        """
        Handles mouse click events: triggers button actions or starts slider dragging.
        """
        if event.button == 1: # Left click
            if self.generate_button.collidepoint(event.pos):
                # Apply current slider values to settings
                self.settings.set_snum(self.sliders["snum"].get_settings())
                self.settings.set_pnum(self.sliders["pnum"].get_settings())
                self.settings.set_srange(self.sliders["srange"].get_settings())
                self.GEN_HOVERED = False
                p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)
                self.game.change_scene(game.Scene.SIMULATION, self.settings)
            
            elif self.load_file_button.collidepoint(event.pos):
                self.FILE_HOVERED = False
                if not self.read_from_file():
                    return
                p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)
                self.game.change_scene(game.Scene.SIMULATION, self.settings)
            
            # Check if any slider is being dragged
            for slider in self.sliders:
                if self.sliders[slider].get_dot_rect().collidepoint(event.pos):
                    self.sliders[slider].drag(x)
                    self.curr_slider = self.sliders[slider]
                    p.mouse.set_cursor(p.SYSTEM_CURSOR_HAND)
                    break

    def handle_mouse_motion(self, x):
        """
        Handles mouse movement to update slider position while dragging.
        """
        if self.curr_slider is not None and self.curr_slider.get_if_drag():
            self.curr_slider.move(x)
            p.mouse.set_cursor(p.SYSTEM_CURSOR_HAND)

    def handle_mouse_released(self, x):
        """
        Ends slider dragging when mouse is released.
        """
        if self.curr_slider is not None:
             self.curr_slider.drag(x)
             self.curr_slider = None
             p.mouse.set_cursor(p.SYSTEM_CURSOR_ARROW)

    def handle_event(self, event):
        """
        Centralized handler for all Pygame events (mouse motion, clicks, quit).
        """
        mouse_x, mouse_y = p.mouse.get_pos()
        if event.type == p.QUIT:
            p.quit()
            quit()
        if event.type == p.MOUSEMOTION:
            self.handle_mouse_hovered()
        if event.type == p.MOUSEBUTTONDOWN:
            self.handle_mouse_pressed(event, mouse_x)
        if event.type == p.MOUSEMOTION:
            self.handle_mouse_motion(mouse_x)
        if event.type == p.MOUSEBUTTONUP:
            self.handle_mouse_released(mouse_x)


    def draw(self):
        """
        Draws all UI elements: buttons and sliders.
        """
        # Draw "Generate" button with hover effect
        if self.GEN_HOVERED == True:    
            p.draw.rect(self.screen, self.GREY, self.generate_button)
        self.screen.blit(self.generate, (self.screen.get_width() / 2 - self.generate.get_width() / 2, 500))
        p.draw.rect(self.screen, self.BLACK, (self.screen.get_width() / 2 - self.generate.get_width() / 2 - 10, 500 - 3, self.generate.get_width() + 20, self.generate.get_height() + 6), 1)
        
        # Draw "Load from File" button with hover effect
        if self.FILE_HOVERED == True:
            p.draw.rect(self.screen, self.GREY, self.load_file_button)
        self.screen.blit(self.load_file, (self.screen.get_width() / 2 - self.load_file.get_width() / 2, 450))
        p.draw.rect(self.screen, self.BLACK, (self.screen.get_width() / 2 - self.load_file.get_width() / 2 - 10, 450 - 3, self.load_file.get_width() + 20, self.load_file.get_height() + 6), 1)
        
        # Draw sliders
        for slider in self.sliders:
            self.sliders[slider].draw()
        
    def render(self):
        """
        Clears the screen and renders the entire menu UI.
        """
        self.screen.fill(self.WHITE)
        self.draw()

    def update(self):
        """
        Updates the display with the current frame.
        """
        p.display.flip()
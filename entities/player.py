import pygame

# Mapping ship colors to RGB values for rendering/effects
SHIP_COLOR_MAP = {
    "cyan":   (0,   220, 255),
    "violet": (190, 0,   255),
    "red":    (255, 60,  60),
    "yellow": (255, 230, 0),
    "purple": (130, 0,   255),
}


class Player:
    def __init__(self, screen_width, screen_height, color="cyan"):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = 80
        self.height = 80
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 100
        self.speed = 8
        self.color_key = color

        self.is_blinking = False
        self.blink_timer = 0
        self.visible = True

        self.image = self._create_ship_surface(self.color_key)

    def set_color(self, color):
        """Updates the ship's color and recreates its surface sprite."""
        self.color_key = color
        self.image = self._create_ship_surface(self.color_key)

    def _create_ship_surface(self, color_key):
        """Generates a procedural ship sprite based on the selected color theme."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        primary_color = SHIP_COLOR_MAP.get(color_key, (0, 220, 255))
        highlight_color = (220, 245, 255)  # Ice/Frost Accent

        # Ship Body Points (Sleek Futuristic Spaceship)
        center_x = self.width // 2
        
        # Main Hull
        hull_points = [
            (center_x, 5),                   # Nose tip
            (center_x + 18, 45),             # Upper right wing tip
            (center_x + 35, 65),             # Outer right wing tip
            (center_x + 20, 70),             # Right engine side
            (center_x, 60),                  # Center rear notch
            (center_x - 20, 70),             # Left engine side
            (center_x - 35, 65),             # Outer left wing tip
            (center_x - 18, 45),             # Upper left wing tip
        ]
        
        pygame.draw.polygon(surf, primary_color, hull_points)
        pygame.draw.polygon(surf, highlight_color, hull_points, 2)  # Frost border Outline

        # Cockpit Canopy
        canopy_points = [
            (center_x, 22),
            (center_x + 8, 40),
            (center_x, 46),
            (center_x - 8, 40),
        ]
        pygame.draw.polygon(surf, highlight_color, canopy_points)

        # Thruster Glow
        pygame.draw.circle(surf, (0, 210, 255), (center_x - 12, 66), 4)
        pygame.draw.circle(surf, (0, 210, 255), (center_x + 12, 66), 4)

        return surf

    def move_left(self):
        self.x -= self.speed

    def move_right(self):
        self.x += self.speed

    def keep_inside_screen(self):
        if self.x < 0:
            self.x = 0
        elif self.x > self.screen_width - self.width:
            self.x = self.screen_width - self.width

    def update_blink(self):
        """Handles death/blinking animation logic."""
        if self.is_blinking:
            self.blink_timer += 1
            if self.blink_timer % 10 == 0:
                self.visible = not self.visible

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
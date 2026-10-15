import pygame

class ToggleSwitch:
    def __init__(self, x, y, width=60, height=30, initial_state=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.state = initial_state
        
        self.bg_off = (24, 36, 62)
        self.bg_on = (0, 140, 210)
        self.border_color = (0, 180, 240)
        self.knob_color = (255, 255, 255)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
                return True
        return False

    def draw(self, screen):
        bg_col = self.bg_on if self.state else self.bg_off
        pygame.draw.rect(screen, bg_col, self.rect, border_radius=self.rect.height // 2)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=self.rect.height // 2)

        knob_radius = (self.rect.height - 8) // 2
        if self.state:
            knob_x = self.rect.right - knob_radius - 6
        else:
            knob_x = self.rect.x + knob_radius + 6
        
        knob_y = self.rect.centery
        pygame.draw.circle(screen, self.knob_color, (knob_x, knob_y), knob_radius)
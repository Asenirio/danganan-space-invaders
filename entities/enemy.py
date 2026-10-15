import pygame

class Enemy:
    def __init__(self, index, total_enemies, screen_width, screen_height=600):
        self.width = 80
        self.height = 80
        self.screen_width = screen_width
        self.screen_height = screen_height

        try:
            raw = pygame.image.load("assets/enemy.png").convert_alpha()
            self.image = pygame.transform.scale(raw, (self.width, self.height))
        except Exception:
            self.image = self._create_rogue_ninja_surface()

        spacing = screen_width / (total_enemies + 1)
        self.target_mid_x = spacing * (index + 1) - (self.width // 2)

        # Alternate rows for staggered ninja formation
        self.target_mid_y = 100 + (60 if index % 2 == 0 else 0)

        self.x = self.target_mid_x
        self.y = -self.height  # Start off-screen

        self.state = "entering"
        self.speed = 4
        self.dx = 0
        self.dy = 0

    def _create_rogue_ninja_surface(self):
        """Generates an Akatsuki Rogue Ninja sprite procedurally."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        cx, cy = self.width // 2, self.height // 2

        # Red Akatsuki Aura glow
        pygame.draw.circle(surf, (220, 20, 20, 40), (cx, cy), 36)

        # Rogue Cloak Body
        pygame.draw.polygon(surf, (20, 15, 25), [
            (cx - 24, cy + 30),
            (cx + 24, cy + 30),
            (cx + 16, cy - 8),
            (cx - 16, cy - 8)
        ])

        # Akatsuki Red Cloud accent on cloak
        pygame.draw.ellipse(surf, (210, 30, 40), (cx - 12, cy + 8, 24, 14))

        # Ninja Head
        pygame.draw.circle(surf, (230, 180, 140), (cx, cy - 18), 16)

        # Crossed Rogue Headband
        pygame.draw.rect(surf, (60, 65, 75), (cx - 16, cy - 26, 32, 9), border_radius=2)
        pygame.draw.rect(surf, (180, 190, 200), (cx - 8, cy - 25, 16, 7), border_radius=1)

        # Slash through headband symbol
        pygame.draw.line(surf, (200, 30, 30), (cx - 6, cy - 25), (cx + 6, cy - 19), 2)

        # Glowing Red Enemy Eyes
        pygame.draw.circle(surf, (255, 30, 30), (cx - 6, cy - 16), 3)
        pygame.draw.circle(surf, (255, 30, 30), (cx + 6, cy - 16), 3)

        return surf

    def start_drop(self, target_x, target_y):
        """Dive toward the player's current ninja position."""
        self.state = "dropping"

        distance_x = target_x - (self.x + self.width // 2)
        distance_y = target_y - self.y
        distance = (distance_x ** 2 + distance_y ** 2) ** 0.5

        if distance > 0:
            self.dx = (distance_x / distance) * self.speed
            self.dy = (distance_y / distance) * self.speed
        else:
            self.dx = 0
            self.dy = self.speed

    def update(self):
        if self.state == "entering":
            if self.y < self.target_mid_y:
                self.y += 2
            else:
                self.y = self.target_mid_y
                self.state = "waiting"

        elif self.state == "dropping":
            self.x += self.dx
            self.y += self.dy

            if (self.y > self.screen_height + self.height or
                    self.x < -self.width * 2 or
                    self.x > self.screen_width + self.width):
                self.state = "offscreen"

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.state != "offscreen":
            screen.blit(self.image, (self.x, self.y))
import pygame
import math

class Bullet:
    def __init__(self, x, y):
        self.width = 28
        self.height = 28
        self.x = x
        self.y = y
        self.speed = 9
        self.is_active = True
        self.angle = 0

        # Try loading custom image asset, otherwise construct procedurally
        try:
            raw = pygame.image.load("assets/bullet.png").convert_alpha()
            self.image = pygame.transform.scale(raw, (self.width, self.height))
            self.use_custom_asset = True
        except Exception:
            self.use_custom_asset = False
            self.image = self._create_shuriken_surface()

    def _create_shuriken_surface(self):
        """Generates a metallic 4-pointed Shinobi Shuriken with a glowing center."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        cx, cy = self.width // 2, self.height // 2
        r_outer = 13
        r_inner = 4

        # Draw 4 pointed blades
        blades = []
        for i in range(4):
            angle_rad = i * (math.pi / 2)
            tip_x = cx + r_outer * math.cos(angle_rad)
            tip_y = cy + r_outer * math.sin(angle_rad)

            side1_a = angle_rad + math.pi / 4
            side2_a = angle_rad - math.pi / 4

            p1_x = cx + r_inner * math.cos(side1_a)
            p1_y = cy + r_inner * math.sin(side1_a)
            p2_x = cx + r_inner * math.cos(side2_a)
            p2_y = cy + r_inner * math.sin(side2_a)

            blades.append([(tip_x, tip_y), (p1_x, p1_y), (cx, cy)])
            blades.append([(tip_x, tip_y), (p2_x, p2_y), (cx, cy)])

        for idx, poly in enumerate(blades):
            color = (220, 225, 235) if idx % 2 == 0 else (140, 150, 170)
            pygame.draw.polygon(surf, color, poly)

        # Center hole / ring
        pygame.draw.circle(surf, (40, 40, 50), (cx, cy), 4)
        pygame.draw.circle(surf, (0, 220, 255), (cx, cy), 2)
        return surf

    def update(self):
        self.y -= self.speed
        self.angle = (self.angle + 20) % 360
        if self.y < -self.height:
            self.is_active = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.is_active:
            rotated_img = pygame.transform.rotate(self.image, self.angle)
            new_rect = rotated_img.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(rotated_img, new_rect.topleft)
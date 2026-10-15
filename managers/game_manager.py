import pygame
import random
from entities.player import Player, SHIP_COLOR_MAP
from entities.button import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet
from entities.toggle import ToggleSwitch
from managers.db_manager import DBManager

# --- Constants & Configuration ---
SHIP_COLORS = ["cyan", "violet", "red", "yellow", "purple"]
SHIP_COLOR_RGB = {
    "cyan":   (0,   220, 255),
    "violet": (190, 0,   255),
    "red":    (255, 60,  60),
    "yellow": (255, 230, 0),
    "purple": (130, 0,   255),
}
CONTROL_SCHEMES = ["arrows", "wasd"]
DIFFICULTIES    = ["easy", "normal", "hard"]
DIFFICULTY_LABELS = {"easy": "Easy", "normal": "Normal", "hard": "Hard"}
DIFFICULTY_SPAWN  = {"easy": 3, "normal": 5, "hard": 8}

# Color Palette
DARK_BG       = (5, 8, 16)
ACCENT        = (0, 245, 255)
CYAN_ACCENT   = (120, 240, 255)
WHITE         = (255, 255, 255)
GRAY          = (130, 160, 190)
DARK_BTN      = (12, 24, 42)
SEL_BTN       = (0, 160, 220)
RED_ERR       = (255, 60, 100)
PANEL_BG      = (8, 16, 32, 238)
PANEL_BOR     = (58, 112, 156)
FIELD_BG      = (12, 26, 48)
ACCENT_DIM    = (0, 90, 140)
GOLD_COLOR    = (255, 215, 0)
SILVER_COLOR  = (192, 192, 192)
BRONZE_COLOR  = (205, 127, 50)

_BACKGROUND_CACHE = {}


# --- UI Helper Functions ---
def draw_glow_rect(screen, rect, color, radius=12, layers=4):
    for i in range(layers, 0, -1):
        expand = i * 4
        alpha  = max(8, 35 // i)
        glow_rect = rect.inflate(expand * 2, expand * 2)
        s = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=radius + expand)
        screen.blit(s, glow_rect.topleft)


def draw_cyber_panel(screen, rect, bg_color=PANEL_BG, border_color=PANEL_BOR, border_radius=16):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, bg_color, s.get_rect(), border_radius=border_radius)
    screen.blit(s, rect.topleft)
    pygame.draw.rect(screen, border_color, rect, 1, border_radius=border_radius)

    accent_len = 22
    pygame.draw.line(screen, ACCENT, (rect.x + 10, rect.y), (rect.x + 10 + accent_len, rect.y), 2)
    pygame.draw.line(screen, ACCENT, (rect.x, rect.y + 10), (rect.x, rect.y + 10 + accent_len), 2)
    pygame.draw.line(screen, ACCENT, (rect.right - 10 - accent_len, rect.bottom), (rect.right - 10, rect.bottom), 2)
    pygame.draw.line(screen, ACCENT, (rect.right, rect.bottom - 10 - accent_len), (rect.right, rect.bottom - 10), 2)


def draw_cyber_button(screen, font, rect, text, primary=True, hover=False):
    base_color = SEL_BTN if primary else DARK_BTN
    border_color = ACCENT if (primary or hover) else PANEL_BOR

    if primary or hover:
        draw_glow_rect(screen, rect, ACCENT if primary else (0, 160, 220), radius=12, layers=3)

    top_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 2)
    pygame.draw.rect(screen, base_color, rect, border_radius=12)

    if primary:
        top_surf = pygame.Surface((top_rect.width, top_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(top_surf, (255, 255, 255, 40), top_surf.get_rect(), border_top_left_radius=12, border_top_right_radius=12)
        screen.blit(top_surf, top_rect.topleft)

    pygame.draw.rect(screen, border_color, rect, 2, border_radius=12)
    pygame.draw.line(screen, WHITE if primary else CYAN_ACCENT, (rect.x + 14, rect.y + 3), (rect.x + rect.width - 14, rect.y + 3), 1)

    txt_surf = font.render(text, True, WHITE if (primary or hover) else GRAY)
    screen.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2, rect.centery - txt_surf.get_height() // 2))


def draw_text_field(screen, font, rect, text, placeholder, focused, masked=False,
                    selected=False, visible=False, toggle_rect=None, toggle_focused=False):
    border_color = ACCENT if focused else PANEL_BOR
    bg_color     = (20, 42, 75) if focused else FIELD_BG

    if focused:
        draw_glow_rect(screen, rect, ACCENT, radius=12, layers=2)

    pygame.draw.rect(screen, bg_color, rect, border_radius=12)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=12)

    display = ("●" * len(text)) if masked and not visible else text
    if display:
        surf = font.render(display, True, WHITE)
    else:
        surf = font.render(placeholder, True, (90, 130, 175))

    text_x = rect.x + 16
    text_y = rect.y + (rect.height - surf.get_height()) // 2

    if selected and display:
        selection_rect = pygame.Rect(text_x - 3, text_y - 2, surf.get_width() + 6, surf.get_height() + 4)
        pygame.draw.rect(screen, (0, 140, 220), selection_rect, border_radius=4)
        surf = font.render(display, True, WHITE)

    screen.blit(surf, (text_x, text_y))

    if masked and toggle_rect:
        draw_password_toggle(screen, toggle_rect, visible, toggle_focused)

    if focused and (pygame.time.get_ticks() // 500) % 2 == 0:
        cx_pos = rect.x + 16 + (surf.get_width() if display else 0) + 2
        pygame.draw.line(screen, ACCENT, (cx_pos, rect.y + 10), (cx_pos, rect.bottom - 10), 2)


def draw_password_toggle(screen, rect, visible, focused=False):
    bg = (30, 58, 95) if focused else (18, 36, 60)
    pygame.draw.rect(screen, bg, rect, border_radius=8)
    if focused:
        pygame.draw.rect(screen, ACCENT, rect, 2, border_radius=8)

    color = ACCENT if visible else GRAY
    pygame.draw.ellipse(screen, color, pygame.Rect(rect.x + 8, rect.y + 10, rect.width - 16, rect.height - 20), 2)
    pygame.draw.circle(screen, color, rect.center, 4)


def draw_divider(screen, cx, y, width=360, color=ACCENT_DIM):
    pygame.draw.line(screen, color, (cx - width // 2, y), (cx + width // 2, y), 2)
    pygame.draw.circle(screen, ACCENT, (cx, y), 3)


def draw_glow_title(screen, big_font, text, cx, y, color=ACCENT):
    glow = big_font.render(text, True, color)
    for dx, dy in [(-3, 3), (3, 3), (0, 4)]:
        gs = pygame.Surface(glow.get_size(), pygame.SRCALPHA)
        gs.blit(glow, (0, 0))
        gs.set_alpha(45)
        screen.blit(gs, (cx - glow.get_width() // 2 + dx, y + dy))
    surf = big_font.render(text, True, color)
    screen.blit(surf, (cx - surf.get_width() // 2, y))


def draw_animated_background(screen, width, height, stars):
    cache_key = (width, height)
    background = _BACKGROUND_CACHE.get(cache_key)
    if background is None:
        background = pygame.Surface((width, height))
        top_color, bottom_color = (5, 9, 23), (13, 11, 31)
        for y in range(height):
            blend = y / max(1, height - 1)
            color = tuple(int(top + (bottom - top) * blend) for top, bottom in zip(top_color, bottom_color))
            pygame.draw.line(background, color, (0, y), (width, y))

        haze = pygame.Surface((width, height), pygame.SRCALPHA)
        for center, color, max_radius in (
            ((int(width * 0.12), int(height * 0.25)), (24, 83, 133), 230),
            ((int(width * 0.86), int(height * 0.7)), (79, 38, 122), 270),
        ):
            for radius in range(max_radius, 0, -18):
                alpha = int(15 * (1 - radius / max_radius))
                bounds = pygame.Rect(0, 0, radius * 2, radius * 2)
                bounds.center = center
                pygame.draw.ellipse(haze, (*color, alpha), bounds)
        background.blit(haze, (0, 0))

        planet_center = (int(width * 0.84), int(height * 0.72))
        planet_radius = max(54, min(width, height) // 5)
        pygame.draw.circle(background, (10, 20, 42), planet_center, planet_radius)
        pygame.draw.circle(background, (27, 52, 82), planet_center, planet_radius, 1)
        pygame.draw.ellipse(
            background, (29, 65, 96),
            pygame.Rect(planet_center[0] - planet_radius - 46, planet_center[1] - 19, (planet_radius + 46) * 2, 38), 1,
        )
        _BACKGROUND_CACHE[cache_key] = background

    t = pygame.time.get_ticks()
    screen.blit(background, (0, 0))

    for i, (x, y, r, brightness) in enumerate(stars):
        flicker = int(brightness + 40 * ((t // 700 + i * 31) % 3 - 1) * 0.3)
        flicker = max(50, min(230, flicker))
        pygame.draw.circle(screen, (max(0, flicker - 50), flicker, 255), (x, y), r)


def draw_auth_branding(screen, big_font, small_font, width):
    center = (int(width * 0.205), 220)
    pygame.draw.circle(screen, (31, 91, 132), center, 82, 1)
    pygame.draw.circle(screen, (23, 60, 97), center, 66, 1)
    pygame.draw.ellipse(screen, (54, 109, 150), pygame.Rect(center[0] - 100, center[1] - 23, 200, 46), 1)
    pygame.draw.circle(screen, (8, 24, 47), center, 45)
    pygame.draw.circle(screen, ACCENT, center, 4)
    pygame.draw.line(screen, (38, 77, 110), (center[0] - 108, center[1]), (center[0] - 89, center[1]), 1)
    pygame.draw.line(screen, (38, 77, 110), (center[0] + 89, center[1]), (center[0] + 108, center[1]), 1)

    eyebrow = small_font.render("DEEP SPACE  /  PILOT NETWORK", True, CYAN_ACCENT)
    screen.blit(eyebrow, (48, 92))
    title_font = pygame.font.SysFont("Arial", 44, bold=True)
    for text, y in (("SPACE", 344), ("INVADERS", 390)):
        title = title_font.render(text, True, WHITE)
        screen.blit(title, (48, y))

    pygame.draw.rect(screen, ACCENT, pygame.Rect(50, 452, 34, 3), border_radius=2)
    description = small_font.render("A NEW FRONTIER AWAITS", True, GRAY)
    screen.blit(description, (50, 466))
    status = small_font.render("SYSTEM  ONLINE", True, (115, 194, 205))
    screen.blit(status, (50, 515))
    pygame.draw.circle(screen, (95, 232, 173), (56, 553), 4)
    screen.blit(small_font.render("FLIGHT DECK READY", True, GRAY), (68, 542))


def generate_stars(screen_width, screen_height, count=180):
    return [(random.randint(0, screen_width), random.randint(0, screen_height), random.choice([1, 1, 1, 2, 2]), random.randint(60, 180)) for _ in range(count)]


def clean_username(username):
    if not username:
        return "Guest"
    cleaned = "".join(c for c in username if c.isprintable() and ord(c) >= 32)
    return cleaned.strip() or "Guest"


def render_retro_score(score_val, color, scale=3):
    small_font = pygame.font.SysFont("Consolas", 14, bold=True)
    temp = small_font.render(str(score_val), False, color)
    w, h = temp.get_size()
    return pygame.transform.scale(temp, (int(w * scale), int(h * scale)))


def draw_option_row(screen, font, label, options, selected, y, x_start, item_w=120, item_h=40):
    label_surf = font.render(label, True, WHITE)
    screen.blit(label_surf, (x_start, y + 8))

    rects = []
    btn_x = x_start + 180
    for opt in options:
        rect = pygame.Rect(btn_x, y, item_w, item_h)
        color = SEL_BTN if opt == selected else DARK_BTN
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, ACCENT if opt == selected else GRAY, rect, 2, border_radius=10)

        if label == "Ship Color:":
            pygame.draw.circle(screen, SHIP_COLOR_RGB.get(opt, WHITE), (btn_x + item_w // 2, y + item_h // 2), 12)
            pygame.draw.circle(screen, WHITE if opt == selected else GRAY, (btn_x + item_w // 2, y + item_h // 2), 12, 2)
        else:
            disp = opt.upper() if label == "Controls:" else DIFFICULTY_LABELS.get(opt, opt.capitalize())
            txt = font.render(disp, True, WHITE)
            screen.blit(txt, (btn_x + (item_w - txt.get_width()) // 2, y + (item_h - txt.get_height()) // 2))

        rects.append((rect, opt))
        btn_x += item_w + 10
    return rects


# --- GameManager Class ---
class GameManager:
    def __init__(self, screen, screen_width, screen_height, player_name=""):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_name = player_name
        self.db = DBManager(user="root", password="")
        self.leaderboard = []
        self.stars = generate_stars(screen_width, screen_height)

        self.font       = pygame.font.SysFont("Arial", 26, bold=True)
        self.big_font   = pygame.font.SysFont("Arial", 56, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.tiny_font  = pygame.font.SysFont("Arial", 16, bold=True)

        cx = screen_width // 2

        self.name_input_rect   = pygame.Rect(cx - 160, 320, 320, 52)
        self.start_button_rect = pygame.Rect(cx - 110, 400, 220, 52)
        self.profile_btn_rect  = pygame.Rect(cx - 110, 468, 220, 42)
        self.reload_button_rect = pygame.Rect(cx - 110, screen_height // 2 + 50, 220, 52)

        self.profile_ship_color   = "cyan"
        self.profile_control      = "arrows"
        self.profile_difficulty   = "normal"
        self.profile_back_rect    = pygame.Rect(cx - 110, screen_height - 62, 220, 48)
        self.profile_option_rects = []

        self.profile_left_toggle  = ToggleSwitch(0, 0, 50, 24, initial_state=True)
        self.profile_right_toggle = ToggleSwitch(0, 0, 50, 24, initial_state=True)
        self.profile_fire_toggle  = ToggleSwitch(0, 0, 50, 24, initial_state=True)

        auth_cx = int(screen_width * 0.73)
        field_w = 340
        field_x = auth_cx - field_w // 2
        
        self.login_user_rect     = pygame.Rect(field_x, 212, field_w, 52)
        self.login_pass_rect     = pygame.Rect(field_x, 294, field_w, 52)
        self.login_pass_eye_rect = pygame.Rect(self.login_pass_rect.right - 44, self.login_pass_rect.y + 6, 36, 40)
        self.login_btn_rect      = pygame.Rect(field_x, 380, 158, 52)
        self.login_reg_btn_rect  = pygame.Rect(field_x + field_w - 158, 380, 158, 52)
        self.login_lb_btn_rect   = pygame.Rect(auth_cx - 110, 452, 220, 44)

        self.reg_user_rect     = pygame.Rect(field_x, 190, field_w, 52)
        self.reg_pass_rect     = pygame.Rect(field_x, 272, field_w, 52)
        self.reg_conf_rect     = pygame.Rect(field_x, 354, field_w, 52)
        self.reg_pass_eye_rect = pygame.Rect(self.reg_pass_rect.right - 44, self.reg_pass_rect.y + 6, 36, 40)
        self.reg_conf_eye_rect = pygame.Rect(self.reg_conf_rect.right - 44, self.reg_conf_rect.y + 6, 36, 40)
        self.reg_create_rect   = pygame.Rect(field_x, 434, 158, 52)
        self.reg_back_rect     = pygame.Rect(field_x + field_w - 158, 434, 158, 52)

        self.lb_back_rect = pygame.Rect(cx - 110, 528, 220, 46)

        self.login_username  = ""
        self.login_password  = ""
        self.login_focus     = "username"
        self.login_error     = ""
        self.login_password_visible = False

        self.reg_username    = ""
        self.reg_password    = ""
        self.reg_confirm     = ""
        self.reg_focus       = "username"
        self.reg_error       = ""
        self.reg_success     = ""
        self.reg_password_visible = False
        self.reg_confirm_visible = False

        self.old_name = ""
        self.reset_game()

    def reset_game(self):
        self.player  = Player(self.screen_width, self.screen_height, self.profile_ship_color)
        self.buttons = MobileButtons(
            left_enabled=self.profile_left_toggle.state,
            right_enabled=self.profile_right_toggle.state,
            fire_enabled=self.profile_fire_toggle.state
        )
        self.bullet  = None
        self.enemies = []

        self.score        = 0
        self.personal_best = 0
        self.spawn_number = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.game_state   = "login"

        self.old_name     = self.player_name
        self.player_history = []
        self.timer        = 0
        self.state_timer  = 0

        self.login_username = self.player_name
        self.login_password = ""
        self.login_error    = ""
        self.reg_username   = ""
        self.reg_password   = ""
        self.reg_confirm    = ""
        self.reg_error      = ""
        self.reg_success    = ""

    def _load_profile_from_db(self):
        if not self.player_name:
            return
        profile = self.db.get_player_profile(self.player_name)
        if profile:
            self.profile_ship_color = profile.get("ship_color", "cyan") or "cyan"
            self.profile_control    = profile.get("control_scheme", "arrows") or "arrows"
            self.profile_difficulty = profile.get("difficulty", "normal") or "normal"
            self.profile_left_toggle.state  = bool(profile.get("btn_left_enabled", 1))
            self.profile_right_toggle.state = bool(profile.get("btn_right_enabled", 1))
            self.profile_fire_toggle.state  = bool(profile.get("btn_fire_enabled", 1))
            self.player.set_color(self.profile_ship_color)
        self.personal_best = self.db.get_player_best_score(self.player_name)

    def _save_profile_to_db(self):
        if not self.player_name:
            return
        self.db.get_or_create_player(self.player_name)
        self.db.update_player_profile(
            self.player_name,
            ship_color     = self.profile_ship_color,
            control_scheme = self.profile_control,
            difficulty     = self.profile_difficulty,
            left_en        = self.profile_left_toggle.state,
            right_en       = self.profile_right_toggle.state,
            fire_en        = self.profile_fire_toggle.state,
        )

    def _after_login(self):
        self._load_profile_from_db()
        self.spawn_number = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.player.set_color(self.profile_ship_color)
        self.game_state = "name_input"

    def _start_game(self):
        self.player_name = self.player_name.strip() or "Guest"
        if self.old_name and self.old_name != self.player_name:
            self.db.update_player_username(self.old_name, self.player_name)
        self.db.get_or_create_player(self.player_name)
        self._load_profile_from_db()
        self.spawn_number = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.player.set_color(self.profile_ship_color)
        self.buttons = MobileButtons(
            left_enabled=self.profile_left_toggle.state,
            right_enabled=self.profile_right_toggle.state,
            fire_enabled=self.profile_fire_toggle.state
        )
        self.game_state = "playing"
        self.spawn_enemies()

    def _handle_text_input(self, event, field_name, max_len=50):
        current = getattr(self, field_name)
        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
        selection_attr = f"_{field_name}_select_all"
        selected = getattr(self, selection_attr, False)
        if event.key == pygame.K_a and ctrl:
            setattr(self, selection_attr, True)
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            current = "" if (ctrl or selected) else (current[:-1] if event.key == pygame.K_BACKSPACE else current)
            setattr(self, selection_attr, False)
        elif event.key == pygame.K_v and ctrl:
            try:
                clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                if clip:
                    text = clip.decode("utf-8", errors="ignore").replace("\x00", "").split("\n")[0]
                    if selected:
                        current = ""
                    current = (current + text)[:max_len]
            except Exception:
                pass
            setattr(self, selection_attr, False)
        elif event.unicode and event.unicode.isprintable() and event.key != pygame.K_TAB:
            if selected:
                current = ""
            if len(current) < max_len:
                current += event.unicode
            setattr(self, selection_attr, False)
        setattr(self, field_name, current)

    def spawn_enemies(self):
        self.enemies = [Enemy(i, self.spawn_number, self.screen_width, self.screen_height) for i in range(self.spawn_number)]
        self.timer = 0

    def update(self, events):
        state_handlers = {
            "login": self._update_login,
            "register": self._update_register,
            "leaderboard": self._update_leaderboard,
            "name_input": self._update_name_input,
            "profile": self._update_profile,
            "playing": self._update_playing,
            "blinking": self._update_playing,
            "game_over": self._update_game_over
        }
        handler = state_handlers.get(self.game_state)
        if handler:
            handler(events)

    def _update_login(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    order = ["username", "password", "password_toggle"]
                    idx = order.index(self.login_focus)
                    step = -1 if event.mod & pygame.KMOD_SHIFT else 1
                    self.login_focus = order[(idx + step) % len(order)]
                elif event.key == pygame.K_RETURN:
                    if self.login_focus == "password_toggle":
                        self.login_password_visible = not self.login_password_visible
                    else:
                        self._do_login()
                        return
                elif event.key == pygame.K_SPACE and self.login_focus == "password_toggle":
                    self.login_password_visible = not self.login_password_visible
                elif self.login_focus == "username":
                    self._handle_text_input(event, "login_username", max_len=50)
                elif self.login_focus == "password":
                    self._handle_text_input(event, "login_password", max_len=100)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.login_pass_eye_rect.collidepoint(event.pos):
                    self.login_focus = "password_toggle"
                    self.login_password_visible = not self.login_password_visible
                elif self.login_user_rect.collidepoint(event.pos):
                    self.login_focus = "username"
                elif self.login_pass_rect.collidepoint(event.pos):
                    self.login_focus = "password"
                elif self.login_btn_rect.collidepoint(event.pos):
                    self._do_login()
                    return
                elif self.login_reg_btn_rect.collidepoint(event.pos):
                    self.reg_username, self.reg_password, self.reg_confirm = self.login_username, "", ""
                    self.reg_error, self.reg_success, self.reg_focus, self.game_state = "", "", "username", "register"
                    return
                elif self.login_lb_btn_rect.collidepoint(event.pos):
                    self.leaderboard = self.db.get_top_scores(limit=10)
                    self.game_state = "leaderboard"
                    return

        self._draw_login(mouse_pos)

    def _do_login(self):
        if not self.login_username.strip():
            self.login_error = "Please enter a username."
            return
        if not self.login_password:
            self.login_error = "Please enter a password."
            return

        player_row = self.db.login_player(self.login_username.strip(), self.login_password)
        if player_row:
            self.player_name = player_row["username"]
            self.login_error = ""
            self.login_password = ""
            self._after_login()
        else:
            self.login_error = "Incorrect username or password."

    def _draw_login(self, mouse_pos=(0, 0)):
        self.screen.fill(DARK_BG)
        draw_animated_background(self.screen, self.screen_width, self.screen_height, self.stars)
        draw_auth_branding(self.screen, self.big_font, self.small_font, self.screen_width)

        auth_cx = int(self.screen_width * 0.73)
        heading_font = pygame.font.SysFont("Arial", 30, bold=True)
        heading = heading_font.render("PILOT ACCESS", True, WHITE)
        self.screen.blit(heading, (auth_cx - heading.get_width() // 2, 126))
        sub = self.small_font.render("SIGN IN TO CONTINUE", True, CYAN_ACCENT)
        self.screen.blit(sub, (auth_cx - sub.get_width() // 2, 164))

        panel = pygame.Rect(auth_cx - 200, 112, 400, 404)
        draw_cyber_panel(self.screen, panel)

        self.screen.blit(self.tiny_font.render("USERNAME", True, CYAN_ACCENT), (self.login_user_rect.x + 4, self.login_user_rect.y - 20))
        self.screen.blit(self.tiny_font.render("PASSWORD", True, CYAN_ACCENT), (self.login_pass_rect.x + 4, self.login_pass_rect.y - 20))

        draw_text_field(self.screen, self.font, self.login_user_rect, self.login_username, "Enter username...", self.login_focus == "username")
        draw_text_field(self.screen, self.font, self.login_pass_rect, self.login_password, "Enter password...", self.login_focus in ("password", "password_toggle"), masked=True, visible=self.login_password_visible, toggle_rect=self.login_pass_eye_rect, toggle_focused=self.login_focus == "password_toggle")

        draw_cyber_button(self.screen, self.font, self.login_btn_rect, "LOGIN", primary=True, hover=self.login_btn_rect.collidepoint(mouse_pos))
        draw_cyber_button(self.screen, self.font, self.login_reg_btn_rect, "REGISTER", primary=False, hover=self.login_reg_btn_rect.collidepoint(mouse_pos))

        draw_divider(self.screen, auth_cx, 440, width=340, color=ACCENT_DIM)
        draw_cyber_button(self.screen, self.small_font, self.login_lb_btn_rect, "LEADERBOARD", primary=False, hover=self.login_lb_btn_rect.collidepoint(mouse_pos))

        if self.login_error:
            err_bg = pygame.Rect(auth_cx - 185, 518, 370, 32)
            pygame.draw.rect(self.screen, (60, 12, 32), err_bg, border_radius=8)
            pygame.draw.rect(self.screen, RED_ERR, err_bg, 1, border_radius=8)
            err = self.small_font.render(self.login_error, True, RED_ERR)
            self.screen.blit(err, (auth_cx - err.get_width() // 2, 523))

        hint = self.tiny_font.render("Tab: Switch Field   •   Enter: Login", True, (90, 140, 190))
        self.screen.blit(hint, (auth_cx - hint.get_width() // 2, self.screen_height - 24))

    def _update_register(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    order = ["username", "password", "password_toggle", "confirm", "confirm_toggle"]
                    idx = order.index(self.reg_focus)
                    step = -1 if event.mod & pygame.KMOD_SHIFT else 1
                    self.reg_focus = order[(idx + step) % len(order)]
                elif event.key == pygame.K_RETURN:
                    if self.reg_focus == "password_toggle":
                        self.reg_password_visible = not self.reg_password_visible
                    elif self.reg_focus == "confirm_toggle":
                        self.reg_confirm_visible = not self.reg_confirm_visible
                    else:
                        self._do_register()
                        return
                elif event.key == pygame.K_SPACE and self.reg_focus == "password_toggle":
                    self.reg_password_visible = not self.reg_password_visible
                elif event.key == pygame.K_SPACE and self.reg_focus == "confirm_toggle":
                    self.reg_confirm_visible = not self.reg_confirm_visible
                elif self.reg_focus == "username":
                    self._handle_text_input(event, "reg_username", max_len=50)
                elif self.reg_focus == "password":
                    self._handle_text_input(event, "reg_password", max_len=100)
                elif self.reg_focus == "confirm":
                    self._handle_text_input(event, "reg_confirm", max_len=100)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.reg_pass_eye_rect.collidepoint(event.pos):
                    self.reg_focus, self.reg_password_visible = "password_toggle", not self.reg_password_visible
                elif self.reg_conf_eye_rect.collidepoint(event.pos):
                    self.reg_focus, self.reg_confirm_visible = "confirm_toggle", not self.reg_confirm_visible
                elif self.reg_user_rect.collidepoint(event.pos):
                    self.reg_focus = "username"
                elif self.reg_pass_rect.collidepoint(event.pos):
                    self.reg_focus = "password"
                elif self.reg_conf_rect.collidepoint(event.pos):
                    self.reg_focus = "confirm"
                elif self.reg_create_rect.collidepoint(event.pos):
                    self._do_register()
                    return
                elif self.reg_back_rect.collidepoint(event.pos):
                    self.game_state = "login"
                    return

        self._draw_register(mouse_pos)

    def _do_register(self):
        if not self.reg_username or len(self.reg_username) < 3:
            self.reg_error = "Username must be at least 3 characters."
            return
        if not self.reg_password or len(self.reg_password) < 4:
            self.reg_error = "Password must be at least 4 characters."
            return
        if self.reg_password != self.reg_confirm:
            self.reg_error = "Passwords do not match."
            return

        ok, result = self.db.register_player(self.reg_username.strip(), self.reg_password)
        if ok:
            self.player_name = self.reg_username.strip()
            self.reg_error = ""
            self.reg_success = f"Account created! Welcome, {self.player_name}!"
            self._after_login()
        else:
            self.reg_error = result

    def _draw_register(self, mouse_pos=(0, 0)):
        self.screen.fill(DARK_BG)
        draw_animated_background(self.screen, self.screen_width, self.screen_height, self.stars)
        draw_auth_branding(self.screen, self.big_font, self.small_font, self.screen_width)

        auth_cx = int(self.screen_width * 0.73)
        
        panel = pygame.Rect(auth_cx - 210, 96, 420, 460)
        draw_cyber_panel(self.screen, panel, bg_color=(6, 14, 28, 245), border_color=(75, 145, 195), border_radius=18)

        heading_font = pygame.font.SysFont("Arial", 28, bold=True)
        heading = heading_font.render("PILOT ENLISTMENT", True, WHITE)
        self.screen.blit(heading, (auth_cx - heading.get_width() // 2, 114))
        
        sub = self.tiny_font.render("ESTABLISH NEW SECURITY CREDENTIALS", True, CYAN_ACCENT)
        self.screen.blit(sub, (auth_cx - sub.get_width() // 2, 148))

        labels_data = [
            ("USERNAME ID (3+ CHARS)", self.reg_user_rect),
            ("SECURITY KEY (4+ CHARS)", self.reg_pass_rect),
            ("CONFIRM SECURITY KEY", self.reg_conf_rect),
        ]
        for lbl_text, f_rect in labels_data:
            self.screen.blit(self.tiny_font.render(lbl_text, True, (140, 180, 220)), (f_rect.x + 2, f_rect.y - 20))

        draw_text_field(self.screen, self.font, self.reg_user_rect, self.reg_username, "Choose callsign...", self.reg_focus == "username")
        draw_text_field(self.screen, self.font, self.reg_pass_rect, self.reg_password, "Secret passphrase...", self.reg_focus in ("password", "password_toggle"), masked=True, visible=self.reg_password_visible, toggle_rect=self.reg_pass_eye_rect, toggle_focused=self.reg_focus == "password_toggle")
        draw_text_field(self.screen, self.font, self.reg_conf_rect, self.reg_confirm, "Verify passphrase...", self.reg_focus in ("confirm", "confirm_toggle"), masked=True, visible=self.reg_confirm_visible, toggle_rect=self.reg_conf_eye_rect, toggle_focused=self.reg_focus == "confirm_toggle")

        draw_cyber_button(self.screen, self.font, self.reg_create_rect, "ENLIST", primary=True, hover=self.reg_create_rect.collidepoint(mouse_pos))
        draw_cyber_button(self.screen, self.font, self.reg_back_rect, "ABORT", primary=False, hover=self.reg_back_rect.collidepoint(mouse_pos))

        msg_y = 502
        if self.reg_error:
            err_bg = pygame.Rect(auth_cx - 195, msg_y, 390, 36)
            pygame.draw.rect(self.screen, (50, 10, 26), err_bg, border_radius=10)
            pygame.draw.rect(self.screen, RED_ERR, err_bg, 1, border_radius=10)
            err_surf = self.small_font.render(self.reg_error, True, RED_ERR)
            self.screen.blit(err_surf, (auth_cx - err_surf.get_width() // 2, msg_y + 8))
        elif self.reg_success:
            ok_bg = pygame.Rect(auth_cx - 195, msg_y, 390, 36)
            pygame.draw.rect(self.screen, (10, 45, 35), ok_bg, border_radius=10)
            pygame.draw.rect(self.screen, (80, 240, 160), ok_bg, 1, border_radius=10)
            ok_surf = self.small_font.render(self.reg_success, True, (120, 255, 180))
            self.screen.blit(ok_surf, (auth_cx - ok_surf.get_width() // 2, msg_y + 8))

        hint = self.tiny_font.render("[TAB] Navigate Fields   •   [ENTER] Submit Enlistment", True, (100, 150, 200))
        self.screen.blit(hint, (auth_cx - hint.get_width() // 2, self.screen_height - 26))

    def _update_leaderboard(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.lb_back_rect.collidepoint(event.pos):
                self.game_state = "login"
                return
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.game_state = "login"
                return
        self._draw_leaderboard(pygame.mouse.get_pos())

    def _draw_leaderboard(self, mouse_pos=(0, 0)):
        self.screen.fill(DARK_BG)
        draw_animated_background(self.screen, self.screen_width, self.screen_height, self.stars)

        cx = self.screen_width // 2
        
        draw_glow_title(self.screen, self.big_font, "HALL OF FAME", cx, 24, color=ACCENT)
        sub = self.small_font.render("GLOBAL ELITE PILOT RANKINGS // ALL-TIME ARCHIVE", True, (140, 180, 220))
        self.screen.blit(sub, (cx - sub.get_width() // 2, 94))
        draw_divider(self.screen, cx, 122, width=420, color=ACCENT_DIM)

        table_rect = pygame.Rect(cx - 340, 138, 680, 376)
        draw_cyber_panel(self.screen, table_rect, bg_color=(6, 14, 28, 248), border_radius=18)

        header_y = 154
        rank_x, name_x, score_center_x, date_x = cx - 300, cx - 190, cx + 110, cx + 210

        for h_text, h_x in [("RANK", rank_x), ("PILOT CALLSIGN", name_x), ("LOGGED DATE", date_x)]:
            self.screen.blit(self.tiny_font.render(h_text, True, CYAN_ACCENT), (h_x, header_y))
        score_lbl_surf = self.tiny_font.render("SCORE", True, CYAN_ACCENT)
        self.screen.blit(score_lbl_surf, (score_center_x - score_lbl_surf.get_width() // 2, header_y))

        pygame.draw.line(self.screen, (45, 95, 140), (table_rect.x + 16, header_y + 26), (table_rect.right - 16, header_y + 26), 1)

        if not self.leaderboard:
            no_data = self.font.render("NO FLIGHT TELEMETRY RECORDED YET", True, GRAY)
            self.screen.blit(no_data, (cx - no_data.get_width() // 2, 290))
        else:
            row_y = header_y + 36
            badge_colors = {1: GOLD_COLOR, 2: SILVER_COLOR, 3: BRONZE_COLOR}
            medals = {1: "★ 01", 2: "★ 02", 3: "★ 03"}
            for i, entry in enumerate(self.leaderboard, start=1):
                display_name = clean_username(entry["username"])
                is_me = (entry["username"] == self.player_name)
                row_color = ACCENT if is_me else WHITE

                strip = pygame.Rect(table_rect.x + 10, row_y - 4, table_rect.width - 20, 30)
                if is_me:
                    s = pygame.Surface((strip.width, strip.height), pygame.SRCALPHA)
                    s.fill((0, 245, 255, 55))
                    self.screen.blit(s, strip.topleft)
                    pygame.draw.rect(self.screen, ACCENT, strip, 1, border_radius=6)
                elif i % 2 == 0:
                    s = pygame.Surface((strip.width, strip.height), pygame.SRCALPHA)
                    s.fill((255, 255, 255, 12))
                    self.screen.blit(s, strip.topleft)

                rank_str = medals.get(i, f"   {i:02d}")
                self.screen.blit(self.small_font.render(rank_str, True, badge_colors.get(i, (160, 200, 230))), (rank_x, row_y))
                self.screen.blit(self.small_font.render(display_name[:20], True, row_color), (name_x, row_y))
                
                score_surf = self.font.render(str(entry["score"]), True, row_color)
                self.screen.blit(score_surf, (score_center_x - score_surf.get_width() // 2, row_y - 2))
                
                date_str = str(entry.get("achieved_at"))[:10] if entry.get("achieved_at") else "—"
                self.screen.blit(self.tiny_font.render(date_str, True, (120, 150, 180)), (date_x, row_y + 4))
                row_y += 32

        self.lb_back_rect = pygame.Rect(cx - 110, 528, 220, 46)
        draw_cyber_button(self.screen, self.font, self.lb_back_rect, "< RETURN", primary=False, hover=self.lb_back_rect.collidepoint(mouse_pos))

    def _update_name_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                ctrl_held = pygame.key.get_mods() & pygame.KMOD_CTRL
                if event.key == pygame.K_BACKSPACE:
                    if ctrl_held or getattr(self, "_name_select_all", False):
                        self.player_name = ""
                        self._name_select_all = False
                    else:
                        self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_a and ctrl_held:
                    self._name_select_all = True
                elif event.key == pygame.K_v and ctrl_held:
                    try:
                        clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                        if clip:
                            text = clip.decode("utf-8", errors="ignore").replace("\x00", "").split("\n")[0]
                            self.player_name = (("" if getattr(self, "_name_select_all", False) else self.player_name) + text)[:15]
                            self._name_select_all = False
                    except Exception:
                        pass
                elif event.key == pygame.K_RETURN:
                    self._start_game()
                    return
                elif event.key != pygame.K_TAB and event.unicode.isprintable():
                    if getattr(self, "_name_select_all", False):
                        self.player_name = event.unicode
                        self._name_select_all = False
                    elif len(self.player_name) < 15:
                        self.player_name += event.unicode
                else:
                    self._name_select_all = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.start_button_rect.collidepoint(event.pos):
                    self._start_game()
                    return
                if self.profile_btn_rect.collidepoint(event.pos):
                    self.player_name = self.player_name.strip() or "Guest"
                    self.db.get_or_create_player(self.player_name)
                    self._load_profile_from_db()
                    self.game_state = "profile"
                    return

        self.screen.fill(DARK_BG)
        draw_animated_background(self.screen, self.screen_width, self.screen_height, self.stars)

        cx = self.screen_width // 2
        draw_glow_title(self.screen, self.big_font, "SPACE INVADERS", cx, 48, color=ACCENT)
        draw_divider(self.screen, cx, 126, width=280, color=ACCENT_DIM)

        card = pygame.Rect(cx - 210, 142, 420, 96)
        draw_cyber_panel(self.screen, card)

        self.screen.blit(self.tiny_font.render("PILOT", True, CYAN_ACCENT), (cx - 180, card.y + 22))
        self.screen.blit(self.font.render(self.player_name, True, WHITE), (cx - 180, card.y + 44))
        pygame.draw.line(self.screen, PANEL_BOR, (cx, card.y + 16), (cx, card.bottom - 16), 1)

        pb_rect = pygame.Rect(cx + 20, card.y + 18, 160, 60)
        pygame.draw.rect(self.screen, FIELD_BG, pb_rect, border_radius=12)
        pygame.draw.rect(self.screen, PANEL_BOR, pb_rect, 1, border_radius=12)

        self.screen.blit(self.tiny_font.render("BEST SCORE", True, CYAN_ACCENT), (pb_rect.centerx - 42, pb_rect.y + 8))
        self.screen.blit(render_retro_score(self.personal_best, WHITE, scale=1.8), (pb_rect.centerx - 30, pb_rect.y + 26))

        self.screen.blit(self.tiny_font.render("DISPLAY NAME", True, CYAN_ACCENT), (self.name_input_rect.x + 4, self.name_input_rect.y - 22))
        draw_text_field(self.screen, self.font, self.name_input_rect, self.player_name, "Your display name...", True, selected=getattr(self, "_name_select_all", False))
        draw_cyber_button(self.screen, self.font, self.start_button_rect, "PLAY", primary=True)
        draw_cyber_button(self.screen, self.small_font, self.profile_btn_rect, "EDIT PROFILE", primary=False)

    def _update_profile(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            self.profile_left_toggle.handle_event(event)
            self.profile_right_toggle.handle_event(event)
            self.profile_fire_toggle.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, category, value in self.profile_option_rects:
                    if rect.collidepoint(event.pos):
                        if category == "color":
                            self.profile_ship_color = value
                            self.player.set_color(value)
                        elif category == "control":
                            self.profile_control = value
                        elif category == "difficulty":
                            self.profile_difficulty = value
                if self.profile_back_rect.collidepoint(event.pos):
                    self._save_profile_to_db()
                    self.game_state = "name_input"

        self._draw_profile(mouse_pos)

    def _draw_profile(self, mouse_pos=(0, 0)):
        self.screen.fill(DARK_BG)
        draw_animated_background(self.screen, self.screen_width, self.screen_height, self.stars)
        self.profile_option_rects = []

        cx = self.screen_width // 2
        
        # Redesigned Modernized Profile Holographic Window
        draw_glow_title(self.screen, self.big_font, "PILOT HANGAR", cx, 14, color=ACCENT)
        sub = self.small_font.render("CONFIGURATION & TACTICAL PREFERENCES", True, (140, 180, 220))
        self.screen.blit(sub, (cx - sub.get_width() // 2, 80))
        draw_divider(self.screen, cx, 106, width=380, color=ACCENT_DIM)

        main_panel = pygame.Rect(cx - 320, 118, 640, 396)
        draw_cyber_panel(self.screen, main_panel, bg_color=(6, 14, 28, 248), border_radius=18)

        # Pilot Identity & Ship Preview Sub-card
        id_card = pygame.Rect(main_panel.x + 16, main_panel.y + 16, main_panel.width - 32, 68)
        pygame.draw.rect(self.screen, (12, 28, 52), id_card, border_radius=12)
        pygame.draw.rect(self.screen, (55, 115, 160), id_card, 1, border_radius=12)

        self.screen.blit(self.tiny_font.render("ACTIVE CALLSIGN", True, CYAN_ACCENT), (id_card.x + 18, id_card.y + 12))
        self.screen.blit(self.font.render(clean_username(self.player_name), True, WHITE), (id_card.x + 18, id_card.y + 30))

        # Live Ship Preview Box
        preview_box = pygame.Rect(id_card.right - 92, id_card.y + 10, 80, 48)
        pygame.draw.rect(self.screen, (8, 18, 36), preview_box, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT, preview_box, 1, border_radius=8)
        self.screen.blit(self.player.image, (preview_box.centerx - self.player.image.get_width() // 2, preview_box.centery - self.player.image.get_height() // 2))

        # Interactive Option Rows inside Main Panel
        x_start = main_panel.x + 22
        y = id_card.bottom + 14

        for label, options, current, item_w, cat in [
            ("Ship Color:", SHIP_COLORS, self.profile_ship_color, 74, "color"),
            ("Controls:", CONTROL_SCHEMES, self.profile_control, 116, "control"),
            ("Difficulty:", DIFFICULTIES, self.profile_difficulty, 100, "difficulty")
        ]:
            rects = draw_option_row(self.screen, self.small_font, label, options, current, y, x_start, item_w=item_w, item_h=34)
            self.profile_option_rects += [(r, cat, v) for r, v in rects]
            y += 44

        # Mobile Buttons Sub-Panel Customizer Integration
        toggles_panel = pygame.Rect(x_start, y + 4, main_panel.width - 44, 88)
        pygame.draw.rect(self.screen, (10, 22, 42), toggles_panel, border_radius=12)
        pygame.draw.rect(self.screen, (45, 95, 140), toggles_panel, 1, border_radius=12)
        
        self.screen.blit(self.tiny_font.render("MOBILE TOUCH CONTROLS CUSTOMIZER", True, CYAN_ACCENT), (toggles_panel.x + 14, toggles_panel.y + 10))

        self.profile_left_toggle.rect.topleft  = (toggles_panel.x + 85, toggles_panel.y + 46)
        self.profile_right_toggle.rect.topleft = (toggles_panel.x + 255, toggles_panel.y + 46)
        self.profile_fire_toggle.rect.topleft  = (toggles_panel.x + 425, toggles_panel.y + 46)

        for lbl, offset in [("Left", 28), ("Right", 192), ("Fire", 364)]:
            self.screen.blit(self.tiny_font.render(lbl, True, WHITE), (toggles_panel.x + offset, toggles_panel.y + 50))

        self.profile_left_toggle.draw(self.screen)
        self.profile_right_toggle.draw(self.screen)
        self.profile_fire_toggle.draw(self.screen)

        # Bottom Save Action Button
        draw_cyber_button(self.screen, self.font, self.profile_back_rect, "SAVE & RETURN", primary=True, hover=self.profile_back_rect.collidepoint(mouse_pos))

    def _update_playing(self, events):
        if self.game_state in ("playing", "blinking"):
            self.player_history.append((self.player.x, self.player.y))
            if len(self.player_history) > 60:
                self.player_history.pop(0)

        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            use_wasd = (self.profile_control == "wasd")
            if keys[pygame.K_a if use_wasd else pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_d if use_wasd else pygame.K_RIGHT]:
                self.player.move_right()

            screen_button_fired = self.buttons.handle_mouse(self.player, events)
            keyboard_fired = any(e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE for e in events)

            if (screen_button_fired or keyboard_fired) and self.bullet is None:
                self.bullet = Bullet(self.player.x + self.player.width // 2 - 16, self.player.y)

            self.player.keep_inside_screen()

            if self.bullet:
                self.bullet.update()
                if not self.bullet.is_active:
                    self.bullet = None

            self.timer += 1
            if self.timer >= 180:
                waiting = [e for e in self.enemies if e.state == "waiting"]
                if waiting:
                    chosen = random.choice(waiting)
                    tx, ty = self.player_history[-1] if self.player_history else (self.player.x, self.player.y)
                    chosen.start_drop(tx, ty)
                    self.timer = 0

            all_despawned = all(e.state == "offscreen" for e in self.enemies)
            for enemy in self.enemies:
                enemy.update()

            if all_despawned:
                self.spawn_number += 1
                self.spawn_enemies()

            self.check_collisions()

        elif self.game_state == "blinking":
            self.player.update_blink()
            self.state_timer += 1
            for enemy in self.enemies:
                enemy.update()

            if self.state_timer >= 180:
                self.db.save_score(self.player_name, self.score)
                if self.score > self.personal_best:
                    self.personal_best = self.score
                self.leaderboard = self.db.get_top_scores(limit=10)
                self.game_state = "game_over"

        self.screen.fill(DARK_BG)
        draw_animated_background(self.screen, self.screen_width, self.screen_height, self.stars)

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        if self.bullet:
            self.bullet.draw(self.screen)
        self.buttons.draw(self.screen)

        for y_off, label, val in [(10, "SCORE", self.score), (54, "BEST", self.personal_best)]:
            bg = pygame.Rect(10, y_off, 150, 38)
            pygame.draw.rect(self.screen, FIELD_BG, bg, border_radius=8)
            pygame.draw.rect(self.screen, PANEL_BOR, bg, 1, border_radius=8)
            self.screen.blit(self.tiny_font.render(label, True, CYAN_ACCENT), (20, y_off + 10))
            self.screen.blit(render_retro_score(val, WHITE, scale=1.8), (84, y_off + 7))

        ctrl_hint = "← → Move  |  SPACE Shoot" if self.profile_control == "arrows" else "A D Move  |  SPACE Shoot"
        hint_surf = self.tiny_font.render(ctrl_hint, True, GRAY)
        self.screen.blit(hint_surf, (self.screen_width - hint_surf.get_width() - 12, 14))

        diff_colors = {"easy": (0, 245, 255), "normal": (130, 210, 255), "hard": (255, 80, 120)}
        diff_surf = self.small_font.render(self.profile_difficulty.upper(), True, diff_colors.get(self.profile_difficulty, WHITE))
        self.screen.blit(diff_surf, (self.screen_width - diff_surf.get_width() - 12, 32))

    def _update_game_over(self, events):
        cx = self.screen_width // 2
        lb_count = min(len(self.leaderboard), 5)
        view_lb_y = 274 + max(lb_count, 1) * 34 + 12
        self.view_lb_btn_rect   = pygame.Rect(cx - 120, view_lb_y, 240, 44)
        self.reload_button_rect = pygame.Rect(cx - 100, view_lb_y + 54, 200, 50)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.reload_button_rect.collidepoint(event.pos):
                    s_name, s_best, s_col, s_ctrl, s_diff = self.player_name, self.personal_best, self.profile_ship_color, self.profile_control, self.profile_difficulty
                    self.reset_game()
                    self.player_name, self.personal_best, self.profile_ship_color, self.profile_control, self.profile_difficulty = s_name, s_best, s_col, s_ctrl, s_diff
                    self.player.set_color(s_col)
                    self.spawn_number = DIFFICULTY_SPAWN.get(s_diff, 5)
                    self.game_state = "name_input"
                    return
                if self.view_lb_btn_rect.collidepoint(event.pos):
                    self.game_state = "leaderboard"
                    return

        self.screen.fill(DARK_BG)
        draw_animated_background(self.screen, self.screen_width, self.screen_height, self.stars)
        draw_glow_title(self.screen, self.big_font, "GAME OVER", cx, 24, color=ACCENT)

        score_card = pygame.Rect(cx - 160, 96, 320, 96)
        draw_cyber_panel(self.screen, score_card)
        sc_lbl = self.tiny_font.render("FINAL SCORE", True, CYAN_ACCENT)
        self.screen.blit(sc_lbl, (cx - sc_lbl.get_width() // 2, 106))
        self.screen.blit(render_retro_score(self.score, WHITE, scale=3.6), (cx - 70, 130))

        if self.score >= self.personal_best and self.score > 0:
            nb_bg = pygame.Rect(cx - 120, 200, 240, 28)
            pygame.draw.rect(self.screen, FIELD_BG, nb_bg, border_radius=8)
            pygame.draw.rect(self.screen, ACCENT, nb_bg, 1, border_radius=8)
            nb_surf = self.small_font.render("New Personal Best!", True, ACCENT)
            self.screen.blit(nb_surf, (cx - nb_surf.get_width() // 2, 202))

        lb_title = self.small_font.render("TOP PILOTS", True, CYAN_ACCENT)
        self.screen.blit(lb_title, (cx - lb_title.get_width() // 2, 242))
        draw_divider(self.screen, cx, 266, width=360, color=ACCENT_DIM)

        y_offset = 274
        if self.leaderboard:
            rank_colors = {1: GOLD_COLOR, 2: SILVER_COLOR, 3: BRONZE_COLOR}
            for i, entry in enumerate(self.leaderboard[:5], start=1):
                display_name = clean_username(entry["username"])
                is_me = (entry["username"] == self.player_name)
                row_col, rk_col = (ACCENT if is_me else WHITE), rank_colors.get(i, (ACCENT if is_me else WHITE))

                if is_me:
                    hi = pygame.Rect(cx - 190, y_offset - 3, 380, 30)
                    hs = pygame.Surface((hi.width, hi.height), pygame.SRCALPHA)
                    hs.fill((0, 245, 255, 35))
                    self.screen.blit(hs, hi.topleft)

                self.screen.blit(self.small_font.render(str(i), True, rk_col), (cx - 185, y_offset))
                self.screen.blit(self.small_font.render(display_name[:16], True, row_col), (cx - 155, y_offset))
                self.screen.blit(self.font.render(str(entry["score"]), True, row_col), (cx + 80, y_offset - 2))
                y_offset += 34
        else:
            no_scores = self.small_font.render("No scores recorded yet", True, GRAY)
            self.screen.blit(no_scores, (cx - no_scores.get_width() // 2, y_offset))

        draw_cyber_button(self.screen, self.small_font, self.view_lb_btn_rect, "Full Leaderboard", primary=False)
        draw_cyber_button(self.screen, self.font, self.reload_button_rect, "PLAY AGAIN", primary=True)

    def check_collisions(self):
        player_rect = self.player.get_rect()
        for enemy in self.enemies:
            if enemy.state == "offscreen":
                continue
            enemy_rect = enemy.get_rect()
            if player_rect.colliderect(enemy_rect):
                self.game_state, self.player.is_blinking, self.state_timer = "blinking", True, 0
                return
            if self.bullet and self.bullet.get_rect().colliderect(enemy_rect):
                enemy.state = "offscreen"
                self.bullet = None
                self.score += 1
                break
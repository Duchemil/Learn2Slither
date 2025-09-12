import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_SIZE, GRID_SIZE,
    CELL_SIZE, SNAKE_COLOR, SNAKE_EYE_COLOR
)
from snake_game import play, play_multiple_games
import itertools

BTN_COLOR = (60, 120, 220)
BTN_HOVER = (80, 140, 240)
TEXT = (240, 240, 240)
TITLE = (255, 255, 255)


class Button:
    def __init__(self, rect, text, onclick):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.onclick = onclick
        self.hover = False

    def draw(self, screen, font):
        color = BTN_HOVER if self.hover else BTN_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        label = font.render(self.text, True, TEXT)
        screen.blit(label, (self.rect.centerx - label.get_width()//2,
                            self.rect.centery - label.get_height()//2))

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.onclick()


class LobbyScene:
    def __init__(self, q_table, defaults=None):
        self.q_table = q_table
        self.font = pygame.font.Font(None, 30)
        self.title_font = pygame.font.Font(None, 64)
        self.status = ""

        # Simple defaults (extend or replace with a proper Settings scene)
        self.cfg = {
            "episodes": 1000,
            "epsilon": 0.01,
            "alpha": 0.1,
            "gamma": 0.9,
            "verbose": False,
            "max": 0,
        }
        if defaults:
            self.cfg.update(defaults)

        x = SCREEN_SIZE + 20
        w = SCREEN_WIDTH - SCREEN_SIZE - 40
        h = 50
        gap = 20
        labels = [
            ("Play", self.on_play),
            ("Play Max", self.on_play_multiple),
            ("Toggle Verbose", self.on_toggle_verbose),
            ("Quit", self.on_quit),
        ]
        n = len(labels)
        total = n * h + (n - 1) * gap
        # Center vertically but keep a minimum top margin
        y_start = max(20, (SCREEN_HEIGHT - total) // 2)

        self.buttons = []
        y = y_start
        for text, cb in labels:
            self.buttons.append(Button((x, y, w, h), text, cb))
            y += h + gap

    def on_play(self):
        self.status = "Starting game..."
        play(self.q_table, verbose=self.cfg["verbose"])
        self.status = "Returned from game."

    def on_play_multiple(self):
        try:
            nb_games = int(input("Enter the number of games to play: "))
            if nb_games <= 0:
                raise ValueError("Number of games must be positive.")
            self.status = f"Playing {nb_games} games..."
            play_multiple_games(self.q_table, verbose=self.cfg["verbose"],
                                num_games=nb_games)
            self.status = f"Finished playing {nb_games} games."
        except ValueError as e:
            self.status = f"Invalid input: {e}"

    def on_quit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def on_toggle_verbose(self):
        self.cfg["verbose"] = not self.cfg["verbose"]
        self.status = f"Verbose: {self.cfg['verbose']}"

    def handle_event(self, event):
        for b in self.buttons:
            b.handle(event)

    def update(self, dt): pass

    def draw(self, screen):
        # Left: game board area with checkered grid
        for x in range(0, SCREEN_SIZE, CELL_SIZE):
            for y in range(0, SCREEN_SIZE, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                if (x // CELL_SIZE + y // CELL_SIZE) % 2 == 0:
                    color = (100, 149, 237)
                else:
                    color = (70, 130, 180)
                pygame.draw.rect(screen, color, rect)
        # Draw “snake” forming "42"
        snake_cells = _make_42_coords()
        if snake_cells:
            # Head = first cell
            head_x, head_y = snake_cells[0]
            for cx, cy in snake_cells:
                rect = pygame.Rect(cx * CELL_SIZE, cy * CELL_SIZE,
                                   CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, SNAKE_COLOR, rect, border_radius=4)
            # Draw simple eyes on head
            head_px = head_x * CELL_SIZE
            head_py = head_y * CELL_SIZE
            eye_r = CELL_SIZE // 8
            eye_off = CELL_SIZE // 4
            pygame.draw.circle(screen, SNAKE_EYE_COLOR, (head_px + eye_off,
                                                         head_py + eye_off),
                               eye_r)
            pygame.draw.circle(screen, SNAKE_EYE_COLOR,
                               (head_px + CELL_SIZE - eye_off,
                                head_py + eye_off), eye_r)

        title_text = "Learn2Slither"
        neon_colors = itertools.cycle([(255, 0, 0), (255, 127, 0),
                                       (255, 255, 0), (0, 255, 0),
                                       (0, 255, 255), (0, 0, 255),
                                       (139, 0, 255)])
        x_offset = 20

        for char in title_text:
            color = next(neon_colors)
            title = self.title_font.render(char, True, color)
            title.set_alpha(200)  # Neon effect
            screen.blit(title, (x_offset, 20))
            x_offset += title.get_width()

        # Right panel and buttons
        for b in self.buttons:
            b.draw(screen, self.font)


def _digit_glyph(d):
    # 3x5 monospace glyphs
    if d == '4':
        return [
            "#.#",
            "#.#",
            "###",
            "..#",
            "..#",
        ]
    if d == '2':
        return [
            "###",
            "..#",
            "###",
            "#..",
            "###",
        ]
    raise ValueError("Unsupported digit")


def _make_42_coords():
    # Build grid coords for "42" within GRID_SIZE, scaled and centered
    glyph_h = 5
    glyph_w = 3
    space_w = 1
    total_w = glyph_w + space_w + glyph_w
    # Scale to fit grid nicely
    sx = max(1, GRID_SIZE // total_w)
    sy = max(1, GRID_SIZE // glyph_h)
    s = min(sx, sy)
    total_w_px = total_w * s
    total_h_px = glyph_h * s
    off_x = (GRID_SIZE - total_w_px) // 2
    off_y = (GRID_SIZE - total_h_px) // 2

    coords = []
    # Place '4'
    g4 = _digit_glyph('4')
    for gy, row in enumerate(g4):
        for gx, ch in enumerate(row):
            if ch == '#':
                for yy in range(s):
                    for xx in range(s):
                        coords.append((off_x + gx * s + xx,
                                       off_y + gy * s + yy))
    # Place '2'
    g2 = _digit_glyph('2')
    dx2 = (glyph_w + space_w) * s
    for gy, row in enumerate(g2):
        for gx, ch in enumerate(row):
            if ch == '#':
                for yy in range(s):
                    for xx in range(s):
                        coords.append((off_x + dx2 + gx * s + xx,
                                       off_y + gy * s + yy))
    return coords

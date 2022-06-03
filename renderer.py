import pygame
from pygame import gfxdraw
from pygame.locals import QUIT

def hexcol(code):
    tmp = code
    if tmp[0] == "#":
        tmp = code[1:]
    r = int(tmp[:2], 16)
    g = int(tmp[2:4], 16)
    b = int(tmp[4:6], 16)
    return (r, g, b)


class Colors:
    BKG = hexcol("#bbada0")
    TOOL_BKG = hexcol("#7d736a")
    RED = hexcol("#dd0000")
    BY_VAL = {
        0: hexcol("#ccc1b4"),
        2: hexcol("#eee4da"),
        4: hexcol("#ede0c8"),
        8: hexcol("#f2b179"),
        16: hexcol("#f59563"),
        32: hexcol("#f67c5f"),
        64: hexcol("#f65e3b"),
        128: hexcol("#edcf72"),
        256: hexcol("#edcc61"),
        512: hexcol("#edc850"),
        1024: hexcol("#edc53f"),
        2048: hexcol("#edc22e")
    }
    DARK_TEXT = hexcol("#776e65")
    LIGHT_TEXT = hexcol("#f9f6f2")


class TextRenderer:
    @staticmethod
    def draw_text(font, color, surf, targetRect, text, center=True):
        fontSurf = font.render(text, True, color)
        fontRect = fontSurf.get_rect()
        drawRect = targetRect
        if center:
            drawRect = pygame.Rect(targetRect.left + (targetRect.width - fontRect.width) / 2, targetRect.top + (targetRect.height - fontRect.height) / 2, fontRect.width, fontRect.height)
        surf.blit(fontSurf, drawRect)


class GameRenderer:
    SIZE = 640
    TOOLBAR_HEIGHT = 64
    def __init__(self, board, agent):
        pygame.init()
        # Create screen
        self.screen = pygame.display.set_mode(size=(self.SIZE, self.SIZE + self.TOOLBAR_HEIGHT))
        pygame.display.set_caption("2048 AI v5.0")
        # Set up sync timing
        self.clock = pygame.time.Clock()
        # Get font
        self.roboto20 = pygame.font.Font('Roboto-Regular.ttf', 20)
        self.roboto48 = pygame.font.Font('Roboto-Bold.ttf', 48)
        self.roboto64 = pygame.font.Font('Roboto-Bold.ttf', 64)
        self.roboto72 = pygame.font.Font('Roboto-Bold.ttf', 72)
        # Connect to board
        self.board = board
        # Create game over surface
        self.game_over = pygame.Surface((self.SIZE, self.SIZE)).convert_alpha()
        gameOverColor = Colors.BY_VAL[0]
        self.game_over.fill((gameOverColor[0], gameOverColor[1], gameOverColor[2], 192))
        # Attach agent
        self.agent = agent
        self.agent.board_ref = self
    
    def get_board_rect(self):
        return pygame.Rect(0, 0, self.SIZE, self.SIZE)
    
    def get_toolbar_rect(self):
        return pygame.Rect(0, self.SIZE, self.SIZE, self.TOOLBAR_HEIGHT)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                raise SystemExit
            elif event.type == pygame.KEYDOWN and not self.board.no_moves():
                if event.key == pygame.K_LEFT:
                    self.board.press_left()
                elif event.key == pygame.K_UP:
                    self.board.press_up()
                elif event.key == pygame.K_RIGHT:
                    self.board.press_right()
                elif event.key == pygame.K_DOWN:
                    self.board.press_down()

    def sync(self):
        pygame.display.flip()
        self.clock.tick(165)  # lmao 165 Hz screen be like

    def run_agent(self):
        if not self.board.no_moves():
            text = self.agent.move()
            self.board = self.agent.root.board
            return text
        else:
            return ""

    def draw(self, toolbar_text):
        self.handle_events()
        # Begin Draw
        self.screen.fill(Colors.BKG)
        # Draw pieces
        for yi in range(4):
            for xi in range(4):
                self.draw_piece(self.board.pieces[yi][xi], xi, yi)
        # Draw toolbar
        gfxdraw.box(self.screen, self.get_toolbar_rect(), Colors.TOOL_BKG)
        TextRenderer.draw_text(self.roboto20, Colors.LIGHT_TEXT, self.screen, self.get_toolbar_rect(), toolbar_text)
        # If game win
        if self.board.is_win():
            self.screen.blit(self.game_over, self.get_board_rect())
            TextRenderer.draw_text(self.roboto72, Colors.DARK_TEXT, self.screen, self.get_board_rect(), "You Win!")
        # If game over draw
        if self.board.no_moves():
            self.screen.blit(self.game_over, self.get_board_rect())
            TextRenderer.draw_text(self.roboto72, Colors.DARK_TEXT, self.screen, self.get_board_rect(), "Game Over!")
        # End Draw
        self.sync()
    
    MARGIN = 16
    PIECE = (SIZE - MARGIN * 5) / 4
    def draw_piece(self, value, xi, yi):
        x = self.MARGIN * (xi + 1) + self.PIECE * xi
        y = self.MARGIN * (yi + 1) + self.PIECE * yi
        rectColor = Colors.BY_VAL[value]

        rect = pygame.Rect(x, y, self.PIECE, self.PIECE)
        gfxdraw.box(self.screen, rect, rectColor)
        if value != 0:
            textColor = Colors.DARK_TEXT
            font = self.roboto72
            if value > 4:
                textColor = Colors.LIGHT_TEXT
            if value >= 128:
                font = self.roboto64
            if value >= 1024:
                font = self.roboto48
            TextRenderer.draw_text(font, textColor, self.screen, rect, str(value))



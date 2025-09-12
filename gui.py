import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from Scene import SceneManager
from LobbyScene import LobbyScene

def run_gui(q_table):
    pygame.display.set_caption("Learn2Slither - Lobby")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    mgr = SceneManager(LobbyScene(q_table))
    mgr.run(screen, fps=60)
import pygame

class Scene:
    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, screen): pass

class SceneManager:
    def __init__(self, initial_scene):
        self.current = initial_scene

    def run(self, screen, fps=60):
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.tick(fps) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.current.handle_event(event)
            self.current.update(dt)
            screen.fill((25, 25, 30))
            self.current.draw(screen)
            pygame.display.flip()
        pygame.display.quit()
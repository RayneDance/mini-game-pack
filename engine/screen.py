class Screen:
    def __init__(self, pygame, width=800, height=600):
        self.width = width
        self.height = height
        self.pygame = pygame
        self.screen = self.pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Default")

    def draw(self):
        self.pygame.display.flip()
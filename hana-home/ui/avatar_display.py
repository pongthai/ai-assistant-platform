import pygame

class AvatarDisplay:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        self.image = pygame.image.load("avatar.png")

    def display(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.screen.blit(self.image, (0, 0))
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

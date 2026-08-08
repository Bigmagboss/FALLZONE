import pygame



VERSION = "0.0001"


pygame.init()


screen = pygame.display.set_mode((900, 500))
pygame.display.set_caption(f"Gridfall v{VERSION}")

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
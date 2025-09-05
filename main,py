import pygame
import random


pygame.init()


ancho, alto = 600, 400
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("♻️ Green Hero")


BLANCO = (255, 255, 255)
VERDE = (0, 200, 0)
ROJO = (200, 0, 0)


jugador = pygame.Rect(280, 350, 40, 40)


basura = pygame.Rect(random.randint(0, ancho-20), 0, 20, 20)

velocidad = 5
puntos = 0
reloj = pygame.time.Clock()

ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and jugador.x > 0:
        jugador.x -= 7
    if teclas[pygame.K_RIGHT] and jugador.x < ancho - 40:
        jugador.x += 7

    basura.y += velocidad
    if basura.y > alto:
        basura.y = 0
        basura.x = random.randint(0, ancho-20)

    if jugador.colliderect(basura):
        puntos += 1
        basura.y = 0
        basura.x = random.randint(0, ancho-20)

    pantalla.fill(BLANCO)
    pygame.draw.rect(pantalla, VERDE, jugador)
    pygame.draw.rect(pantalla, ROJO, basura)

    fuente = pygame.font.SysFont(None, 30)
    texto = fuente.render(f"Puntos: {puntos}", True, (0, 0, 0))
    pantalla.blit(texto, (10, 10))

    pygame.display.flip()
    reloj.tick(30)

pygame.quit()

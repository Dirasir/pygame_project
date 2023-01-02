import pygame
import sys
import os


class Player:
    def __init__(self):
        self.hp = 0
        self.lvl = 1
        self.kills = 100


FPS = 30
pygame.init()
size = width, height = 550, 550
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


class Interface:
    def load_image(self, name, colorkey=None):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image

    def terminate(self):
        pygame.quit()
        sys.exit()

    def start_screen(self):
        intro_text = ["Управление", "",
                      "по стрелочкам",
                      "наступать на ящики нельзя"]

        fon = pygame.transform.scale(self.load_image('fon.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        pygame.draw.rect(screen, "green", (175, 360, 200, 100))
        screen.blit(font.render("PLAY", 1, pygame.Color('black')), (250, 400))
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    clickX = event.pos[0]
                    clickY = event.pos[1]
                    if (374 > clickX > 176) and (460 > clickY > 361):
                        return
            pygame.display.flip()
            clock.tick(FPS)

    def end_screen(self, lvl, kills):
        f = [lvl, kills]
        intro_text = ["Твой уровень:", "",
                      "kills_count:"]
        fon = pygame.transform.scale(self.load_image('fonDEAD.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 60)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        text = font.render(str(Player().lvl), True, pygame.Color("red"))
        screen.blit(text, (300, 60))
        text = font.render(str(Player().kills), True, pygame.Color("red"))
        screen.blit(text, (250, 165))

    def settings(self):
        pass

if __name__ == '__main__':
    Interface().start_screen()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if Player().hp == 0:
                Interface().end_screen(Player().lvl, Player().kills)
        clock.tick(FPS)
        pygame.display.flip()

    pygame.quit()
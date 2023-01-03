import pygame
import sys
import os
import main

FPS = 30
pygame.init()
clock = pygame.time.Clock()

class Interface:
    def __init__(self, size, screen):
        self.size = size
        self.screen = screen
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

        fon = pygame.transform.scale(self.load_image('fon.jpg'), (self.size))
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        button_X = self.size[1] // 3
        pygame.draw.rect(self.screen, "green", (button_X, button_X * 2, 200, 100))
        self.screen.blit(font.render("PLAY", 1, pygame.Color('black')), (button_X+75, button_X * 2 + 40))
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    clickX = event.pos[0]
                    clickY = event.pos[1]
                    if ((button_X+200) > clickX > button_X) and ((button_X * 2) + 200 > clickY > button_X * 2):
                        return
            pygame.display.flip()
            clock.tick(FPS)

    def end_screen(self, lvl, kills):
        f = [lvl, kills]
        intro_text = ["Твой уровень:", "",
                      "kills_count:"]
        fon = pygame.transform.scale(self.load_image('fonDEAD.jpg'), (self.size))
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 60)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)
        text = font.render(str(lvl), True, pygame.Color("red"))
        self.screen.blit(text, (300, 60))
        text = font.render(str(kills), True, pygame.Color("red"))
        self.screen.blit(text, (250, 165))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    Interface(main.size, main.screen).start_screen()
            pygame.display.flip()
            clock.tick(FPS)
    def settings(self):
        pass

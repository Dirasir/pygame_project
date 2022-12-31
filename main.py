import pygame
import sys
import os
import random
import math

sss = "map.txt"


# класс счётчика фпс
class FPSCounter:
    def __init__(self, surface, font, clock, color, pos):
        self.surface = surface
        self.font = font
        self.clock = clock
        self.pos = pos
        self.color = color

        self.fps_text = self.font.render(str(int(self.clock.get_fps())) + "FPS", False, self.color)
        self.fps_text_rect = self.fps_text.get_rect(center=(self.pos[0], self.pos[1]))

    def render(self):
        self.surface.blit(self.fps_text, self.fps_text_rect)

    def update(self):
        self.fps_text = self.font.render(str(int(self.clock.get_fps())) + "FPS", False, self.color)
        self.fps_text_rect = self.fps_text.get_rect(center=(self.pos[0], self.pos[1]))


FPS = 30
pygame.init()
size = width, height = 550, 550
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


# функиця загрузки изображения при вводе 1 удаляется фон
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == 1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# функция выключения игры
def terminate():
    pygame.quit()
    sys.exit()


# подаём на ввод файл со строками
# на выходе получаем список из строчек
def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    if not os.path.isfile(filename):
        print(f"Файл с изображением '{filename}' не найден")
        sys.exit()
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# начальный экран
def start_screen():
    intro_text = ["Управление", "",
                  "по стрелочкам",
                  "наступать на ящики нельзя"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
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
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


# список с изображениями ландшафта
tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass4.png')
}
crystal_images = {
    "blue": load_image("blue_kristal.png", 1)
}
player_image = load_image('mar.png')

tile_width = tile_height = 50

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
enemy_weapon_group = pygame.sprite.Group()
player_weapon_group = pygame.sprite.Group()
crystal_group = pygame.sprite.Group()


# создания уровня на вход подаёться список созданный в функии load_level()
def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
    # вернем игрока, а также размер поля в клетках
    return x, y


# класс для каждой клетки ландшафта
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.image = pygame.transform.scale(self.image, (tile_width, tile_height))
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        if tile_type == "wall":
            self.add(box_group)


class Crystal(pygame.sprite.Sprite):
    def __init__(self, crystal_type, pos_x, pos_y):
        super().__init__(crystal_group, all_sprites)
        self.image = crystal_images[crystal_type]
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.price = 0
        if crystal_type == "blue":
            self.price = 10


# класс ножа игрока
class Knife(pygame.sprite.Sprite):
    image = load_image("knife.png", 1)

    def __init__(self, pos):
        super().__init__(player_weapon_group, all_sprites)
        self.image = Knife.image
        self.image = pygame.transform.scale(self.image, (40, 10))

        self.rect = self.image.get_rect().move(player.rect.x, player.rect.y)

        self.damage = 10

        self.move_speed = 4
        self.x = self.rect.x
        self.y = self.rect.y
        self.t = ((abs(self.rect.x - pos[0]) ** 2 + abs(
            self.rect.y - pos[1]) ** 2) ** 0.5 - 12) / self.move_speed
        if self.t == 0:
            self.t = 0.000001
        self.move_x = -(self.rect.x - pos[0]) / self.t
        self.move_y = -(self.rect.y - pos[1]) / self.t
        self.fps = 0
        self.move = True

        self.rotate = -(math.degrees(math.atan(self.move_y / self.move_x)))
        if self.move_x < 0:
            self.rotate += 180

        self.image = pygame.transform.rotate(self.image, self.rotate)
        self.rect = self.image.get_rect().move(player.rect.x, player.rect.y)

    def update(self):
        self.fps += 1
        # по прошествию 10 секунд объект удалается
        if self.fps == FPS * 10:
            self.kill()
        if self.move:
            self.x += self.move_x
            self.y += self.move_y
            # проверка сталкивается ли объект со стеной или врагом
            if pygame.sprite.spritecollideany(self, box_group) or pygame.sprite.spritecollideany(self, enemy_group):
                self.move = False
                self.x += self.move_x * 2
                self.y += self.move_y * 2
        self.rect.x = self.x
        self.rect.y = self.y


# класс снарядов врагов
class Poo(pygame.sprite.Sprite):
    image = load_image("poo.png", 1)

    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_weapon_group, all_sprites)
        self.image = Poo.image
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect().move(pos_x, pos_y)

        self.move_speed = 4
        self.x = self.rect.x
        self.y = self.rect.y
        self.t = ((abs(self.rect.x - player.rect.x) ** 2 + abs(
            self.rect.y - player.rect.y) ** 2) ** 0.5 - 12) / self.move_speed
        if self.t == 0:
            self.t = 0.000001
        self.move_x = -(self.rect.x - player.rect.x) / self.t
        self.move_y = -(self.rect.y - player.rect.y) / self.t

        self.damage = 10

        self.fps = 0
        self.move = True

    def update(self):
        self.fps += 1
        # по прошествию 5 секунд объект удалается
        if self.fps == FPS * 5:
            self.kill()
        if self.move:
            self.x += self.move_x
            self.y += self.move_y
            # проверка сталкиваеся ли объект со стеной или игроком
            if pygame.sprite.spritecollideany(self, box_group) or pygame.sprite.spritecollideany(self, player_group):
                self.move = False
                self.x += self.move_x * 2
                self.y += self.move_y * 2
        self.rect.x = self.x
        self.rect.y = self.y


# класс врага2
class Enemy1(pygame.sprite.Sprite):
    image = load_image("kobakov.png", 1)

    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = Enemy1.image
        self.image = pygame.transform.scale(self.image, (45, 45))
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.move_speed = 2
        self.x = self.rect.x
        self.y = self.rect.y
        self.hp = 10

    def update(self):
        self.t = ((abs(self.rect.x - player.rect.x) ** 2 + abs(
            self.rect.y - player.rect.y) ** 2) ** 0.5 - 12) / self.move_speed
        if self.t == 0:
            self.t = 0.000001
        self.move_x = (self.rect.x - player.rect.x) / self.t
        self.move_y = (self.rect.y - player.rect.y) / self.t

        self.x += -self.move_x
        self.rect.x = self.x

        if pygame.sprite.spritecollideany(self, box_group) or len(
                pygame.sprite.spritecollide(self, enemy_group, False)) > 1:
            if self.move_x > 0:
                self.x -= -(self.move_x + 1)
            if self.move_x < 0:
                self.x -= -(self.move_x - 1)
        self.y += -self.move_y
        self.rect.y = self.y
        if pygame.sprite.spritecollideany(self, box_group) or len(
                pygame.sprite.spritecollide(self, enemy_group, False)) > 1:
            self.y -= -(self.move_y)

        self.rect.x = self.x
        self.rect.y = self.y

        st = pygame.sprite.spritecollideany(self, player_weapon_group)
        if st:
            self.hp -= st.damage
            st.kill()

        if self.hp <= 0:
            if not random.randint(0, 3):
                Crystal("blue",self.x,self.y)
            self.kill()


# класс врага2
class Enemy2(pygame.sprite.Sprite):
    image = load_image("creature.png", 1)

    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = Enemy2.image
        self.image = pygame.transform.scale(self.image, (45, 45))
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.move_speed = 1
        self.x = self.rect.x
        self.y = self.rect.y
        self.hp = 20

    def update(self):

        self.t = ((abs(self.rect.x - player.rect.x) ** 2 + abs(
            self.rect.y - player.rect.y) ** 2) ** 0.5 - 12) / self.move_speed
        if self.t == 0:
            self.t = 0.000001
        self.move_x = (self.rect.x - player.rect.x) / self.t
        self.move_y = (self.rect.y - player.rect.y) / self.t

        self.x += -self.move_x
        self.rect.x = self.x

        if pygame.sprite.spritecollideany(self, box_group) or len(
                pygame.sprite.spritecollide(self, enemy_group, False)) > 1:
            if self.move_x > 0:
                self.x -= -(self.move_x + 1)
            if self.move_x < 0:
                self.x -= -(self.move_x - 1)
        self.y += -self.move_y
        self.rect.y = self.y
        if pygame.sprite.spritecollideany(self, box_group) or len(
                pygame.sprite.spritecollide(self, enemy_group, False)) > 1:
            self.y -= -(self.move_y)

        self.rect.x = self.x
        self.rect.y = self.y

        st = pygame.sprite.spritecollideany(self, player_weapon_group)
        if st:
            self.hp -= st.damage
            st.kill()

        if (abs(self.rect.x - player.rect.x) ** 2 + abs(self.rect.y - player.rect.y) ** 2) ** 0.5 < 430:
            if not random.randint(0, 600):
                Poo(self.rect.x + 7, self.rect.y + 7)

        if self.hp <= 0:
            if not random.randint(0, 4):
                Crystal("blue",self.x,self.y)
            self.kill()


# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.hp = 100
        self.weapon_kd = 0
        self.exp = 0

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
        if pygame.sprite.spritecollideany(self, box_group) or pygame.sprite.spritecollideany(self, enemy_group):
            self.rect.x -= x
            self.rect.y -= y

    def shot(self, pos):
        if self.weapon_kd == FPS * 2:
            Knife(pos)
            self.weapon_kd = 0

    def update(self):
        st = pygame.sprite.spritecollideany(self, enemy_weapon_group)
        if st:
            self.hp -= st.damage
            st.kill()

        st = pygame.sprite.spritecollideany(self, crystal_group)
        if st:
            self.exp += st.price
            st.kill()

        if self.weapon_kd < FPS * 2:
            self.weapon_kd += 1
        pygame.draw.rect(screen, "grey", (self.rect.x - 13, self.rect.y + 50, 50, 10))
        pygame.draw.rect(screen, "red", (self.rect.x - 13, self.rect.y + 50, self.hp // 2, 10))

        pygame.draw.rect(screen, "grey", (self.rect.x - 13, self.rect.y + 50 + 20, 50, 10))
        pygame.draw.rect(screen, "yellow",
                         (self.rect.x - 13, self.rect.y + 50 + 20, 50 * (self.weapon_kd / (FPS * 2)), 10))

        pygame.draw.rect(screen, "grey", (5, height - 30, width - 10, 25))
        pygame.draw.rect(screen, "blue", (5, height - 30, (self.exp / 100) * (width - 10), 25))
        if self.hp <= 0:
            self.kill()


# класс камеры
class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.x = 0
        self.y = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if obj in enemy_group:
            obj.x += self.dx
            obj.y += self.dy
        elif obj in enemy_weapon_group:
            obj.x += self.dx
            obj.y += self.dy
        elif obj in player_weapon_group:
            obj.x += self.dx
            obj.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        self.y -= self.dy
        self.x -= self.dx


if __name__ == '__main__':
    start_screen()
    level_x, level_y = generate_level(load_level(sss))
    camera = Camera()
    for i in range(1):
        Enemy1(random.randint(6, 25) * 50, random.randint(6, 15) * 50)
        Enemy2(random.randint(6, 25) * 50, random.randint(6, 15) * 50)
    player = Player(16 * 50, 10 * 50)
    font = pygame.font.Font(None, 36)
    fps_counter = FPSCounter(screen, font, clock, "green", (40, 10))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shot(event.pos)
        # перемещение героя
        spisok = list(pygame.key.get_pressed())
        spisok[511] = True
        if spisok.index(True) == 7:
            player.move(2, 0)
            spisok[7] = False
        if spisok.index(True) == 4:
            player.move(-2, 0)
            spisok[4] = False
        if spisok.index(True) == 22:
            player.move(0, 2)
            spisok[22] = False
        if spisok.index(True) == 26:
            player.move(0, -2)
            spisok[26] = False
        # ----------------
        screen.fill("black")

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        # обновление всех груп в нужном порядке. Тоже самое что и all_sprites.update()
        tiles_group.update()
        box_group.update()
        enemy_group.update()
        enemy_weapon_group.update()
        player_weapon_group.update()
        crystal_group.update()
        # ---------------------------------------------
        all_sprites.draw(screen)
        player.update()

        # счётчик фпс
        fps_counter.render()
        fps_counter.update()
        # -------
        clock.tick(FPS)
        pygame.display.flip()

    pygame.quit()

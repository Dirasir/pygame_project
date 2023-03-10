import pygame
import sys
import os
import random
import math
import time
import notmain

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
size = width, height = 950, 800
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
kills_count = 0

#способность увелечение ха персонажа
class Up_strange:
    def __init__(self):
        #super().__init__(ability_sprites, all_sprites)
        self.image = "blue_crystal.png"
        self.description = "Увеличение хп персонажа на 10"
    def use(self):
        player.hp += 20

#способность увелечение скорости ходьбы персонажа
class Up_movespeed:
    def __init__(self):
        #super().__init__(ability_sprites, all_sprites)
        self.image = "Run1.png"
        self.description = "Увеличение скорости персонажа на 1"
    def use(self):
        player.move_speed += 1

#способность увелечение урона персонажа
class Up_damage:
    def __init__(self):
        #super().__init__(ability_sprites, all_sprites)
        self.image = "red_crystal.png"
        self.description = "Увеличение урона персонажа на 5"
    def use(self):
        player.bonus_damage += 5

# функиця загрузки изображения при вводе 1 удаляется фон
def load_image(name, colorkey=None):
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

# список с изображениями ландшафта
tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass4.png'),
    'deathzone': load_image('grass4.png')
}
crystal_images = {
    "blue": load_image("blue_crystal.png"),
    "gray": load_image("gray_crystal.png"),
    "green": load_image("green_crystal.png"),
    "purple": load_image("purple_crystal.png"),
    "light_blue": load_image("light_blue_crystal.png"),
    "red": load_image("red_crystal.png"),
    "yellow": load_image("yellow_crystal.png")
}


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
deathzone_group = pygame.sprite.Group()

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
            elif level[y][x] == ',':
                Tile('deathzone', x, y)
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
        if tile_type == "deathzone":
            self.add(deathzone_group)


class Crystal(pygame.sprite.Sprite):
    def __init__(self, crystal_type, pos_x, pos_y):
        super().__init__(crystal_group, all_sprites)
        self.image = crystal_images[crystal_type]
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.price = 0
        if crystal_type == "light_blue":
            self.price = 10
        if crystal_type == "blue":
            self.price = 20
        if crystal_type == "purple":
            self.price = 50


# класс ножа игрока
class Knife(pygame.sprite.Sprite):
    image = load_image("Sprite_Weapon.png")

    def __init__(self, pos, bonus_dmg):
        super().__init__(player_weapon_group, all_sprites)
        self.image = Knife.image
        self.image = pygame.transform.scale(self.image, (30, 30))

        self.rect = self.image.get_rect().move(player.rect.x, player.rect.y)

        self.damage = 10 + bonus_dmg

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

        self.rotate = -(math.degrees(math.atan(self.move_y / self.move_x))) + 0.000000000000001
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
    image = load_image("fist_slime.png")

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

class Laso(pygame.sprite.Sprite):
    image = load_image("laso.png", -1)

    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_weapon_group, all_sprites)
        self.image = Laso.image
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

        self.damage = 0

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
    image = load_image("kobakov.png", -1)
    def __init__(self, sheet, columns, rows, x, y, time):
        super().__init__(enemy_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect().move(x, y)
        self.move_speed = 2
        self.x = self.rect.x
        self.y = self.rect.y
        self.hp = 10
        self.damage = 10
        self.damage_kd = 0
        self.ind = 0
        self.time = time

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.ind += 1
        if self.damage_kd < 30:
            self.damage_kd += 1
        self.t = ((abs(self.rect.x - player.rect.x) ** 2 + abs(
            self.rect.y - player.rect.y) ** 2) ** 0.5 - 12) / self.move_speed
        if self.t == 0:
            self.t = 0.000001
        if self.ind % 20 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.move_x = (self.rect.x - player.rect.x) / self.t
        self.move_y = (self.rect.y - player.rect.y) / self.t

        self.x += -self.move_x
        self.rect.x = self.x

        if pygame.sprite.spritecollideany(self, player_group) and self.damage_kd == 30:
            player.hp -= self.damage
            self.damage_kd = 0

        if pygame.sprite.spritecollideany(self, box_group) or len(
                pygame.sprite.spritecollide(self, enemy_group, False)) > 1 or pygame.sprite.spritecollideany(self,
                                                                                                             player_group):
            if self.move_x > 0:
                self.x -= -(self.move_x + 1)
            if self.move_x < 0:
                self.x -= -(self.move_x - 1)
        self.y += -self.move_y
        self.rect.y = self.y

        if pygame.sprite.spritecollideany(self, player_group) and self.damage_kd == 30:
            player.hp -= self.damage
            self.damage_kd = 0

        if pygame.sprite.spritecollideany(self, box_group) or len(
                pygame.sprite.spritecollide(self, enemy_group, False)) > 1 or pygame.sprite.spritecollideany(self,
                                                                                                             player_group):
            self.y -= -(self.move_y)

        self.rect.x = self.x
        self.rect.y = self.y

        if pygame.sprite.spritecollideany(self, deathzone_group):
            self.kill()
        st = pygame.sprite.spritecollideany(self, player_weapon_group)
        if st:
            self.hp -= st.damage
            st.kill()

        if self.hp <= 0:
            if not random.randint(0, 3):
                Crystal("light_blue", self.x, self.y)
            self.kill()
            player.kills_count += 1

        if int(self.time) % 60 == 0:
            self.hp += 5
            self.damage += 5

# класс врага2
class Enemy2(pygame.sprite.Sprite):
    image = load_image("creature.png")
    def __init__(self,sheet, columns, rows, x, y, time):
        super().__init__(enemy_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = pygame.transform.scale(self.image, (50, 75))
        self.rect = self.image.get_rect().move(x, y)
        self.move_speed = 1
        self.x = self.rect.x
        self.y = self.rect.y
        self.hp = 20
        self.damage = 20
        self.damage_kd = 0
        self.ind = 0
        self.flag1 = True
        self.time = time
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.ind += 1
        if self.ind % 1 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.flag1:
                self.image = pygame.transform.flip(self.image, True, False)
            if self.rect.x - player.rect.x < 0:
                self.flag1 = True
            elif self.rect.x - player.rect.x > 0:
                self.flag1 = False
        if self.damage_kd < 30:
            self.damage_kd += 1
        self.t = ((abs(self.rect.x - player.rect.x) ** 2 + abs(
            self.rect.y - player.rect.y) ** 2) ** 0.5 - 12) / self.move_speed
        if self.t == 0:
            self.t = 0.000001

        self.move_x = (self.rect.x - player.rect.x) / self.t
        self.move_y = (self.rect.y - player.rect.y) / self.t

        self.x += -self.move_x
        self.rect.x = self.x
        if pygame.sprite.spritecollideany(self, player_group) and self.damage_kd == 30:
            player.hp -= self.damage
            self.damage_kd = 0

        if pygame.sprite.spritecollideany(self, box_group) or len(
                pygame.sprite.spritecollide(self, enemy_group, False)) > 1 or pygame.sprite.spritecollideany(self,
                                                                                                             player_group):
            if self.move_x > 0:
                self.x -= -(self.move_x + 1)
            if self.move_x < 0:
                self.x -= -(self.move_x - 1)

        if pygame.sprite.spritecollideany(self, player_group) and self.damage_kd == 30:
            player.hp -= self.damage
            self.damage_kd = 0
        self.y += -self.move_y
        self.rect.y = self.y
        if pygame.sprite.spritecollideany(self, box_group) or len(
                pygame.sprite.spritecollide(self, enemy_group, False)) > 1 or pygame.sprite.spritecollideany(self,
                                                                                                             player_group):
            self.y -= -(self.move_y)

        self.rect.x = self.x
        self.rect.y = self.y

        st = pygame.sprite.spritecollideany(self, player_weapon_group)
        if st:
            self.hp -= st.damage
            st.kill()

        if (abs(self.rect.x - player.rect.x) ** 2 + abs(self.rect.y - player.rect.y) ** 2) ** 0.5 < 430:
            if not random.randint(0, 450):
                Poo(self.rect.x + 7, self.rect.y + 7)

        if self.hp <= 0:
            if not random.randint(0, 4):
                Crystal("blue", self.x, self.y)
            self.kill()
            player.kills_count += 1

        if pygame.sprite.spritecollideany(self, deathzone_group):
            self.kill()

        if int(self.time) % 60 == 0:
            self.hp += 10
            self.damage += 10

class Enemy3(pygame.sprite.Sprite):
    image = load_image("hokker.png", -1)
    def __init__(self,sheet, columns, rows, x, y, time):
        super().__init__(enemy_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect().move(x, y)
        self.move_speed = 0.5
        self.x = self.rect.x
        self.y = self.rect.y
        self.hp = 30
        self.damage = 30
        self.damage_kd = 0
        self.ind = 0
        self.flag1 = True
        self.time = time
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.ind += 1
        if self.ind % 4 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.flag1:
                self.image = pygame.transform.flip(self.image, True, False)
            if self.rect.x - player.rect.x < 0:
                self.flag1 = True
            elif self.rect.x - player.rect.x > 0:
                self.flag1 = False
        if self.damage_kd < 30:
            self.damage_kd += 1
        self.t = ((abs(self.rect.x - player.rect.x) ** 2 + abs(
            self.rect.y - player.rect.y) ** 2) ** 0.5 - 12) / self.move_speed
        if self.t == 0:
            self.t = 0.000001
        self.move_x = (self.rect.x - player.rect.x) / self.t
        self.move_y = (self.rect.y - player.rect.y) / self.t

        self.x += -self.move_x
        self.rect.x = self.x
        if pygame.sprite.spritecollideany(self, player_group) and self.damage_kd == 30:
            player.hp -= self.damage
            self.damage_kd = 0

        if pygame.sprite.spritecollideany(self, box_group) or len(
                pygame.sprite.spritecollide(self, enemy_group, False)) > 1 or pygame.sprite.spritecollideany(self,
                                                                                                             player_group):
            if self.move_x > 0:
                self.x -= -(self.move_x + 1)
            if self.move_x < 0:
                self.x -= -(self.move_x - 1)

        if pygame.sprite.spritecollideany(self, player_group) and self.damage_kd == 30:
            player.hp -= self.damage
            self.damage_kd = 0
        self.y += -self.move_y
        self.rect.y = self.y
        if pygame.sprite.spritecollideany(self, box_group) or len(
                pygame.sprite.spritecollide(self, enemy_group, False)) > 1 or pygame.sprite.spritecollideany(self,
                                                                                                             player_group):
            self.y -= -(self.move_y)

        self.rect.x = self.x
        self.rect.y = self.y

        st = pygame.sprite.spritecollideany(self, player_weapon_group)
        if st:
            self.hp -= st.damage
            st.kill()

        if (abs(self.rect.x - player.rect.x) ** 2 + abs(self.rect.y - player.rect.y) ** 2) ** 0.5 < 430:
            if not random.randint(0, 600):
                Laso(self.rect.x + 7, self.rect.y + 7)

        if self.hp <= 0:
            if not random.randint(0, 4):
                Crystal("purple", self.x, self.y)
            self.kill()
            player.kills_count += 1

        if pygame.sprite.spritecollideany(self, deathzone_group):
            self.kill()

        if int(self.time) % 60 == 0:
            self.hp += 5
            self.damage += 5


spisok_level = [i for i in range(0, 1500, 50)]

# класс игрока
class Player(pygame.sprite.Sprite):
    image0 = load_image("Main_Character_Standing.png")

    def __init__(self,sheet, columns, rows, x, y):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (75, 75))
        self.rect = self.image.get_rect().move(x, y)
        self.hp = 100
        self.weapon_kd = 0
        self.level_kd = 0
        self.exp = 0
        self.level = 1
        self.kills_count = 0
        self.flag = True
        self.flag1 = False
        self.ind = 0
        self.move_speed = 2
        self.bonus_damage = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def move(self, x, y):
        if self.ind % 4 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.flag1:
                self.image = pygame.transform.flip(self.image, True, False)
            if x > 0:
                self.flag1 = True
            elif x < 0:
                self.flag1 = False
        self.image = pygame.transform.scale(self.image, (75, 75))
        if self.flag:
            self.rect.x += x
            self.rect.y += y
            if pygame.sprite.spritecollideany(self, box_group):
                self.rect.x -= x
                self.rect.y -= y

    def shot(self, pos):
        if self.weapon_kd >= FPS * 2 - self.level_kd:
            Knife(pos, self.bonus_damage)
            self.weapon_kd = 0

    def update(self):
        self.ind += 1
        self.flag = True
        st1 = pygame.sprite.spritecollideany(self, enemy_weapon_group)
        if st1:
            if st1.damage == 0:
                self.flag = False
            else:
                self.hp -= st1.damage
                st1.kill()


        st3 = pygame.sprite.spritecollideany(self, crystal_group)
        if st3:
            self.exp += st3.price
            st3.kill()

        if self.weapon_kd< FPS * 2 - self.level_kd:
            self.weapon_kd += 1
        pygame.draw.rect(screen, "grey", (self.rect.x, self.rect.y + 85, 70, 10))
        pygame.draw.rect(screen, "red", (self.rect.x, self.rect.y + 85, (self.hp / 100) * 70, 10))

        pygame.draw.rect(screen, "grey", (self.rect.x, self.rect.y + 85 + 20, 70, 10))
        pygame.draw.rect(screen, "yellow", (self.rect.x, self.rect.y + 85 + 20, 70 * (self.weapon_kd / (FPS * 2 - self.level_kd + 0.00000000000000001)), 10))

        if self.exp >= spisok_level[self.level]:
            self.level += 1
            self.exp -= spisok_level[self.level - 1]
            notmain.Interface(size, screen).ability_win(Up_strange, Up_movespeed,
                                                        Up_damage)

        pygame.draw.rect(screen, "grey", (65, height - 55, width - 70, 35))
        pygame.draw.rect(screen, "blue", (65, height - 55, (self.exp / spisok_level[self.level]) * (width - 70), 35))

        if self.hp <= 0:
            pygame.mixer.music.load("data/roblox-death-sound-effect.mp3")
            pygame.mixer.music.play(0)
            notmain.Interface(size, screen).end_screen(player.level, player.kills_count)
            self.kill()


        if self.hp > 100:
            self.hp = 100


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
    notmain.Interface(size, screen).start_screen()
    level_x, level_y = generate_level(load_level(sss))
    pygame.mixer.music.load("data/zvukiprirodi.mp3.mp3")
    pygame.mixer.music.play(-1)
    camera = Camera()
    player = Player(load_image("runn.png"), 3, 1, 16 * 50,  10 * 50)
    font = pygame.font.Font(None, 36)
    fps_counter = FPSCounter(screen, font, clock, "green", (40, 10))
    start_time = time.ctime(time.time())[14:19]

    start_time = int(start_time[:2]) * 60 + int(start_time[3:])
    fpsfps = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.shot(event.pos)
            if event.type == pygame.KEYDOWN:
                if list(pygame.key.get_pressed())[41] == True:
                    notmain.Interface(size, screen).start_screen()
                    pygame.mixer.music.pause()
                pygame.mixer.music.unpause()
        fpsfps += 1
        #появление врагов
        if fpsfps == FPS * 5:
            Enemy1(load_image("slime1 _run.png"), 2, 1,
                   400 + random.randint(400, 600) * random.randrange(-1, 2, 2),
                   400 + random.randint(400, 600) * random.randrange(-1, 2, 2), last_time)
            Enemy2(load_image("eliteslime_run.png"), 3, 1,
                   400 + random.randint(400, 600) * random.randrange(-1, 2, 2),
                   400 + random.randint(400, 600) * random.randrange(-1, 2, 2), last_time)
            Enemy3(load_image("cowslime_run.png"), 2, 1,
                   400 + random.randint(400, 600) * random.randrange(-1, 2, 2),
                   400 + random.randint(400, 600) * random.randrange(-1, 2, 2), last_time)
            fpsfps = 0
        # перемещение героя
        spisok = list(pygame.key.get_pressed())
        spisok[511] = True
        if spisok.index(True) == 7:
            player.move(player.move_speed, 0)
            spisok[7] = False
        if spisok.index(True) == 4:
            player.move(-player.move_speed, 0)
            spisok[4] = False
        if spisok.index(True) == 22:
            player.move(0, player.move_speed)
            spisok[22] = False
        if spisok.index(True) == 26:
            player.move(0, -player.move_speed)
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
        font = pygame.font.Font(None, 110)
        screen.blit(font.render(str(player.level), 1, pygame.Color('green')), (10, 730))

        # создание таймера
        last_time = time.ctime(time.time())[14:19]
        last_time = int(last_time[:2]) * 60 + int(last_time[3:]) - start_time
        time_first = str(last_time // 60) + ":" + str(last_time % 60)

        #оповещение о повышении сложности
        if last_time % 60 == 0:
            if last_time % 60 != 4:
                font = pygame.font.Font(None, 35)
                text = font.render("Увеличение сложности", True, pygame.Color("red"))
                screen.blit(text, (200, 100))

        font = pygame.font.Font(None, 110)
        screen.blit(font.render(time_first, 1, pygame.Color('black')), (340, 10))

        # счётчик фпс
        fps_counter.render()
        fps_counter.update()
        # -------
        clock.tick(FPS)
        pygame.display.flip()

    pygame.quit()

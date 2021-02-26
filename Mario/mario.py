import pygame
import sys
import os

pygame.init()
size = width, height = [500, 500]
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
screen.fill(pygame.Color('black'))


FPS = 50


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
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


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():

    fon = load_image('fon.jpg')
    screen.blit(pygame.transform.scale(fon, (width, height)), (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)



level_map = None


def load_level(filename):
    global level_map
    print(filename)
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    level_map = list(map(lambda x: x.ljust(max_width, '.'), level_map))
    return level_map


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.lastrectx = None

    def agree(self, n):
        if n == 'L' and 0 <= self.rect.move(-tile_width, 0).left <= width \
                and level_map[self.rect.move(-tile_width, 0).top // 50][self.rect.move(-tile_width, 0).left // 50] \
                in ('.', '@'):
            return True
        elif n == 'R' and 0 <= self.rect.move(tile_width, 0).left <= width \
                and level_map[self.rect.move(tile_width, 0).top // 50][self.rect.move(tile_width, 0).left // 50] \
                in ('.', '@'):
            return True
        elif n == 'U' and 0 <= self.rect.move(0, -tile_height).left <= height\
                and level_map[self.rect.move(0, -tile_height).top // 50][self.rect.move(0, -tile_height).left // 50]\
                in ('.', '@'):
            return True
        elif n == 'D' and 0 <= self.rect.move(0, tile_height).left <= height\
                and level_map[self.rect.move(0, tile_height).top // 50][self.rect.move(0, tile_height).left // 50]\
                in ('.', '@'):
            return True
        return False

    def update(self, direction=None):
        if direction:
            if direction == 'L' and 0 <= self.rect.move(-tile_width, 0).left <= width\
                    and level_map[self.rect.move(-tile_width, 0).top // 50][self.rect.move(-tile_width, 0).left // 50]\
                    in ('.', '@'):
                self.lastrectx = self.rect.topleft[1]
                self.rect = self.rect.move(-tile_width, 0)
            elif direction == 'R' and 0 <= self.rect.move(tile_width, 0).left <= width\
                    and level_map[self.rect.move(tile_width, 0).top // 50][self.rect.move(tile_width, 0).left // 50]\
                    in ('.', '@'):
                self.lastrectx = self.rect.topleft[1]
                self.rect = self.rect.move(tile_width, 0)
            elif direction == 'U' and 0 <= self.rect.move(0, -tile_height).left <= height\
                    and level_map[self.rect.move(0, -tile_height).top // 50][self.rect.move(0, -tile_height).left // 50]\
                    in ('.', '@'):
                self.rect = self.rect.move(0, -tile_height)
            elif direction == 'D' and 0 <= self.rect.move(0, tile_height).left <= height\
                    and level_map[self.rect.move(0, tile_height).top // 50][self.rect.move(0, tile_height).left // 50]\
                    in ('.', '@'):
                self.rect = self.rect.move(0, tile_height)
        else:
            pass


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, ob):
        ob.rect.x += self.dx
        ob.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        n = 'H'
        if self.dx == 50:
            n = 'R'
        elif self.dx == -50:
            n = 'L'
        if self.dy == 50:
            n = 'D'
        elif self.dy == -50:
            n = 'U'
        if not target.agree(n):
            self.dy = 0
            self.dx = 0
     #   if target.agree((self.dx, self.dy)):
       #     print('ок')


file = input('Какой уровень? Выберите: 1, 2 или 3')
if file == '1':
    filename = 'map.txt'
elif file == '2':
    filename = 'map2.txt'
elif file == '3':
    filename = 'map3.txt'

player, level_x, level_y = generate_level(load_level(filename))
start_screen()
camera = Camera()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                player.update('L')
            if event.key == pygame.K_RIGHT:
                player.update('R')
            if event.key == pygame.K_UP:
                player.update('U')
            if event.key == pygame.K_DOWN:
                player.update('D')
    screen.fill(pygame.Color('black'))
    camera.update(player)
    for i in all_sprites:
        camera.apply(i)
    all_sprites.update()
    all_sprites.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(50)
pygame.quit()

"""Модуль реализует логику игры «Морской бой»"""

import random
from battle.botAI import BotAI
from enum import Enum


class Direction(Enum):
    """Направление корабля"""
    HORIZONTAL = 0
    VERTICAL = 1


class Cell:
    """Клетка игрового поля"""
    def __init__(self, x, y):
        """Инициализация клетки"""
        self.x = x
        self.y = y

    def __eq__(self, other):
        """Проверка равенства клеток"""
        return self.x == other.x and self.y == other.y

    def __str__(self):
        """Строковое представление клетки (x, y)"""
        return f'({self.x}, {self.y})'

    def __hash__(self):
        """Хеш объекта Клетки"""
        return hash((self.x, self.y))


class Ship:
    """Корабль игрового поля"""
    def __init__(self, cells):
        """Создание корабля из списка клеток"""
        self.cells = cells

    def __iter__(self):
        """Итератор списка клеток корабля"""
        return iter(self.cells)

    def __eq__(self, other):
        """Проверка равенства кораблей"""
        return self.cells == other.cells


class Player:
    """Игрок"""
    def __init__(self, name, field):
        """Создание игрока со своим полем"""
        self.name = name
        self.field = field


class Field:
    """Игровое поле"""
    def __init__(self, size_x, size_y, max_size_ship):
        """Создание поля (размер, макс. длина корабля,
        список живых клеток,
        список выстрелов,
        принадлежность точки кораблю
        """
        self.size_x = size_x
        self.size_y = size_y
        self.max_size_ship = max_size_ship
        self.cells = []  # список живых клеток
        self.shots = {}  # список выстрелов
        self.ships = []  # список кораблей
        self.dict_ships = {}  # Какая точка какому кораблю принадлежит

    def random_placement_ships(self):
        """Случайная расстановка кораблей"""
        c = 1  # Количество кораблей столькоклеточных
        for size_ship in range(self.max_size_ship, 0, -1):
            for _ in range(c):  # Количество кораблей
                while True:
                    x = random.randint(0, self.size_x - 1)
                    y = random.randint(0, self.size_y - 1)
                    cell = Cell(x, y)
                    if cell in self.cells:
                        continue
                    ans = self.generation_ship(
                        size_ship, cell, Direction.HORIZONTAL)
                    ans1 = self.generation_ship(
                        size_ship, cell, Direction.VERTICAL)

                    if ans is not None and ans1 is not None:
                        r = random.randint(0, 1)
                        if r == 0:
                            self.add_ship(ans)
                        else:
                            self.add_ship(ans1)
                    elif ans is not None:
                        self.add_ship(ans)
                    elif ans1 is not None:
                        self.add_ship(ans1)
                    else:
                        continue
                    break
            c += 1

    def generation_ship(self, size_ship, cell, direction):
        """Создание корабля с проверкой, что рядом нет соседей.
        Возвращает корабль, иначе None"""
        ans = []
        for delta in range(size_ship):
            if direction == Direction.HORIZONTAL:
                ans.append(
                    Cell((cell.x + delta) % self.size_x, cell.y))
            else:
                ans.append(
                    Cell(cell.x, (cell.y + delta) % self.size_y))
        for point in ans:
            if self._check_alive_neighbors(point):
                return None
        return Ship(ans)

    def add_ship(self, ship):
        """Добавление корабля на поле"""
        self.cells.extend(ship)
        self.ships.append(ship)
        self._completion_dict_ships(ship)

    def check_shot(self, x, y):
        """По координатам проверяет, содержится ли точка в
        списке выстрелов по полю"""
        return Cell(x, y) in self.shots

    def _check_alive_neighbors(self, cell):  # Есть ли живые соседи
        """Возвращает True, если есть живые клетки-соседи на поле"""
        for i in range(-1, 2):
            for j in range(-1, 2):
                point = Cell(
                    (cell.x + i) % self.size_x, (cell.y + j) % self.size_y)
                if (i != 0 or j != 0) and point in self.cells:
                    return True
        return False

    def _completion_dict_ships(self, ship):
        """Заполняет словарь принадлежности клетки к кораблю"""
        for cell in ship:
            self.dict_ships[cell] = ship

    def shot(self, *point):
        """Выстрел по клетке
        Возвращает True, если попал,
        False, если не попал и
        None, если выстрела не произошло"""
        if len(point) < 1 or len(point) > 2:
            return None

        if len(point) == 1:
            cell = point[0]
        else:
            cell = Cell(point[0], point[1])

        if cell not in self.shots:
            if cell in self.cells:
                self.shots[cell] = True
                self.cells.remove(cell)
                if self._check_ship(cell):
                    self._border_dead_ship(self.dict_ships[cell])
                return True
            else:
                self.shots[cell] = False
                return False
        return None

    def _check_ship(self, cell):
        """Возвращает True, если корабль мёртв"""
        for point in self.dict_ships[cell]:
            if point not in self.shots:
                return False
        return True

    def _border_dead_ship(self, ship):
        """Автоматические 'выстрелы' по обводке мёртвого корабля"""
        for cell in ship:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    point = Cell(
                        (cell.x + i) % self.size_x, (cell.y + j) % self.size_y)
                    if point not in self.shots:
                        self.shot(point)

    def is_empty(self):
        """Возвращает True, если живых клеток не осталось"""
        if len(self.cells) < 1:
            return True
        return False


class Game:
    """Игра"""
    def __init__(self, size_x, size_y, max_size_ship, level):
        """Создание игры с ботом"""
        self.size_x = size_x
        self.size_y = size_y
        self.max_size_ship = max_size_ship
        self.bot = Player('Bot', Field(size_x, size_y, max_size_ship))
        self.player = Player('Nikolai', Field(size_x, size_y, max_size_ship))
        self.first_player_current = True
        if level == 1:
            self.shot_botAI = BotAI.shot_level_1
        else:
            self.shot_botAI = BotAI.shot_level_2

    def start(self):
        """Начало игры со случайной расстановкой кораблей"""
        self.player.field.random_placement_ships()
        self.bot.field.random_placement_ships()

    def restart(self):
        self.bot = Player('Bot', Field(self.size_x, self.size_y, self.max_size_ship))
        self.player = Player('Nikolai', Field(self.size_x, self.size_y, self.max_size_ship))
        self.first_player_current = True
        self.start()

    def shot(self, point=None):
        """Выстрел того, чья сейчас очередь"""
        if self.first_player_current and point is not None:
            cell = Cell(point[0], point[1])
            result_shot = self.bot.field.shot(cell)
        else:
            result_shot = self.shot_botAI(self.player.field)

        if result_shot is not None and not result_shot:
            self.first_player_current = not self.first_player_current

    def player_is_win(self):
        """Возвращает True, если выиграл Игрок,
        Возвращает False, если победил бот
        И None, если игра ещё не закончилась"""
        if self.bot.field.is_empty():
            return True
        if self.player.field.is_empty():
            return False
        return None

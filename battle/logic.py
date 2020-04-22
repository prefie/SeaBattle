"""Модуль реализует логику игры «Морской бой»"""

import random
from enum import Enum


class Direction(Enum):
    """Направление корабля"""
    HORIZONTAL = 0
    VERTICAL = 1


class ResultShot(Enum):
    """Результат выстрела"""
    CANCEL = -1
    MISS = 0
    HIT = 1


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

    def shot(self, cell):
        """Выстрел по клетке
        Возвращает ResultShot.HIT, если попал,
        ResultShot.MISS, если не попал и
        ResultShot.CANCEL, если выстрела не произошло"""
        if cell not in self.shots:
            if cell in self.cells:
                self.shots[cell] = True
                self.cells.remove(cell)
                if self._check_ship(cell):
                    self._border_dead_ship(self.dict_ships[cell])
                return ResultShot.HIT
            else:
                self.shots[cell] = False
                return ResultShot.MISS
        return ResultShot.CANCEL

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

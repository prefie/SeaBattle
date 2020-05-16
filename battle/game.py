"""Модуль реализует логику игры «Морской бой»"""

import random
import re
import json
import zlib
from battle.botAI import BotAI
from enum import Enum
from math import sqrt


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

    @staticmethod
    def fromstr(string):
        string_split = list(map(int, re.findall(r'\d+', string)))
        return Cell(string_split[0], string_split[1])

    def __eq__(self, other):
        """Проверка равенства клеток"""
        return self.x == other.x and self.y == other.y

    def __str__(self):
        """Строковое представление клетки (x, y)"""
        return f'{self.x},{self.y}'

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

    def __str__(self):
        return '.'.join(map(str, self.cells))


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
        if not self._checking_placement():
            raise ValueError
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
        for cell in ship:
            self.dict_ships[cell] = ship

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

    def _completion_dict_ships(self):
        """Заполняет словарь принадлежности клетки к кораблю"""
        for ship in self.ships:
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

    @staticmethod
    def fromstr(string):
        size_x, size_y, max_size_ship, cells, ships, shots = string.split(';')
        size_x, size_y, max_size_ship =\
            list(map(int, (size_x, size_y, max_size_ship)))
        field = Field(size_x, size_y, max_size_ship)
        field._cells_fromstr(cells)
        field._ships_fromstr(ships)
        field._shots_fromstr(shots)
        field._completion_dict_ships()
        return field

    def _checking_placement(self):
        """Возвращает True, если расстановка
        с таким количеством кораблей возможна"""
        count = 0
        c = 1  # Кораблей столькоклеточных
        for size_ship in range(self.max_size_ship, 0, -1):
            for _ in range(c):
                count = count + 2 * c + 3
            c += 1
        count = count - (self.size_x + self.size_y)
        return (count <= self.size_y * self.size_x and
                self.size_x > self.max_size_ship and
                self.size_y > self.max_size_ship)

    def _cells_instr(self):
        return ':'.join(map(str, self.cells))

    def _cells_fromstr(self, string):
        list_cells = []
        string_split = string.split(':')
        for cell in string_split:
            list_cells.append(Cell.fromstr(cell))
        self.cells = list_cells

    def _ships_instr(self):
        return ':'.join(map(str, self.ships))

    def _ships_fromstr(self, string):
        list_ships = []
        string_split = string.split(':')
        for ship in string_split:
            strings_cells = ship.split('.')
            list_cells = [Cell.fromstr(cell) for cell in strings_cells]
            list_ships.append(Ship(list_cells))
        self.ships = list_ships

    def _shots_instr(self):
        return ':'.join(map(lambda shot: '.'.join(map(str, shot)),
                            self.shots.items()))

    def _shots_fromstr(self, string):
        if len(string) < 1:
            return
        dict_shots = {}
        string_split = string.split(':')
        for shot in string_split:
            shot_split = shot.split('.')
            dict_shots[Cell.fromstr(shot_split[0])] = shot_split[1] == 'True'
        self.shots = dict_shots

    def __str__(self):
        string = ";".join(
            map(str, (self.size_x, self.size_y, self.max_size_ship))) + ";"
        return string + ";".join((self._cells_instr(),
                                  self._ships_instr(),
                                  self._shots_instr()))

    def __eq__(self, other):
        return (other.size_x == self.size_x and
                other.size_y == self.size_y and
                other.max_size_ship == self.max_size_ship and
                other.cells == self.cells and
                other.ships == self.ships and
                other.dict_ships == self.dict_ships and
                other.shots == self.shots)


class Game:
    """Игра"""

    def __init__(self, size_x, size_y, max_size_ship, level):
        """Создание игры с ботом"""
        self.size_x = size_x
        self.size_y = size_y
        self.max_size_ship = max_size_ship
        self.level = level
        self.bot = Player('Bot', Field(size_x, size_y, max_size_ship))
        self.player = Player('Nikolai', Field(size_x, size_y, max_size_ship))
        self.first_player_current = True
        if level == 1:
            self.shot_botAI = BotAI.shot_level_1
        else:
            self.shot_botAI = BotAI.shot_level_2

        self._count_undo = int(sqrt(max(self.size_x, self. size_y)))
        self._states_fields_log = []

    def start(self):
        """Начало игры со случайной расстановкой кораблей"""
        self.player.field.random_placement_ships()
        self.bot.field.random_placement_ships()

    def restart(self):
        self.bot = Player(
            'Bot', Field(self.size_x, self.size_y, self.max_size_ship))
        self.player = Player(
            'Nikolai', Field(self.size_x, self.size_y, self.max_size_ship))
        self.first_player_current = True
        self._count_undo = int(sqrt(max(self.size_x, self.size_y)))
        self.start()

    def shot(self, point=None):
        """Выстрел того, чья сейчас очередь"""
        if (self.first_player_current and
                not self.bot.field.check_shot(point[0], point[1])):
            self._remember_states_fields()

        if self.first_player_current and point is not None:
            cell = Cell(point[0], point[1])
            result_shot = self.bot.field.shot(cell)
        elif not self.first_player_current:
            result_shot = self.shot_botAI(self.player.field)
            """Заполнение списка состояний"""
        else:
            result_shot = None

        if result_shot is not None and not result_shot:
            self.first_player_current = not self.first_player_current

    def _remember_states_fields(self):
        player_field = Field.fromstr(str(self.player.field))
        bot_field = Field.fromstr(str(self.bot.field))
        self._states_fields_log.append(
            (player_field, bot_field, self.first_player_current))

    def can_undo(self):
        return len(self._states_fields_log) > 0 and self._count_undo > 0

    def undo(self):
        if not self.can_undo():
            return
        self.player.field, self.bot.field, self.first_player_current =\
            self._states_fields_log.pop()
        self._count_undo -= 1

    @staticmethod
    def load_game():
        with open('save', 'rb') as f:
            data = json.loads(zlib.decompress(f.read()).decode('utf-8'))
            player_field = Field.fromstr(data['player_field'])
            bot_filed = Field.fromstr(data['bot_field'])
            size_x = int(data['size_x'])
            size_y = int(data['size_y'])
            max_size_ship = int(data['max_size_ship'])
            level = int(data['max_size_ship'])
            game = Game(size_x, size_y, max_size_ship, level)
            game.player.field = player_field
            game.bot.field = bot_filed
            return game

    def save_game(self):
        with open('save', 'wb') as f:
            data = {
                'size_x': str(self.size_x),
                'size_y': str(self.size_y),
                'max_size_ship': str(self.max_size_ship),
                'level': str(self.level),
                'player_field': str(self.player.field),
                'bot_field': str(self.bot.field)
            }
            f.write(zlib.compress(json.dumps(data).encode('utf-8')))

    def player_is_win(self):
        """Возвращает True, если выиграл Игрок,
        Возвращает False, если победил бот
        И None, если игра ещё не закончилась"""
        if self.bot.field.is_empty():
            return True
        if self.player.field.is_empty():
            return False
        return None

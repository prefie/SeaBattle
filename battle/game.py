"""Модуль реализует логику игры «Морской бой»"""

import random
import re
import json
import zlib
import logging
from battle.botAI import BotAI
from enum import Enum
from math import sqrt

REGULAR = re.compile(
    r'\d+;\d+;\d+;(\d+,\d+:?)*;((\d+,\d+\.?)+:?)*;(\d+,\d+\.\w+:?)*')
logging.basicConfig(level=logging.INFO, filename='game.log')
LOGGER_NAME = 'battle.game'
LOGGER = logging.getLogger(LOGGER_NAME)


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
        """Создание клетки из её текстового представления"""
        if re.match(r'\d+,\d+', string) is None:
            raise ValueError(string)

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
        for cell in other.cells:
            if cell not in self.cells:
                return False

        for cell in self.cells:
            if cell not in other.cells:
                return False
        return True

    def __str__(self):
        return '.'.join(map(str, self.cells))


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

        if not self._check_placement() or size_x < 4 or size_y < 2:
            raise ValueError(size_x, size_y, max_size_ship)

        self.cells = []  # список живых клеток
        self.shots = {}  # список выстрелов
        self._ships = []  # список кораблей
        self._dict_ships = {}  # Какая точка какому кораблю принадлежит

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
        """Возвращает True, если удалось разместить корабль"""
        for cell in ship:
            if (self._check_alive_neighbors(cell) or
                    cell in self.cells):
                return False

        self.cells.extend(ship)
        self._ships.append(ship)
        for cell in ship:
            self._dict_ships[cell] = ship
        return True

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
        for ship in self._ships:
            for cell in ship:
                self._dict_ships[cell] = ship

    def shot(self, *point):
        """Выстрел по клетке
        Возвращает True, если попал,
        False, если не попал и
        None, если выстрела не произошло"""
        if len(point) < 1 or len(point) > 2:
            return None

        if len(point) == 1 and isinstance(point[0], Cell):
            cell = point[0]
        else:
            cell = Cell(point[0], point[1])

        if cell not in self.shots:
            if cell in self.cells:
                self.shots[cell] = True
                self.cells.remove(cell)
                if self._check_ship(cell):
                    self._border_dead_ship(self._dict_ships[cell])
                return True
            else:
                self.shots[cell] = False
                return False
        return None

    def _check_ship(self, cell):
        """Возвращает True, если корабль мёртв"""
        for point in self._dict_ships[cell]:
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
        return len(self.cells) < 1

    @staticmethod
    def fromstr(string):
        """Создание поля из его текстового представления"""

        match = re.match(REGULAR, string)
        if match is None or len(match.group()) != len(string):
            raise ValueError(string)

        size_x, size_y, max_size_ship, cells, ships, shots = string.split(';')
        size_x, size_y, max_size_ship =\
            list(map(int, (size_x, size_y, max_size_ship)))
        field = Field(size_x, size_y, max_size_ship)
        field._cells_fromstr(cells)
        field._ships_fromstr(ships)
        field._shots_fromstr(shots)
        field._completion_dict_ships()
        return field

    def _check_placement(self):
        """Возвращает True, если расстановка
        с таким количеством кораблей возможна"""
        count = 0
        c = 1  # Кораблей столькоклеточных
        for size_ship in range(self.max_size_ship, 0, -1):
            for _ in range(c):
                count = count + 2 * c + 2
            c += 1
        return (count <= self.size_y * self.size_x and
                self.size_x > self.max_size_ship and
                self.size_y > self.max_size_ship)

    def _cells_instr(self):
        return ':'.join(map(str, self.cells))

    def _cells_fromstr(self, string):
        if len(string) < 1:
            return

        list_cells = []
        string_split = string.split(':')
        for cell in string_split:
            list_cells.append(Cell.fromstr(cell))
        self.cells = list_cells

    def _ships_instr(self):
        return ':'.join(map(str, self._ships))

    def _ships_fromstr(self, string):
        if len(string) < 1:
            return

        list_ships = []
        string_split = string.split(':')
        for ship in string_split:
            strings_cells = ship.split('.')
            list_cells = [Cell.fromstr(cell) for cell in strings_cells]
            list_ships.append(Ship(list_cells))
        self._ships = list_ships

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
        """Текстовое представление игрового поля"""
        string = ";".join(
            map(str, (self.size_x, self.size_y, self.max_size_ship))) + ";"
        return string + ";".join((self._cells_instr(),
                                  self._ships_instr(),
                                  self._shots_instr()))

    def __eq__(self, other):
        if not isinstance(other, Field):
            return False

        return (self.size_x == other.size_x and
                self.size_y == other.size_y and
                self.max_size_ship == other.max_size_ship and
                self.cells == other.cells and
                self.shots == other.shots and
                self._ships == self._ships)


class Player:
    """Игрок"""
    def __init__(self, field):
        self.field = field

    def shot(self, field, x, y):
        """Выстрел по данному полю, позвращает результат выстрела"""
        return field.shot(x, y)


class Game:
    """Игра"""

    def __init__(self, size_x, size_y, max_size_ship, level):
        """Создание игры с ботом"""
        LOGGER.info('The game is created.')
        self.level = level
        self.player = Player(Field(size_x, size_y, max_size_ship))
        self.bot = BotAI(Field(size_x, size_y, max_size_ship), level)
        self.player_current = True

        self._count_undo = int(sqrt(max(size_x, size_y)))
        self._states_fields_log = []

    def start(self):
        """Начало игры со случайной расстановкой кораблей"""
        LOGGER.info('The game started.')
        self.player.field.random_placement_ships()
        self.bot.field.random_placement_ships()

    def restart(self):
        """Рестарт игры"""
        LOGGER.info('The game is restarted with the current settings.')
        self.bot.field = Field(
            self.bot.field.size_x,
            self.bot.field.size_y,
            self.bot.field.max_size_ship)

        self.player.field = Field(
            self.player.field.size_x,
            self.player.field.size_y,
            self.player.field.max_size_ship)

        self.player_current = True
        self._count_undo = int(sqrt(max(self.bot.field.size_x,
                                        self.bot.field.size_y)))

        self._states_fields_log.clear()
        self.start()

    def shot(self, point=None):
        """Выстрел того, чья сейчас очередь
        Возвращает True, если попадание"""
        if (self.player_current and
                point is not None and
                not self.bot.field.check_shot(point[0], point[1])):
            self._remember_states_fields()

        if self.player_current and point is not None and not self.bot.field.check_shot(point[0], point[1]):
            result_shot = self.player.shot(self.bot.field, point[0], point[1])
            LOGGER.info(f'The player made shot at (%s, %s) and {"hit" if result_shot else "missed"}',
                        point[0], point[1])
        elif not self.player_current:
            result_shot = self.bot.shot(self.player.field)
            LOGGER.info(f'The bot made shot at (%s, %s) and {"hit" if result_shot else "missed"}',
                        self.bot.last_shot[0], self.bot.last_shot[1])
        else:
            result_shot = None

        if result_shot is not None and not result_shot:
            self.player_current = not self.player_current

        return result_shot

    def _remember_states_fields(self):
        player_field = Field.fromstr(str(self.player.field))
        bot_field = Field.fromstr(str(self.bot.field))
        self._states_fields_log.append(
            (player_field, bot_field))

    def can_undo(self):
        """Возвращает True, если есть ходы для отмены"""
        return len(self._states_fields_log) > 0 and self._count_undo > 0

    def undo(self):
        """Отмена хода"""
        if not self.can_undo():
            return

        self.player.field, self.bot.field =\
            self._states_fields_log.pop()
        self.player_current = True
        self._count_undo -= 1
        LOGGER.info(f"The player's last move was canceled. You can cancel: {self._count_undo}")

    @staticmethod
    def load_game(filename='save'):
        """Возвращает игру, загруженную из файла"""
        with open(filename, 'rb') as f:
            data = json.loads(zlib.decompress(f.read()).decode('utf-8'))
            level = int(data['level'])
            player_field = Field.fromstr(data['player_field'])
            bot_filed = Field.fromstr(data['bot_field'])
            game = Game(
                player_field.size_x,
                player_field.size_y,
                player_field.max_size_ship,
                level)

            game.player.field = player_field
            game.bot.field = bot_filed
            LOGGER.info(f'The game was downloaded from a file.')
            return game

    def save_game(self, filename='save'):
        """Сохранение игры в файл"""
        with open(filename, 'wb') as f:
            data = {
                'level': str(self.level),
                'player_field': str(self.player.field),
                'bot_field': str(self.bot.field)
            }
            f.write(zlib.compress(json.dumps(data).encode('utf-8')))
        LOGGER.info(f'The game was saved to a file.')

    def is_player_win(self):
        """Возвращает True, если выиграл Игрок,
        Возвращает False, если победил бот
        И None, если игра ещё не закончилась"""
        if self.bot.field.is_empty():
            LOGGER.info('The player won.')
            return True
        if self.player.field.is_empty():
            LOGGER.info('The bot won.')
            return False
        return None

    def __eq__(self, other):
        if not isinstance(other, Game):
            return False

        return (self.level == other.level and
                self.player.field == other.player.field and
                self.bot.field == other.bot.field)

"""Модуль реализует создание и управление игрой «Морской бой»"""

from battle.logic import Player, Field, Cell, ResultShot
from battle.botAI import BotAI


class Game:
    """Игра"""
    def __init__(self, size_x, size_y, max_size_ship, level):
        """Создание игры с ботом"""
        self.player = Player('Nikolai', Field(size_x, size_y, max_size_ship))
        self.bot = Player('Bot', Field(size_x, size_y, max_size_ship))
        self.first_player_current = True
        if level == 1:
            self.botAI = BotAI.shot_level_1
        else:
            self.botAI = BotAI.shot_level_1

    def start(self):
        """Начало игры со случайной расстановкой кораблей"""
        self.player.field.random_placement_ships()
        self.bot.field.random_placement_ships()

    def shot(self, point=None):
        """Выстрел того, чья сейчас очередь"""
        if self.first_player_current:
            if point is None or len(point) != 2:
                return
            cell = Cell(point[0], point[1])
            if self.bot.field.shot(cell) == ResultShot.MISS:
                self.first_player_current = False
        else:
            if self.botAI(self.player.field) == ResultShot.MISS:
                self.first_player_current = True

    def player_is_win(self):
        """Возвращает True, если выиграл Игрок,
        Возвращает False, если победил бот
        И None, если игра ещё не закончилась"""
        if self.bot.field.is_empty():
            return True
        if self.player.field.is_empty():
            return False
        return None

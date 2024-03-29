"""Модуль реализует искусственный интеллект игры «Морской бой»"""

import random


class BotAI:
    number_levels = 2

    def __init__(self, field, level_bot):
        if level_bot < 1 or level_bot > BotAI.number_levels:
            raise ValueError('Incorrect level of the bot.')

        self.field = field
        self.level_bot = level_bot
        self.last_shot = None

        self._recommend = set()

    def shot(self, field):
        """Выстрел по полю, возвращает результат выстрела"""
        if self.level_bot == 2:
            return self._shot_level_2(field)
        else:
            return self._shot_level_1(field)

    def _shot_level_1(self, field):
        """Случайный выстрел по полю
        Возвращает результат выстрела по полю"""
        x, y = self._generation_random(field)
        self.last_shot = (x, y)
        return field.shot(x, y)

    @staticmethod
    def _generation_random(field):
        x = random.randint(0, field.size_x - 1)
        y = random.randint(0, field.size_y - 1)
        while field.check_shot(x, y):
            x = random.randint(0, field.size_x - 1)
            y = random.randint(0, field.size_y - 1)
        return x, y

    def _shot_level_2(self, field):
        """Умный случайный выстрел по полю
        Возвращает результат выстрела по полю"""
        if len(self._recommend) < 1:
            x, y = self._generation_random(field)
        else:
            x, y = self._recommend.pop()
            if field.check_shot(x, y):
                return self._shot_level_2(field)

        result = field.shot(x, y)
        if result:
            self._recommendation_level_2(x, y, field)

        self.last_shot = (x, y)
        return result

    def _recommendation_level_2(self, x, y, field):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i == 0 or j == 0) and (i != j):
                    self._recommend.add(
                        ((x + i) % field.size_x, (y + j) % field.size_y))

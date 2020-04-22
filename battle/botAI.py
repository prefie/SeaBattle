"""Модуль реализует искусственный интеллект игры «Морской бой»"""

import random
import time

class BotAI:
    @classmethod
    def shot_level_1(cls, field):
        """Случайный выстрел по полю
        Возвращает координаты предполагаемого выстрела"""
        x, y = cls._generation_random(field)
        return field.shot(x, y)

    recommend = set()

    @classmethod
    def shot_level_2(cls, field):
        """Умный случайный выстрел"""
        if len(cls.recommend) < 1:
            x, y = cls._generation_random(field)
        else:
            x, y = cls.recommend.pop()
            while field.check_shot(x, y):
                if len(cls.recommend) < 1:
                    x, y = cls._generation_random(field)
                    break
                x, y = cls.recommend.pop()

        result = field.shot(x, y)
        if result:
            cls._recommendation_level_2(x, y, field)
        return result

    @classmethod
    def _recommendation_level_2(cls, x, y, field):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i == 0 or j == 0) and (i != j):
                    cls.recommend.add(
                        ((x + i) % field.size_x, (y + j) % field.size_y))

    @classmethod
    def _generation_random(cls, field):
        x = random.randint(0, field.size_x - 1)
        y = random.randint(0, field.size_y - 1)
        while field.check_shot(x, y):
            x = random.randint(0, field.size_x - 1)
            y = random.randint(0, field.size_y - 1)
        return x, y

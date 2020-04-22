"""Модуль реализует искусственный интеллект игры «Морской бой»"""

from battle.logic import Cell
import random


class BotAI:
    @staticmethod
    def shot_level_1(field):
        """Случайный выстрел по полю
        Возвращает результат выстрела"""
        x = random.randint(0, field.size_x - 1)
        y = random.randint(0, field.size_y - 1)
        cell = Cell(x, y)
        while cell in field.shots:
            x = random.randint(0, field.size_x - 1)
            y = random.randint(0, field.size_y - 1)
            cell = Cell(x, y)
        return field.shot(cell)

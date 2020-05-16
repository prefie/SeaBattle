# Игра «Морской бой»
Версия 0.1

Автор: Шушарин Николай (prefie@bk.ru)


## Описание
Данное приложение является консольной реализацией игры "Морской бой".
Вам предстоит сразиться с искусственным интеллектом различного уровня.
Игровое поле - тор, корабли - вертикальные или горизонтальные.
После запуска игры вы увидите два игровых поля. Ваше - левое, а поле соперника - правое.
Корабли выставляются случайно.
Игра заканчивается, когда все корабли одного из игроков погибают.
(Сделаны выстрелы по всем "живым" клеткам)


## Требования
* Python версии не ниже 3.6


## Состав
* Консольная версия: `seabattle.py`
* Модули: `battle/`
* Тесты: `test_game.py`


## Консольная версия
Справка по запуску: `./seabattle.py --help`

(Используйте для начала новой игры: `seabattle.py [-g height width max_size_ship level]`)

(Используйте для начала сохранённой игры: `seabattle.py [-l]`)

Пример запуска новой игры: `./seabattle.py -g 10 10 4 2`

Пример запуска сохранённой игры: `./seabattle.py -l`

### Управление

Вам следует кликать мышкой по клеткам игрового поля соперника,
чтобы наносить удары (выстрелы).

* ЛКМ — Нанести удар по клетке
* `q` - выход из игры
* `r` - рестарт игры c теми же параметрами
* `s` - сохранить текущую игру
* `u` - отменить ход (не более `int(sqrt(max(width, height)))` раз за партию)

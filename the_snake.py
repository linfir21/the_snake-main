from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Координаты центра экрана
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
ALL_DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
WHITE = (255, 255, 255)

# Словарь для управления направлением
DIRECTION_KEYS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
}

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()

"""Приятно познакомиться, Андрей. Не будь сильно строгим ко мне,
это моей первый серьезный проект, и я действительного многого еще не знаю.
Я постарался исправить всё то, что ты указал, но мог пропустить
или неверно понять, за ранее извини. И спасибо за похвалу,
в неоторых частях кода, я старался)
Буду рад твоим дальнейщим наставлениям."""


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=SCREEN_CENTER,
                 body_color=BOARD_BACKGROUND_COLOR):
        """Инициализирует игровой объект."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на экране."""
        raise NotImplementedError('Метод должен быть '
                                  'реализован в дочернем классе')

    def draw_cell(self, position=None, color=None):
        """Отрисовывает одну ячейку объекта на экране."""
        if position is None:
            position = self.position
        if color is None:
            color = self.body_color

        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)

        # Рисуем границу только если цвет ячейки не совпадает с цветом фона
        if color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, представляющий яблоко в игре."""

    def __init__(self, occupied_positions=(),
                 position=None, body_color=APPLE_COLOR):
        """Инициализирует яблоко со случайной позицией."""
        if position is None:
            position = SCREEN_CENTER
        super().__init__(position, body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Устанавливает случайную позицию для яблока
        в пределах игрового поля, избегая занятых позиций.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на экране."""
        self.draw_cell()


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self, position=SCREEN_CENTER, body_color=SNAKE_COLOR):
        """Инициализирует змейку с начальными параметрами."""
        super().__init__(position, body_color)
        self.reset()

    def reset(self, random_direction=False):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        if random_direction:
            self.direction = choice(ALL_DIRECTIONS)
        else:
            self.direction = RIGHT
        self.last = None

    def update_direction(self, new_direction):
        """Обновляет направление движения змейки."""
        if new_direction:
            self.direction = new_direction

    def get_head_position(self):
        """Возвращает позицию головы змейки.
        Returns:
            tuple: Координаты (x, y) головы змейки.
        """
        return self.positions[0]

    def move(self):
        """Двигает змейку."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_x = (head_x + (dir_x * GRID_SIZE)) % SCREEN_WIDTH
        new_y = (head_y + (dir_y * GRID_SIZE)) % SCREEN_HEIGHT
        new_position = (new_x, new_y)

        self.positions.insert(0, new_position)

        # Всегда удаляем последний элемент
        self.last = self.positions.pop()

        return new_position

    def grow(self):
        """Увеличивает длину змейки."""
        self.length += 1
        if self.last:
            self.positions.append(self.last)
            self.last = None

    def draw(self):
        """Отрисовывает змейку на экране."""
        # Отрисовка головы
        self.draw_cell(self.positions[0])

        # Затирание последнего сегмента
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для управления змейкой.

    Args:
        game_object (Snake): Объект змейки для управления.

    Returns:
        tuple: Новое направление движения или None.
    """
    new_direction = None

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            # Получаем новое направление из словаря
            new_direction = DIRECTION_KEYS.get((game_object.direction,
                                                event.key))

    return new_direction


def draw_score(snake_length):
    """Отрисовывает счет на экране."""
    font = pg.font.SysFont('Arial', 20)
    score_text = font.render(f'Длина: {snake_length}', True, WHITE)
    screen.blit(score_text, (10, 10))

    # Инструкции
    inst_text = font.render('Стрелки: управление, ESC: выход', True, WHITE)
    screen.blit(inst_text, (SCREEN_WIDTH - 350, 10))


def main():
    """Основная функция игры, содержащая главный игровой цикл."""
    # Инициализация PyGame:
    pg.init()

    # Создание экземпляров классов
    snake = Snake()
    apple = Apple(snake.positions)

    # Основной игровой цикл
    while True:
        clock.tick(SPEED)

        # Обработка действий пользователя
        new_direction = handle_keys(snake)
        snake.update_direction(new_direction)

        # Движение змейки
        new_head_position = snake.move()

        # Проверка столкновения с собой
        if new_head_position in snake.positions[1:]:
            # Очистка экрана при сбросе
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset(random_direction=True)
            apple.randomize_position(snake.positions)

        # Проверка съедения яблока (только если не было столкновения)
        elif new_head_position == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)

        # Отрисовка
        apple.draw()
        snake.draw()
        draw_score(len(snake.positions))  # Используем длину списка positions

        pg.display.update()


if __name__ == '__main__':
    main()

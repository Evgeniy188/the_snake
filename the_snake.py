from random import choice, randint

import pygame as pg

# Инициализация PyGame:
pg.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - серый:
BOARD_BACKGROUND_COLOR = (180, 180, 180)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет GameObject
GAMEOBJECT_COLOR = (0, 0, 255)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет неправильной еды
POISON_COLOR = (125, 0, 255)

# Цвет камня
STONE_COLOR = (0, 0, 0)

# Скорость движения змейки:
SPEED_MIN = 10
SPEED_MAX = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()

# Словарь для получения направления движения змейки
handle_keys_dict = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT
}


class GameObject:
    """это базовый класс, от которого наследуются другие
    игровые объекты.
    """

    position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def __init__(self, body_color=GAMEOBJECT_COLOR):
        self.body_color = body_color

    def draw_cell(self, surface, position, body_color=None):
        """Отрисовка одной ячейки"""
        rect = pg.Rect(
            (position[0], position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        body_color = body_color if body_color else self.body_color
        pg.draw.rect(surface, body_color, rect)
        return rect

    def draw(self):
        """Заготовка метода для отрисовки объекта на игровом поле."""
        raise NotImplementedError('Абстрактный метод, который предназначен для'
                                  'переопределения в дочерних классах')


class FieldObject(GameObject):
    """Класс, унаследованный от GameObject, описывающий яблоко и
    действия с ним.
    """

    def __init__(self, positions, body_color=APPLE_COLOR, ):
        super().__init__(body_color)
        self.snake_positions = positions
        self.randomize_position()

    def randomize_position(self):
        """Устанавливает случайное положение яблока на игровом поле — задаёт
        атрибуту position новое значение. Координаты выбираются так, чтобы
        яблоко оказалось в пределах игрового поля.
        """
        self.position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                         randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
        # Проверка что объект не появился в теле змеи
        while self.position in self.snake_positions:
            self.randomize_position()

    def draw(self, surface):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = self.draw_cell(surface, self.position)
        pg.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, унаследованный от GameObject, описывающий змейку и повдение
    змейки в игре.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.reset()
        self.next_direction = None
        self.last = [None, None]

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает позицию головы змейки
        (первый элемент в списке positions).
        """
        return self.positions[0]

    def move(self):
        """Обновляет позицию змейки (координаты каждой секции), добавляя новую
        голову в начало списка positions и удаляя последний элемент, если
        длина змейки не увеличилась.
        """
        # Прохождение змейки через границу поля и и появление с другой стороны
        head_position = self.get_head_position()
        head_position = [(head_position[0] + self.direction[0] * GRID_SIZE) %
                         SCREEN_WIDTH,
                         (head_position[1] + self.direction[1] * GRID_SIZE) %
                         SCREEN_HEIGHT]
        # Проверка столкновения змеи с собой
        if (head_position in self.positions) and (self.length > 1):
            self.reset()
        else:
            self.positions.insert(0, tuple(head_position))
            if (len(self.positions) - self.length) == 1:  # съела яблоко
                self.last[0] = self.positions.pop()
            elif (len(self.positions) - self.length) == 2:  # съела яд
                self.last[0] = self.positions.pop()
                self.last[1] = self.positions.pop()

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения
        с собой.
        """
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice([UP, DOWN, RIGHT, LEFT])
        screen.fill(BOARD_BACKGROUND_COLOR)

    def draw(self, surface):
        """Отрисовывает змейку на экране, затирая след."""
        for position in self.positions[:-1]:
            rect = (
                pg.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pg.draw.rect(surface, self.body_color, rect)
            pg.draw.rect(surface, BORDER_COLOR, rect, 1)
        # Отрисовка головы змейки
        rect = self.draw_cell(surface, self.positions[0])
        pg.draw.rect(surface, BORDER_COLOR, rect, 1)

        # Затирание последнего сегмента
        if self.last[0] and (self.last[1] is None):
            self.draw_cell(surface, self.last[0], BOARD_BACKGROUND_COLOR)

        # Затирание последнего и предпоследнего сегмента
        elif self.last[0] and self.last[1]:
            self.draw_cell(surface, self.last[0], BOARD_BACKGROUND_COLOR)
            self.draw_cell(surface, self.last[1], BOARD_BACKGROUND_COLOR)
            self.last[1] = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш, чтобы изменить направление
    движения змейки.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            game_object.next_direction = handle_keys_dict.get(
                (game_object.direction, event.key))


def score(score, speed):
    """Функция для отражения счета игры."""
    font_score = pg.font.SysFont('Constantia', 20)
    render_score = font_score.render(
        f'Счет: {score - 1} Скорость: {speed}', True, (0, 0, 0))
    rect = render_score.get_rect()
    rect.midtop = (100, 10)
    screen.blit(render_score, rect)


def main():
    """Функция описывающая логику игры."""
    snake = Snake()
    apple = FieldObject(snake.positions, APPLE_COLOR)
    poison = FieldObject(snake.positions, POISON_COLOR)
    stone = FieldObject(snake.positions, STONE_COLOR)
    n = 1  # счетчик для появления камней
    speed = SPEED_MIN

    while True:
        clock.tick(speed)
        handle_keys(snake)

        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:  # змея съела яблоко
            snake.length += 1
            apple.randomize_position()
            # Увеличение скорости игры при росте размера змеи
            if not (snake.length % 5) and speed <= SPEED_MAX:
                speed += 1
            screen.fill(BOARD_BACKGROUND_COLOR)

        if snake.get_head_position() == poison.position:  # змея съела яд
            snake.length -= 1
            if snake.length < 1:
                snake.reset()
                speed = SPEED_MIN
            poison.randomize_position()
            screen.fill(BOARD_BACKGROUND_COLOR)

        if ((n % 100) == 0) and randint(0, 1):  # изменение места камня
            stone.randomize_position()
            screen.fill(BOARD_BACKGROUND_COLOR)
            n = 1
        if (
            snake.get_head_position() == stone.position
            or snake.get_head_position() in snake.positions[1:]
        ):  # змея попала в камень или в саму себя
            snake.reset()
            speed = SPEED_MIN

        snake.draw(screen)
        apple.draw(screen)
        poison.draw(screen)
        stone.draw(screen)
        score(snake.length, speed)
        pg.display.update()
        n += 1


if __name__ == '__main__':
    main()

"""Запускает игру 'Змейка'."""
from random import choice, randint
import pygame as pg

# Инициализация pg:
pg.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
SCREEN_CENTER: tuple = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP: tuple = (0, -1)
DOWN: tuple = (0, 1)
LEFT: tuple = (-1, 0)
RIGHT: tuple = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR: tuple = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR: tuple = (93, 216, 228)

# Цвет яблока
APPLE_COLOR: tuple = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR: tuple = (0, 255, 0)

# Скорость движения змейки:
SPEED: int = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


# Все классы игры.
class GameObject(object):
    """Базовый класс, от которого наследуются другие игровые объекты.

    Он содержит общие атрибуты игровых объектов — например,
    эти атрибуты описывают позицию и цвет объекта.
    """

    def __init__(self):
        """Инициализирует базовые атрибуты объекта."""
        self.position = SCREEN_CENTER
        self.body_color = None

    def draw(self):
        """Метод определяет, как объект будет отрисовываться на экране.

        Абстрактный метод, предназначен для переопределения в дочерних классах.
        По умолчанию — pass.
        """


class Snake(GameObject):
    """Класс, описывающий змейку и действия с ней.

    Унаследован от GameObject.
    """

    def __init__(self):
        """Инициализирует атрибуты змейки."""
        super().__init__()
        self.reset()
        self.direction = RIGHT
        self.body_color = SNAKE_COLOR

    def update_direction(self, next_direction):
        """Обновляет направление движения змейки.

        :param next_direction: Cледующее направление движения,
        которое будет применено после обработки нажатия клавиши.
        """
        if next_direction:
            self.direction = next_direction
            next_direction = None

    def move(self):
        """Обновляет позицию змейки (координаты каждой секции).

        Добавляет новую голову в начало списка positions
        и удаляет последний элемент, если длина змейки не увеличилась.
        """
        head_position_x, head_position_y = self.head_position
        direction_x, direction_y = self.direction

        # Следующее условие высчитывает координаты новой головы змейки.
        # Для начала оно проверяет значение переменной direction_y.
        # Если direction_y равно 0, то это значит,
        # что позиция головы змейки обновляется по оси X,
        # учитывая значение переменной direction_x.
        # А оно в свою очередь равно либо 1, либо -1,
        # то есть мы можем просто умножать на direction_x не задумываясь о том,
        # движется змейка влево или вправо, потому что
        # автоматически получим значение для движения в нужную сторону
        # Если direction_y не равно 0, то мы делаем все тоже самое но по оси Y.
        # При этом координаты обновляются таким образом,
        # чтобы объект оставался в пределах экрана.
        if direction_y == 0:
            new_head_position_x = head_position_x + direction_x * GRID_SIZE
            self.head_position = (new_head_position_x % SCREEN_WIDTH,
                                  head_position_y
                                  )
        else:
            new_head_position_y = head_position_y + direction_y * GRID_SIZE
            self.head_position = (head_position_x,
                                  new_head_position_y % SCREEN_HEIGHT
                                  )

        self.positions.insert(0, self.head_position)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на экране, затирая след."""
        # Отрисовка головы змейки
        head_rect = pg.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect((self.last), (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.last = None
        self.head_position = self.get_head_position()
        self.next_direction = None


class Apple(GameObject):
    """Класс, описывающий яблоко и действия с ним.

    Унаследован от GameObject.
    """

    def __init__(self, snake_positions=SCREEN_CENTER, body_color=APPLE_COLOR):
        """Инициализирует атрибуты яблока.

        :param snake_positions: Список клеток занятых телом змейки.
        :param body_color: Цвет тела яблока. По умолчанию равен APPLE_COLOR.
        """
        self.randomize_position(snake_positions)
        self.body_color = body_color

    def randomize_position(self, snake_positions=SCREEN_CENTER):
        """Устанавливает случайное положение яблока на игровом поле.

        :param snake_positions: Список клеток занятых телом змейки.
        """
        while True:
            self.x_coordinate = (randint(0, SCREEN_WIDTH)
                                 * GRID_SIZE % SCREEN_WIDTH)
            self.y_coordinate = (randint(0, GRID_HEIGHT)
                                 * GRID_SIZE % SCREEN_HEIGHT)

            self.position = (self.x_coordinate, self.y_coordinate)

            if self.position not in snake_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pg.Rect((self.position), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш."""
    key_directions = {
        (pg.K_UP, RIGHT): UP,
        (pg.K_UP, LEFT): UP,
        (pg.K_DOWN, RIGHT): DOWN,
        (pg.K_DOWN, LEFT): DOWN,
        (pg.K_LEFT, UP): LEFT,
        (pg.K_LEFT, DOWN): LEFT,
        (pg.K_RIGHT, UP): RIGHT,
        (pg.K_RIGHT, DOWN): RIGHT
    }

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit('Игра завершена пользователем.')

        if event.type == pg.KEYDOWN:
            current_direction = game_object.direction
            new_direction = key_directions.get((event.key, current_direction),
                                               current_direction)
            game_object.next_direction = new_direction


def main():
    """Основной цикл игры.

    Здесь происходит обновление состояний объектов:
    змейка обрабатывает нажатия клавиш и двигается в соответствии
    с выбранным направлением.
    """
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction(snake.next_direction)
        snake.move()

        if (snake.head_position in
           snake.positions[1:] or snake.head_position == snake.last):
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(snake.positions)

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()

        pg.display.update()


if __name__ == '__main__':
    main()

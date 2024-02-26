from random import choice, randint
import pygame

# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Все классы игры.
class GameObject():
    """Базовый класс, от которого наследуются другие игровые объекты.
    Он содержит общие атрибуты игровых объектов — например,
    эти атрибуты описывают позицию и цвет объекта.
    """

    def __init__(self) -> None:
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = None

    def draw(self):
        """Абстрактный метод, который предназначен для переопределения
        в дочерних классах. Этот метод должен определять, как объект
        будет отрисовываться на экране. По умолчанию — pass.
        """
        pass


class Apple(GameObject):
    """Класс, унаследованный от GameObject,
    описывающий яблоко и действия с ним.
    """

    def __init__(self):
        self.position = self.randomize_position()
        self.body_color = APPLE_COLOR

    def randomize_position(self):
        """Устанавливает случайное положение яблока на игровом
        поле — задаёт атрибуту position новое значение.
        """
        self.x_coordinate = randint(0, GRID_WIDTH - GRID_SIZE) * GRID_SIZE
        self.y_coordinate = randint(0, GRID_HEIGHT - GRID_SIZE) * GRID_SIZE
        self.position = (self.x_coordinate, self.y_coordinate)
        return self.position

    def draw(self, surface):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(self.position[0], self.position[1],
                           GRID_SIZE, GRID_SIZE
                           )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, унаследованный от GameObject,
    описывающий змейку и её поведение.
    Этот класс управляет её движением, отрисовкой,
    а также обрабатывает действия пользователя.
    """

    def __init__(self):
        super().__init__()
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions
        и удаляя последний элемент, если длина змейки не увеличилась.
        """
        self.head_position = self.get_head_position()
        if self.direction == RIGHT:
            self.head_position = (self.head_position[0] + RIGHT[0] * GRID_SIZE,
                                  self.head_position[1] + RIGHT[1] * GRID_SIZE
                                  )
            if self.head_position[0] > 620:
                self.head_position = (0, self.head_position[1])

        if self.direction == LEFT:
            self.head_position = (self.head_position[0] + LEFT[0] * GRID_SIZE,
                                  self.head_position[1] + LEFT[1] * GRID_SIZE
                                  )
            if self.head_position[0] < 0:
                self.head_position = (620, self.head_position[1])

        if self.direction == UP:
            self.head_position = (self.head_position[0] + UP[0] * GRID_SIZE,
                                  self.head_position[1] + UP[1] * GRID_SIZE
                                  )
            if self.head_position[1] < 0:
                self.head_position = (self.head_position[0], 460)

        if self.direction == DOWN:
            self.head_position = (self.head_position[0] + DOWN[0] * GRID_SIZE,
                                  self.head_position[1] + DOWN[1] * GRID_SIZE
                                  )
            if self.head_position[1] > 480:
                self.head_position = (self.head_position[0], 0)

        self.positions.insert(0, self.head_position)

        if len(self.positions) > self.length + 1:
            self.positions.pop()

        self.snake_collision()

    def draw(self, surface):
        """Отрисовывает змейку на экране, затирая след."""
        for position in self.positions[:-1]:
            rect = (
                pygame.Rect((position[0], position[1]),
                            (GRID_SIZE, GRID_SIZE)
                            )
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)
        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки
        (первый элемент в списке positions).
        """
        return self.positions[0]

    def snake_collision(self):
        """Проверяет столкнулась ли змейка сама с собой.
        Если да то игра перезапускается.
        """
        if self.head_position in self.positions[1:]:
            self.reset()

    def reset(self):
        """Сбрасывает змейку в начальное состояние
        после столкновения с собой.
        """
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш,
    чтобы изменить направление движения змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной цикл игры, происходит обновление состояний объектов:
    змейка обрабатывает нажатия клавиш и двигается в соответствии
    с выбранным направлением.
    """
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.positions[0] == apple.position:
            snake.length += 1
            apple.randomize_position()
            while apple.randomize_position() in snake.positions:
                apple.randomize_position()

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)

        pygame.display.update()


if __name__ == '__main__':
    main()

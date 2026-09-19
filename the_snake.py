from __future__ import annotations

import random
from typing import Optional, Sequence

import pygame

# Псевдонимы типов (Type Aliases) для читаемости
Position = tuple[int, int]
Direction = tuple[int, int]
Color = tuple[int, int, int]

SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# frozenset используется далее, чтобы не поставить яблоко на место змейки
ALL_POSITIONS: frozenset[Position] = frozenset(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
)

UP: Direction = (0, -1)
DOWN: Direction = (0, 1)
LEFT: Direction = (-1, 0)
RIGHT: Direction = (1, 0)
SPEED: int = 7

BOARD_BACKGROUND_COLOR: Color = (0, 0, 0)
GRID_COLOR: Color = (40, 40, 40)
APPLE_COLOR: Color = (255, 0, 0)
SNAKE_COLOR: Color = (0, 255, 0)

pygame.init()
screen: pygame.Surface = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock: pygame.time.Clock = pygame.time.Clock()


class GameObject:
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self) -> None:
        """Инициализирует позицию по умолчанию и цвет объекта."""
        self.position: Optional[Position] = (
            GRID_WIDTH // 2 * GRID_SIZE,
            GRID_HEIGHT // 2 * GRID_SIZE,
        )
        self.body_color: Optional[Color] = None

    def draw(self, surface: pygame.Surface) -> None:
        """
        Абстрактный метод для переопределения в дочерних классах.

        Определяет, как объект будет отрисовываться на экране.
        """
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко."""

    def __init__(
        self, occupied_positions: Optional[Sequence[Position]] = None
    ) -> None:
        """Инициализирует яблоко, задаёт цвет и случайную позицию."""
        super().__init__()
        self.body_color: Color = APPLE_COLOR
        self.randomize_position(occupied_positions)

    def randomize_position(
        self, occupied_positions: Optional[Sequence[Position]] = None
    ) -> bool:
        """Устанавливает случайное положение яблока на игровом поле."""
        if occupied_positions is None:
            occupied_positions = []

        free_positions = ALL_POSITIONS - set(occupied_positions)
        if not free_positions:
            self.position = None
            return False

        self.position = random.choice(tuple(free_positions))
        return True

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        if self.position is not None:
            rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self) -> None:
        """Инициализирует начальное состояние змейки."""
        super().__init__()
        self.body_color: Color = SNAKE_COLOR
        self.length: int = 1
        self.positions: list[Position] = []
        self.direction: Direction = RIGHT
        self.next_direction: Optional[Direction] = None
        self.last: Optional[Position] = None
        self.reset()

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        if self.position is not None:
            self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self) -> None:
        """Обновляет направление движения змейки перед следующим шагом."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self) -> Position:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self) -> None:
        """
        Обновляет позицию змейки: добавляет новую голову и удаляет хвост,
        если длина не изменилась. Реализовано прохождение сквозь стены.
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        new_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head: Position = (new_x, new_y)

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает змейку на экране и затирает след."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)


def draw_grid(surface: pygame.Surface) -> None:
    """Отрисовывает серую сетку для абсолютно всех ячеек игрового поля."""
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш для изменения направления змейки."""
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
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit


def main() -> None:
    """Основной цикл игры."""
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            has_free_space = apple.randomize_position(snake.positions)
            if not has_free_space:
                snake.reset()
                apple.randomize_position(snake.positions)

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        screen.fill(BOARD_BACKGROUND_COLOR)
        draw_grid(screen)

        apple.draw(screen)
        snake.draw(screen)

        pygame.display.update()


if __name__ == '__main__':
    main()

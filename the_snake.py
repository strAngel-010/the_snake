from __future__ import annotations

import random
from typing import Optional, Sequence

import pygame as pg

import sys

# Псевдонимы типов (Type Aliases) для читаемости
Position = tuple[int, int]
Direction = tuple[int, int]
Color = tuple[int, int, int]

SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

DEFAULT_POSITION: Position = (
    GRID_WIDTH // 2 * GRID_SIZE,
    GRID_HEIGHT // 2 * GRID_SIZE,
)

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

BLACK: Color = (0, 0, 0)
DARK_GRAY: Color = (40, 40, 40)
RED: Color = (255, 0, 0)
GREEN: Color = (0, 255, 0)

BOARD_BACKGROUND_COLOR: Color = BLACK
GRID_COLOR: Color = DARK_GRAY
APPLE_COLOR: Color = RED
SNAKE_COLOR: Color = GREEN

pg.init()
screen: pg.Surface = pg.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock: pg.time.Clock = pg.time.Clock()


class GameObject:
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self, body_color: Optional[Color] = None) -> None:
        """Инициализирует позицию по умолчанию и цвет объекта."""
        self.position: Optional[Position] = DEFAULT_POSITION
        self.body_color: Optional[Color] = body_color

    def draw_cell(
        self,
        position: Position,
        fill_color: Optional[Color] = None,
        border_color: Color = GRID_COLOR,
    ) -> None:
        """Отрисовывает одну ячейку с заливкой и контуром."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        color = fill_color if fill_color is not None else self.body_color
        if color is not None:
            pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, border_color, rect, 1)

    def draw(self) -> None:
        """
        Абстрактный метод для переопределения в дочерних классах.

        Определяет, как объект будет отрисовываться на экране.
        """
        raise NotImplementedError(
            f'Метод draw() должен быть переопределен '
            f'в классе {self.__class__.__name__}'
        )


class Apple(GameObject):
    """Класс, описывающий яблоко."""

    def __init__(
        self,
        occupied_positions: Optional[Sequence[Position]] = None,
        body_color: Color = APPLE_COLOR
    ) -> None:
        """Инициализирует яблоко, задаёт цвет и случайную позицию."""
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(
        self, occupied_positions: Optional[Sequence[Position]] = None
    ) -> bool:
        """Устанавливает случайное положение яблока на игровом поле."""
        occupied_positions = occupied_positions or []

        free_positions = ALL_POSITIONS - set(occupied_positions)
        if not free_positions:
            return False

        self.position = random.choice(tuple(free_positions))
        return True

    def draw(self) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        if self.position is not None:
            self.draw_cell(self.position)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    next_direction: Optional[Direction]

    def __init__(self, body_color: Color = SNAKE_COLOR) -> None:
        """Инициализирует начальное состояние змейки."""
        super().__init__(body_color=body_color)
        self.position: Position = DEFAULT_POSITION
        self.reset()

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
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

    def draw(self) -> None:
        """Отрисовывает змейку на экране и затирает след."""
        self.draw_cell(self.get_head_position())

        if self.last:
            self.draw_cell(self.last, fill_color=BOARD_BACKGROUND_COLOR)


def draw_grid() -> None:
    """Отрисовывает серую сетку для абсолютно всех ячеек игрового поля."""
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pg.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pg.draw.rect(screen, GRID_COLOR, rect, 1)


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш для изменения направления змейки."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()


def main() -> None:
    """Основной цикл игры."""
    snake = Snake()
    apple = Apple(snake.positions)

    screen.fill(BOARD_BACKGROUND_COLOR)
    draw_grid()
    apple.draw()

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
                screen.fill(BOARD_BACKGROUND_COLOR)
                draw_grid()

            apple.draw()
        elif snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
            draw_grid()
            apple.draw()

        snake.draw()

        pg.display.update()


if __name__ == '__main__':
    main()

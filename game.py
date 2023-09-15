import pygame
from typing import Tuple, Literal, List
from enum import Enum

# TODO: Implement the gravity jump


class PyGameFileLogger:
    def log(self, data: List[Tuple[float, float]], file_name: str):
        with open(file_name, "a") as f:
            for data_value in data:
                f.write(f"{data_value.__str__().replace('(', '').replace(')', '')}\n")


class PyGameShapesEnum(Enum):
    CIRCLE = 1
    SQUARE = 2
    TRIANGLE = 3


class PyGameCoordinatesTransform:
    @staticmethod
    def transform_coordinates_flip(coordinates: Tuple[float, float], h: float):
        (x, y) = coordinates
        return (x, h - y)


class PyGame2DMotionEquations:
    def __init__(
        self,
        x0: float = 0,
        y0: float = 0,
        vx0: float = 0,
        vy0: float = 0,
        gravity: float = 9.81,
    ):
        """
        Implements the 2D motion equations.

        Args:
            x0 (float, optional): Initial horizontal position in meters (default 0).
            y0 (float, optional): Initial vertical position in meters (default 0).
            vx0 (float, optional): Initial horizontal velocity in meters per second (default 0).
            vy0 (float, optional): Initial vertical velocity in meters per second (default 0).
            gravity (float, optional): Acceleration due to gravity in meters per second squared (default 9.81).

        Attributes:
            a (float): Acceleration due to gravity in meters per second squared.
            x0 (float): Initial horizontal position in meters.
            y0 (float): Initial vertical position in meters.
            vx0 (float): Initial horizontal velocity in meters per second.
            vy0 (float): Initial vertical velocity in meters per second.
        """
        self.a = gravity
        self.x0 = x0
        self.y0 = y0
        self.vx0 = vx0
        self.vy0 = vy0

    def get_x_position(self, t: float):
        return (0.5 * self.a * t**2) + (self.vx0 * t) + self.x0

    def get_y_position(self, t: float):
        return (0.5 * self.a * t**2) + (self.vy0 * t) + self.y0

    def get_x_velocity(self, t: float):
        return self.a * t + self.vx0

    def get_y_velocity(self, t: float):
        return self.a * t + self.vy0


class PyGameObjecMotion(PyGame2DMotionEquations, PyGameFileLogger):
    def __init__(
        self, coords: Tuple, vx0: float = 0, vy0: float = 0, gravity: float = 9.81
    ):
        """
        Initializes a new instance of the PhysicsObject class.

        Args:
            coords (Tuple): A tuple containing the initial coordinates (x, y) of the object.
            vx0 (float, optional): The initial horizontal velocity of the object (default is 0).
            vy0 (float, optional): The initial vertical velocity of the object (default is 0).
            gravity (float, optional): The acceleration due to gravity (default is 9.81 m/s^2).

        Returns:
            None

        Attributes:
            coords (Tuple): The current coordinates (x, y) of the object.
            metrics (dict): A dictionary containing metrics such as velocity and position data.

        Example:
            To create a PhysicsObject with initial coordinates (2.0, 3.0),
            initial horizontal velocity 4.0, initial vertical velocity 5.0,
            and custom gravity 10.0:
            >>> initial_coords = (2.0, 3.0)
            >>> obj = PhysicsObject(initial_coords, vx0=4.0, vy0=5.0, gravity=10.0)
        """

        super().__init__(*coords, vx0, vy0, gravity)
        self.coords = coords
        self.metrics = {
            "velocity": [],
            "position": [],
        }

    def _forward(self, yi: float = 1):
        (x, y) = self.coords
        y -= yi
        self.coords = (x, y)

        self.metrics["position"].append(self.coords)

    def _backwards(self, yi: float = 1):
        (x, y) = self.coords
        y += yi
        self.coords = (x, y)

        self.metrics["position"].append(self.coords)

    def _left(self, xi: float = 1):
        (x, y) = self.coords
        x -= xi
        self.coords = (x, y)

        self.metrics["position"].append(self.coords)

    def _right(self, xi: float = 1):
        (x, y) = self.coords
        x += xi
        self.metrics["position"].append(self.coords)

        self.coords = (x, y)

    def _check_screen_collition(
        self, screen_width: int, screen_height: int, xi: int, yi: int, direction: str
    ):
        (x, y) = self.coords

        if direction == "right" and x + xi >= screen_width:
            return False
        elif direction == "left" and x - xi <= 0:
            return False
        elif direction == "up" and y - yi <= 0:
            return False
        elif direction == "down" and y + yi >= screen_height:
            return False

        return True

    def move(self, direction: str, yi: float = 1, xi: float = 1, steps: int = 1):
        if not self._check_screen_collition(
            screen_height=600,
            screen_width=600,
            xi=xi,
            yi=yi,
            direction=direction,
        ):
            return

        for _ in range(steps):
            if direction == "up":
                self._forward(yi)
            elif direction == "down":
                self._backwards(yi)
            elif direction == "left":
                self._left(xi)
            elif direction == "right":
                self._right(xi)
            else:
                raise ValueError("Direction is not valid")

    def jump(self, yi: int = 1, direction: Literal["up", "down"] = "up"):
        if direction == "up" and yi >= 0:
            self._forward(yi)
        elif direction == "down" and yi <= 0:
            self._backwards(yi)
        else:
            raise ValueError("Direction is not valid")

    def check_object_collision(self, objects):
        pass


class PyGameObject(PyGameObjecMotion, PyGameCoordinatesTransform):
    DEFAULT_COLOR = (255, 0, 0)

    # ! Move this to a separate class later
    get_pygame_shape = {
        PyGameShapesEnum.CIRCLE: pygame.draw.circle,
        PyGameShapesEnum.SQUARE: pygame.draw.rect,
        PyGameShapesEnum.TRIANGLE: pygame.draw.polygon,
    }

    def __init__(
        self,
        surface: pygame.Surface,
        coords: Tuple,
        shape: PyGameShapesEnum,
        vx0: float = 0,
        vy0: float = 0,
        gravity: float = 9.81,
        **kwargs,
    ):
        """
        Initializes a new instance of the PhysicsObject class.

        Args:
            surface (pygame.Surface): The pygame surface on which the object will be drawn.
            coords (Tuple): A tuple containing the initial coordinates (x, y) of the object.
            shape (PyGameShapesEnum): An enum representing the shape of the object.
            vx0 (float, optional): The initial horizontal velocity of the object (default is 0).
            vy0 (float, optional): The initial vertical velocity of the object (default is 0).
            gravity (float, optional): The acceleration due to gravity (default is 9.81 m/s^2).
            **kwargs: Additional keyword arguments for custom options.

        Returns:
            None

        Attributes:
            shape (pygame.Shape): The pygame shape associated with the object.
            surface (pygame.Surface): The surface on which the object is drawn.
            options (dict): A dictionary containing custom options for the object.

        Example:
            To create a PhysicsObject with a rectangle shape, on a pygame surface of size (800, 600):
            >>> surface = pygame.Surface((800, 600))
            >>> initial_coords = (400, 300)
            >>> shape = PyGameShapesEnum.RECTANGLE
            >>> obj = PhysicsObject(surface, initial_coords, shape)
        """
        super().__init__(coords, vx0, vy0, gravity)
        self.shape = self.get_pygame_shape[shape]
        self.surface = surface
        self.options = kwargs if len(kwargs.items()) else {}

    def draw(self):
        # Flip the coordinates to match the pygame's coordinate system
        # ! Change HEIGHT to a global variable as well as the WIDTH
        flipped_coords = self.transform_coordinates_flip(self.coords, 600)
        return self.shape(
            self.surface, self.DEFAULT_COLOR, flipped_coords, **self.options
        )


class PygameApp:
    DRACULA_THEME = (40, 42, 54)

    def __init__(self, width, height, caption, bg_color=DRACULA_THEME, **kwargs):
        self.width = width
        self.height = height
        self.caption = caption
        self.bg_color = bg_color
        self.screen = pygame.display.set_mode((width, height))
        self.options = kwargs if len(kwargs.items()) else {}

        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()

    def get_cursor_position(self):
        x, y = pygame.mouse.get_pos()
        return x, y

    def run(self):
        running = True

        # Player object
        player_radius = 20
        player = PyGameObject(
            self.screen,
            (self.width // 2, player_radius),
            PyGameShapesEnum.CIRCLE,
            radius=player_radius,
        )

        target_coordinates = (0, 0)

        while running:
            # Get the cursor position
            # x, y = self.get_cursor_position()
            # print(f"Cursor: ({x}, {y}) \n")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        target_coordinates = self.get_cursor_position()
                        print(f"Shooting at {target_coordinates}")

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        player.move("up", yi=5, steps=3)
                    elif event.key == pygame.K_DOWN:
                        player.move("down", yi=5, steps=3)
                    elif event.key == pygame.K_LEFT:
                        player.move("left", yi=0, xi=5, steps=3)
                    elif event.key == pygame.K_RIGHT:
                        player.move("right", yi=0, xi=5, steps=3)
                    elif event.key == pygame.K_SPACE:
                        player.jump(100, "up")

            # Fill the screen with the background color (clear it)
            self.screen.fill(self.bg_color)

            # Draw the player in the current pygame screen object
            player.draw()
            # print(player.coords)

            # Update the display
            pygame.display.flip()

            # Update the screen 60 times per second
            self.clock.tick(60)

        #  Save the position metrics to a csv file
        player.log(player.metrics["position"], "position.csv")

        pygame.quit()


if __name__ == "__main__":
    WIDTH = 600
    HEIGHT = 600

    app = PygameApp(WIDTH, HEIGHT, "Testing")
    app.run()

    pygame.quit()

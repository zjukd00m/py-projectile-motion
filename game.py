import math
import pygame
from time import time
from enum import Enum
from typing import Tuple, Literal, List

# TODO: Implement the gravity jump
# TODO: Implement the projectile launch


class PyGameText:
    def __init__(
        self,
        text: str,
        coords: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Tuple[int, int, int] = (0, 0, 0),
        font_style: str = None,
    ):
        self.text = text
        self.color = color
        self.background_color = background_color
        self.font_style = font_style if font_style else ""
        self.coords = coords

    def render(self, screen: pygame.surface.Surface):
        font = pygame.font.Font(None, 24)
        text = font.render(self.text, True, self.color, self.background_color)
        screen.blit(text, self.coords)


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
        ax: float = 0,
    ):
        """
        Implements the 2D motion equations.

        Args:
            x0 (float, optional): Initial horizontal position in meters (default 0).
            y0 (float, optional): Initial vertical position in meters (default 0).
            vx0 (float, optional): Initial horizontal velocity in meters per second (default 0).
            vy0 (float, optional): Initial vertical velocity in meters per second (default 0).
            gravity (float, optional): Acceleration due to gravity in meters per second squared (default 9.81).
            ax (float, optional): Acceleration

        Attributes:
            ay (float): Acceleration due to gravity in meters per second squared.
            ax (float): Acceleration on the X-axis in meters per second
            x0 (float): Initial horizontal position in meters.
            y0 (float): Initial vertical position in meters.
            vx0 (float): Initial horizontal velocity in meters per second.
            vy0 (float): Initial vertical velocity in meters per second.
        """
        self.ay = gravity
        self.ax = ax
        self.x0 = x0
        self.y0 = y0
        self.vx0 = vx0
        self.vy0 = vy0

    def get_x_position(self, t: float):
        ax = self.get_x_velocity(t) * t
        return (0.5 * ax * t**2) + (self.vx0 * t) + self.x0

    def get_y_position(self, t: float):
        return (0.5 * self.ay * t**2) + (self.vy0 * t) + self.y0

    def get_x_velocity(self, t: float):
        return self.ax * t + self.vx0

    def get_y_velocity(self, t: float):
        return self.ay * t + self.vy0


class PyGameObjecMotion(PyGame2DMotionEquations, PyGameFileLogger):
    def __init__(
        self,
        coords: Tuple,
        vx0: float = 0,
        vy0: float = 0,
        gravity: float = 9.81,
        ax: float = 0,
    ):
        """
        Initializes a new instance of the PhysicsObject class.

        Args:
            coords (Tuple): A tuple containing the initial coordinates (x, y) of the object.
            vx0 (float, optional): The initial horizontal velocity of the object (default is 0).
            vy0 (float, optional): The initial vertical velocity of the object (default is 0).
            gravity (float, optional): The acceleration due to gravity (default is 9.81 m/s^2).
            ax(float, optional): The acceleratiion in the x-axis (always 0)

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

    def _forward(self, h: float, yi: float = 1):
        (x, y) = self.coords

        if y - yi <= 0:
            y = h
        else:
            y -= yi

        self.coords = (x, y)

        self.metrics["position"].append(self.coords)

    def _backwards(self, h: float, yi: float = 1):
        (x, y) = self.coords

        if y + yi >= h:
            y = 0
        else:
            y += yi

        self.coords = (x, y)

        self.metrics["position"].append(self.coords)

    def _left(self, w: float, xi: float = 1):
        (x, y) = self.coords

        if x - xi <= 0:
            x = w
        else:
            x -= xi

        self.coords = (x, y)

        self.metrics["position"].append(self.coords)

    def _right(self, w: float, xi: float = 1):
        (x, y) = self.coords

        if x + xi >= w:
            x = 0
        else:
            x += xi

        self.coords = (x, y)

        self.metrics["position"].append(self.coords)

    def _check_screen_collition(
        self, screen_width: int, screen_height: int, xi: int, yi: int, direction: str
    ):
        (x, y) = self.coords

        if direction == "right" and x + xi >= screen_width:
            # x = 0
            return False
        elif direction == "left" and x - xi <= 0:
            # x = screen_width
            return False
        elif direction == "up" and y - yi <= 0:
            # y = 0
            return False
        elif direction == "down" and y + yi >= screen_height:
            # y = screen_height
            return False

        return True

    def move(
        self,
        direction: str,
        h: float,
        w: float,
        yi: float = 1,
        xi: float = 1,
        steps: int = 1,
    ):
        if not self._check_screen_collition(
            screen_height=h,
            screen_width=w,
            xi=xi,
            yi=yi,
            direction=direction,
        ):
            return

        for _ in range(steps):
            if direction == "up":
                self._forward(h, yi)
            elif direction == "down":
                self._backwards(h, yi)
            elif direction == "left":
                self._left(w, xi)
            elif direction == "right":
                self._right(w, xi)
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

    def launch(self, t: float):
        x = self.get_x_position(t / 1000)
        y = self.get_y_position(t / 1000)
        print(f"Launching position => ({x}, {y})")
        self.coords = (x, y)

    def get_velocity_module(self, t: float):
        if t <= 0:
            return math.sqrt(self.vx0**2 + self.vy0)

        vx = self.get_x_velocity(t)
        vy = self.get_y_velocity(t)

        return math.sqrt(vx**2 + vy**2)

    def get_velocity_angle(self):
        return math.atan(self.coords[0] / self.coords[1])

    def get_y_max(self, t: float):
        # The max height is reached when the velocity of the object equals 0
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

    def track_object(self, x_target: float, y_target: float):
        # Draw a line that goes from (x_object, y_object) to (x_target, y_target)
        x, y = self.transform_coordinates_flip(self.coords, h=600)
        return pygame.draw.line(
            self.surface,
            (0, 0, 255),
            (x, y),
            (x_target, y_target),
        )


class PygameApp:
    DRACULA_THEME = (40, 42, 54)

    def __init__(
        self, width, height, caption, bg_color=DRACULA_THEME, texts={}, **kwargs
    ):
        self.width = width
        self.height = height
        self.caption = caption
        self.bg_color = bg_color
        self.screen = pygame.display.set_mode((width, height))
        self.options = kwargs if len(kwargs.items()) else {}
        self.texts = texts

        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()

        self.current_time = 0
        self.previous_time = 0

    @staticmethod
    def to_seconds(milliseconds: float):
        return milliseconds / 1000

    def get_cursor_position(self):
        x, y = pygame.mouse.get_pos()
        return x, y

    def run(self):
        running = True

        # Player object
        player_radius = 20
        player = PyGameObject(
            self.screen,
            (player_radius, player_radius),
            PyGameShapesEnum.CIRCLE,
            vx0=10,
            vy0=10,
            radius=player_radius,
        )

        target_coordinates = (0, 0)
        launch_projectile = False
        track_projectile = False

        # player tracking line coordinates
        x_target = 0
        y_target = 0

        # ! -- Time Management
        # Delta time (time is framerate independent)
        # Time difference between current frame and the previous one
        dt = 0
        # self.current_time = pygame.time.get_ticks()
        self.current_time = time()

        self.text_list = {
            "coordinates": "",
            "velocity": "",
            "acceleration (y-axis)": "9.81 [m/s^2]",
            "acceleration (x-axis)": "",
        }

        while running:
            # Get the cursor position
            x, y = self.get_cursor_position()
            # print(f"Cursor: ({x}, {y}) \n")
            self.text_list["coordinates"] = f"({x}, {y})"

            formatted_current_time = "{:.20f}".format(self.current_time)
            formatted_previous_time = "{:20f}".format(self.previous_time)
            formatted_delta_time = "{:20f}".format(dt)

            # print(f"Current time = {formatted_current_time} [ms]")
            # print(f"Previous time = {formatted_previous_time} [ms]")
            # print(f"Formatted time = {formatted_delta_time} [ms]")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEMOTION:
                    x_target, y_target = self.get_cursor_position()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        target_coordinates = self.get_cursor_position()
                        print(f"Shooting at {target_coordinates}")

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        player.move("up", self.height, self.width, yi=5, steps=3)
                    elif event.key == pygame.K_DOWN:
                        player.move("down", self.height, self.width, yi=5, steps=3)
                    elif event.key == pygame.K_LEFT:
                        player.move(
                            "left", self.height, self.width, yi=0, xi=5, steps=3
                        )
                    elif event.key == pygame.K_RIGHT:
                        player.move(
                            "right", self.height, self.width, yi=0, xi=5, steps=3
                        )
                    elif event.key == pygame.K_SPACE:
                        launch_projectile = not launch_projectile
                    elif event.key == pygame.K_t:
                        track_projectile = not track_projectile

            # Fill the screen with the background color (clear it)
            self.screen.fill(self.bg_color)

            # -- Draw all the objects

            # Draw the player in the current pygame screen object
            if launch_projectile:
                # ? Which time to use ?
                # player.launch(t=)
                pass

            if track_projectile:
                # x_target, y_target = self.get_cursor_position()
                # print(f"({x_target}, {y_target})")
                player.track_object(x_target, y_target)

            player.draw()

            # Render text
            coordinates_text = "Cursor: " + self.text_list["coordinates"]
            player_text = f"Player: ({player.coords[0]}, {player.coords[1]})"
            time_text = f"Time: {pygame.time.get_ticks() / 1000} [s]"

            PyGameText(coordinates_text, (0, 0), (255, 255, 255)).render(
                screen=self.screen
            )
            PyGameText(player_text, (0, 27), (255, 255, 255)).render(screen=self.screen)
            PyGameText(time_text, (0, 54), (255, 255, 255)).render(screen=self.screen)

            # Update the display
            pygame.display.flip()

            # Update the screen 60 times per second
            self.clock.tick(60)

            # ! -- Time management
            dt = (self.current_time - self.previous_time) / 1000
            self.previous_time = self.current_time
            self.current_time = time()

        #  Save the position metrics to a csv file
        player.log(player.metrics["position"], "position.csv")

        pygame.quit()


if __name__ == "__main__":
    pygame.init()

    WIDTH = 600
    HEIGHT = 600

    app = PygameApp(WIDTH, HEIGHT, "Testing")
    app.run()

    pygame.quit()

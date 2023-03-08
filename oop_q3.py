from abc import ABC, abstractmethod
from math import pi


class Shape(ABC):
    """An abstract class to define a shape. It contains the abstract methods
    parameter and area."""

    @abstractmethod
    def get_parameter(self) -> float:
        """An abstract method to return the parameter of the shape."""
        pass

    @abstractmethod
    def get_area(self) -> float:
        """An abstract method to return the area of the shape."""
        pass


class Rectange(Shape):
    """A class that represents a Rectangle Shape. It implements the abstract
    class "Shape" and it's methods get_parameter and get_area."""

    def __init__(self, length: float, width: float) -> None:
        super().__init__()
        self.length = length
        self.width = width

    def get_parameter(self) -> float:
        """Returns the parameter of the rectangle."""

        return self.length + self.width

    def get_area(self) -> float:
        """Returns the area of the rectangle."""

        return self.length * self.width


class Circle(Shape):
    """A class that represents a Circle Shape. It implements the abstract
    class "Shape" and it's methods get_parameter and get_area."""

    def __init__(self, radius: float) -> None:
        super().__init__()
        self.radius = radius

    def get_parameter(self) -> float:
        """Returns the parameter of the circle."""

        return 2*pi*self.radius

    def get_area(self) -> float:
        """Returns the area of the circle."""

        return pi*(self.radius**2)


# testing code
if __name__ == "__main__":

    rec = Rectange(5, 2.5)
    print(rec.get_parameter())
    print(rec.get_area())
    circle = Circle(10)
    print(circle.get_area())
    print(circle.get_parameter())

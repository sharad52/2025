# Liskov Substitution Principle LSP

# Bad example
class BadRectangle:
    """Rectangle class that will be violated by BadSquare"""
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def set_width(self, width: float):
        self._width = width
    
    def set_height(self, height: float):
        self._height = height

    def get_width(self) -> float:
        return self._width
    
    def get_height(self) -> float:
        return self._height
    
    def area(self) -> float:
        return self._width * self._height


class BadSquare(BadRectangle):
    """This violates LSP - changing width affects height and vice versa"""
    def __init__(self, side: float):
        super().__init__(side, side)
    
    def set_width(self, width: float):
        # Violation: Changing width also changes height
        self._width = width
        self._height = width
    
    def set_height(self, height: float):
        # Violation: changing height also changes width
        self._width = height
        self._height = height

# Good example that adheres to the LSP
# Instead we make Abstract class and inherits from them

from abc import ABC, abstractmethod
import math


class Shape(ABC):
    """Base Classes for all shapes"""

    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        self._width = width
        self._height = height

    def area(self):
        return self._width * self._height
    
    def perimeter(self):
        return 2 * (self._width + self._height)
    
    @property
    def width(self) -> float:
        return self._width
    
    @property
    def height(self) -> float:
        return self._height
    

class Square(Shape):
    """Square as separate class - NOT inheriting from Rectangle"""
    def __init__(self, side: float) -> None:
        if side <= 0:
            raise ValueError("Side must be positive")
        self._side = side
    
    @property
    def side(self) -> float:
        return self._side
    
    def area(self):
        return self._side ** 2
    
    def perimeter(self):
        return 4 * self._side
    
        
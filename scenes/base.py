import pygame

class BaseScene:
    """Base class for all scenes in the Potion Shop game."""
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        """Processes a single Pygame event."""
        pass

    def update(self, dt):
        """Updates scene logic given the delta time (in seconds)."""
        pass

    def draw(self, screen):
        """Draws the scene onto the Pygame screen surface."""
        pass

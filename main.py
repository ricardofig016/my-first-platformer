import sys

from classes.game import Game
from classes.editor import Editor


if __name__ == "__main__":
    if "-editor" in sys.argv:
        Editor().run()
    else:
        Game().run()

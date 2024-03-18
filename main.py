import sys

from classes.game import Game
from classes.editor import Editor


if __name__ == "__main__":
    if "--editor" in sys.argv:
        try:
            map_name = sys.argv[sys.argv.index("--editor") + 1]
        except:
            map_name = ""
        Editor(map_name).run()
    elif "--custom-map" in sys.argv:
        try:
            map_name = sys.argv[sys.argv.index("--custom-map") + 1]
        except:
            map_name = ""
        Game(map_name).run()
    else:
        Game().run()

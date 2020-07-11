from displayio import Group, TileGrid
import math
import board
import time

GRAVITY = gravity=9.81

class Player(Group):
    def __init__(self, bitmap, palette):
        super().__init__(scale=1)
        self.tilegrid = TileGrid(bitmap, pixel_shader=palette,
                                     width=1,
                                     height=1,
                                     tile_width=16,
                                     tile_height=16)

        self.append(self.tilegrid)
        self._source_index = 0
        self.animating = False

    def celebrate(self):
        for i in range(0,6):
            self.tilegrid[0] = 1
            time.sleep(0.2)
            self.tilegrid[0] = 2
            time.sleep(0.2)
        self.tilegrid[0] = 0
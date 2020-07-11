from displayio import Group
import math
import board
GRAVITY = gravity=9.81

class Banana(Group):
    def __init__(self, tilegrid):
        super().__init__(scale=1)
        self.append(tilegrid)
        self.tilegrid = tilegrid
        self._source_index = 0
        self.is_throwing = False
        self._throwing_time = -1

    def update(self):
        self._animate()
        if self.is_throwing:
            _new_x = self._vx * self._throwing_time
            _new_y = (self._vy * self._throwing_time - (GRAVITY/2)*self._throwing_time*self._throwing_time)
            #print("({}, {})".format(_new_x, _new_y))
            self._throwing_time += .075
            self.x += int(_new_x)
            self.y -= int(_new_y)

    def _animate(self):
        self.tilegrid[0] = self._source_index
        self._source_index += 1
        if self._source_index >= 4:
            self._source_index = 0

    def throw(self, angle, velocity):

        self._throwing_time = .075*2
        self._angle = angle
        self._velocity = velocity

        self._vx=velocity * math.cos(math.radians(angle))
        self._vy=velocity * math.sin(math.radians(angle))
        self.is_throwing = True

        pass

    def stop_throw(self):
        self._throwing_time = 0
        self._angle = None
        self._velocity = None
        self._vx= None
        self._vy= None
        self.is_throwing = False
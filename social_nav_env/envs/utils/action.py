from collections import namedtuple

ActionXY = namedtuple('ActionXY', ['vx', 'vy'])
ActionRot = namedtuple('ActionRot', ['v', 'r'])
ActionDir = namedtuple('ActionDir', ['F', 'FR', 'R', 'BR', 'B', 'BL', 'L', 'FL'])
ActionSpd = namedtuple('ActionSpd', ['S', 'M', 'F'])

import matplotlib.pyplot as plt
import pygame
import numpy

from astar import AStar
import math

import dispUtils

def planPath(surface, agent, target):
    map = pygame.surfarray.array3d(surface) #transforming window surface into 3d array
    map = numpy.mean(map, axis=2, dtype=numpy.int) #taking the mean across RGB dimenisions
    pixelatedMap = []
    for row in range(0,len(map),50):
        pixelRow = []
        for column in range(0,len(map[row]),50):
            pixelVal = False
            for pixelx in range(50):
                for pixely in range(50):
                    if map[row + pixelx][column + pixely] == 0:
                        pixelVal = True
                        break
                if pixelVal:
                    break
            pixelRow.append(pixelVal)
        pixelatedMap.append(pixelRow)
    pixelatedMap = numpy.array(pixelatedMap)
    pixelatedMap = pixelatedMap.T
    # plt.imshow(pixelatedMap)
    # plt.show()
    #Generate new subgoals
    start = tuple([ math.floor(agent['position'][0]/50) , math.floor(agent['position'][1]/50) ])
    end = tuple([ math.floor(target['position'][0]/50) , math.floor(target['position'][1]/50) ])
    foundPath = MazeSolver(pixelatedMap).astar(start, end)
    subgoals = []
    path = []
    if foundPath is not None:
        foundPath = list(foundPath)
        # foundPath.reverse()
        pos = list(foundPath[0])
        pos[0] = pos[0]*50 +25
        pos[1] = pos[1]*50 +25
        subgoal = {'position': pos, 'size':100}
        subgoals.append(subgoal)
        path.append(agent['position'])

        for i in range(2,len(foundPath)):
            pos = list(foundPath[i])
            pos[0] = pos[0]*50 +25
            pos[1] = pos[1]*50 +25
            subgoal = {'position': pos, 'size':100}
            path.append(pos)


            # if dispUtils.getInterAgentDistace(subgoals[-1],subgoal)>200 and dispUtils.getInterAgentDistace(subgoal,target)>100:
            #     pos = list(foundPath[i-1])
            #     pos[0] = pos[0]*50 +25
            #     pos[1] = pos[1]*50 +25
            #     subgoal = {'position': pos, 'size':100}
            #     dispUtils.noCollideSpawnWithinRadius(surface, subgoal, [], 100, pos, 50)
            #     subgoals.append(subgoal)

            if dispUtils.corridorOfSight(surface,subgoals[-1],subgoal,55,65)==False and dispUtils.getInterAgentDistace(subgoals[-1],subgoal)>150 and dispUtils.getInterAgentDistace(subgoal,target)>100:
                pos = list(foundPath[i-1])
                pos[0] = pos[0]*50 +25
                pos[1] = pos[1]*50 +25
                subgoal = {'position': pos, 'size':100}
                dispUtils.noCollideSpawnWithinRadius(surface, subgoal, [], 100, pos, 50)
                tryCount = 0
                tryDist = 50
                while dispUtils.corridorOfSight(surface,subgoals[-1],subgoal,55,65)==False:
                    tryCount += 1
                    dispUtils.noCollideSpawnWithinRadius(surface, subgoal, [], 100, pos, tryDist)
                    if tryCount>100:
                        tryDist *= 1.5
                        tryCount = 0
                subgoals.append(subgoal)

        subgoals = subgoals[1:]
    return [path, subgoals]


class MazeSolver(AStar):

    """sample use of the astar algorithm. In this exemple we work on a maze made of ascii characters,
    and a 'node' is just a (x,y) tuple that represents a reachable position"""

    def __init__(self, maze):
        self.lines = maze
        self.width = len(self.lines[0])
        self.height = len(self.lines)

    def heuristic_cost_estimate(self, n1, n2):
        """computes the 'direct' distance between two (x,y) tuples"""
        (x1, y1) = n1
        (x2, y2) = n2
        return math.hypot(x2 - x1, y2 - y1)

    def distance_between(self, n1, n2):
        """this method always returns 1, as two 'neighbors' are always adajcent"""
        return 1

    def neighbors(self, node):
        """ for a given coordinate in the maze, returns up to 4 adjacent(north,east,south,west)
            nodes that can be reached (=any adjacent coordinate that is not a wall)
        """
        x, y = node
        return[(nx, ny) for nx, ny in [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y), (x + 1, y - 1), (x + 1, y + 1), (x - 1, y - 1), (x - 1, y + 1)] if 0 <= nx < self.width and 0 <= ny < self.height and self.lines[ny][nx] == False]

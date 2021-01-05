import math
import pygame
import random

import dataUtils
from . import drawers


def mapGeneration(surface, map_type):
    if map_type == "complex":
        map = mapGeneration_complex(surface)
        map_fill = [0,0,0]
        map_element_fill = [255,255,255]
    elif map_type == "twoRooms":
        map = mapGeneration_twoRooms(surface)
        map_fill = [255,255,255]
        map_element_fill = [0,0,0]
    else:
        map=[]
        map_fill = [255,255,255]
        map_element_fill = [0,0,0]


    return [map,map_fill,map_element_fill]

def mapGeneration_twoRooms(surface):
    wallW = 50
    gapSize = 250
    wallX = random.randint(400,surface.get_width() - 400 -wallW)
    wallH = random.randint(400,surface.get_height() - 400)
    walls = []
    walls.append({'position':[wallX,0], 'width':wallW, 'height': wallH})
    walls.append({'position':[wallX,wallH + gapSize], 'width':wallW, 'height': surface.get_height() - wallH -gapSize})
    boxes = []
    for wall in walls:
        boxes.append(drawers.cornerRecttoPoly(wall))
    return boxes


def mapGeneration_complex(surface):
    print('making map')
    noOfRooms = random.randint(3, 5)

    while noOfRooms%2 == 0:
        noOfRooms = random.randint(3, 5)

    noOfCoridoors = noOfRooms + random.randint(0, 5)
    rooms = []
    innerCon = [0] * noOfRooms
    connections = [innerCon[:] for _ in range(noOfRooms)]
    coridoors = []

    for i in range(noOfRooms):
        roomX = random.randint(200,surface.get_width() - 200)
        roomY = random.randint(200,surface.get_height() - 200)
        roomW = random.randint(300, 1000)
        roomH = random.randint(300, 1000)
        rooms.append({'position':[roomX,roomY], 'width':roomW, 'height': roomH})


    if noOfRooms > 2:
        count = 0
        for i in range(noOfCoridoors):
            if i < noOfRooms:
                sourceRoom = i
                linkRoom = random.randint(0, noOfRooms-1)
                goodlink = False
                print('attempting connection between' + str(sourceRoom) + ' and ' + str(linkRoom))
                while goodlink != True and connections[sourceRoom][linkRoom] != 0:
                    print(connections[sourceRoom][linkRoom])
                    print(connections[linkRoom][sourceRoom])
                    if linkRoom != sourceRoom:
                        goodlink = True
                    else:
                        linkRoom = random.randint(0, noOfRooms-1)
                        print('attempting connection between' + str(sourceRoom) + ' and ' + str(linkRoom))

                connections[sourceRoom][linkRoom] = 1
                connections[linkRoom][sourceRoom] = 1
                print(connections)

                cornerX = random.randint(0,rooms[sourceRoom]['width']-250)
                cornerY = random.randint(0,rooms[linkRoom]['height']-250)
                cornerX = rooms[sourceRoom]['position'][0] - rooms[sourceRoom]['width']/2 + cornerX
                cornerY = rooms[linkRoom]['position'][0] - rooms[linkRoom]['height']/2 + cornerY

                corridoorY = rooms[sourceRoom]['position'][1]
                if corridoorY > cornerY+250:
                    corridoorY = cornerY+250

                corridoorX = cornerX
                if corridoorX > rooms[linkRoom]['position'][0]:
                    corridoorX = rooms[linkRoom]['position'][0]+250

                coridoors.append({'position':[cornerX,corridoorY], 'width':250, 'height': abs(rooms[sourceRoom]['position'][1] - cornerY)})
                coridoors.append({'position':[corridoorX,cornerY+250], 'width':abs(rooms[linkRoom]['position'][0] - cornerX), 'height': 250})

            else:
                sourceRoom = random.randint(0, noOfRooms-1)
                linkRoom = random.randint(0, noOfRooms-1)
                goodlink = False
                while not goodlink:
                    if linkRoom != sourceRoom:
                        goodlink = True
                    else:
                        linkRoom = random.randint(0, noOfRooms-1)

                connections[sourceRoom][linkRoom] = 1
                connections[linkRoom][sourceRoom] = 1

                cornerX = random.randint(0,rooms[sourceRoom]['width']-250)
                cornerY = random.randint(0,rooms[linkRoom]['height']-250)
                cornerX = rooms[sourceRoom]['position'][0] - rooms[sourceRoom]['width']/2 + cornerX
                cornerY = rooms[linkRoom]['position'][0] - rooms[linkRoom]['height']/2 + cornerY

                corridoorY = rooms[sourceRoom]['position'][1]
                if corridoorY > cornerY+250:
                    corridoorY = cornerY+250

                corridoorX = cornerX
                if corridoorX > rooms[linkRoom]['position'][0]:
                    corridoorX = rooms[linkRoom]['position'][0]+250

                coridoors.append({'position':[cornerX,corridoorY], 'width':250, 'height': abs(rooms[sourceRoom]['position'][1] - cornerY)})
                coridoors.append({'position':[corridoorX,cornerY+250], 'width':abs(rooms[linkRoom]['position'][0] - cornerX), 'height': 250})


    boxes = []
    for room in rooms:
        boxes.append(drawers.centreRecttoPoly(room))
    for coridoor in coridoors:
        boxes.append(drawers.cornerRecttoPoly(coridoor))

    return boxes

def createWalls(surface,boxSize,wallWidth):
    topCorner = [int(((surface.get_width() - boxSize)/2) - wallWidth), int(((surface.get_height() - boxSize)/2) - wallWidth)]
    leftCorner = [int(((surface.get_width() - boxSize)/2) - wallWidth), int(((surface.get_height() + boxSize)/2))]
    rightCorner = [int(((surface.get_width() + boxSize)/2)), int(((surface.get_height() - boxSize)/2) - wallWidth)]


    topWall = {'position':topCorner, 'width':boxSize+(wallWidth*2), 'height': wallWidth}
    leftWall = {'position':topCorner, 'width':wallWidth, 'height': boxSize+(wallWidth*2)}
    rightWall = {'position':rightCorner, 'width':wallWidth, 'height': boxSize+(wallWidth*2)}
    bottomWall = {'position':leftCorner, 'width':boxSize+(wallWidth*2), 'height': wallWidth}

    walls = [drawers.cornerRecttoPoly(leftWall), drawers.cornerRecttoPoly(rightWall), drawers.cornerRecttoPoly(bottomWall), drawers.cornerRecttoPoly(topWall)]
    return walls

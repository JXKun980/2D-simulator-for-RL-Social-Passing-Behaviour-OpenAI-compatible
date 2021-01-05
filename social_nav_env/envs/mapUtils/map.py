from enum import Enum
import pygame
from pygame import Color
from collections import namedtuple
import math
import random
from .utils import CornerRect, CentreRect

class MapType(Enum):
    DEFAULT = 0
    TWO_ROOMS = 1
    COMPLEX = 2

'''
A convenient wrapper for the pygame module that allow easy drawing and information retrieving
'''
class Map:
    WALL_COLOR = Color(0, 0, 0)
    GROUND_COLOR = Color(255, 255, 255)

    def __init__(self, width, height, map_type, obstacle_colors=[]):
        # Class instance variables
        self.goal_size = 100
        self.polygons = None
        self.map_fill = None
        self.map_element_fill = None
        self.width = width
        self.height = height
        self.obstacle_colors = obstacle_colors + self.WALL_COLOR
        self.agent_rects = {} # dict
        self.goal_rects = {}
        self.wall_rects = []

        # Set up
        pygame.init()
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption('2D Training')

        # Generate map specific data
        if map_type == MapType.COMPLEX:
            raise NotImplementedError
            # self.polygons = mapGeneration_complex()
            # self.map_fill = self.WALL_COLOR
            # self.map_element_fill = self.GROUND_COLOR
        elif map_type == MapType.TWO_ROOMS:
            self.polygons = self.map_generation_two_rooms()
            self.map_fill = self.GROUND_COLOR
            self.map_element_fill = self.WALL_COLOR
        else:
            self.polygons =[]
            self.map_fill = self.GROUND_COLOR
            self.map_element_fill = self.WALL_COLOR

        # Put map data into pygame
        self.surface.fill(self.map_fill)
        for polygon in self.polygons:
            rect = pygame.draw.polygon(self.surface, self.map_element_fill, polygon)
            self.wall_rects.append(rect)

    def map_generation_two_rooms(self):
        wall_width = 50
        gap_height = 250
        boundry_dist = 400
        gap_y = random.randint(boundry_dist, self.height - boundry_dist - gap_height)
        wall_pos_x = random.randint(boundry_dist, self.width - boundry_dist - wall_width)

        walls = []
        walls.append(CornerRect((wall_pos_x, 0), wall_width, gap_y).to_poly())
        walls.append(CornerRect((wall_pos_x, gap_y + gap_height), wall_width, self.height - gap_height - gap_y).to_poly())
        return walls

    def createWalls(self, boxSize, wallWidth):
        topCorner = [int(((self.width - boxSize)/2) - wallWidth), int(((self.height - boxSize)/2) - wallWidth)]
        leftCorner = [int(((self.width - boxSize)/2) - wallWidth), int(((self.height + boxSize)/2))]
        rightCorner = [int(((self.width + boxSize)/2)), int(((self.height - boxSize)/2) - wallWidth)]

        topWall = CornerRect(topCorner, boxSize+(wallWidth*2), wallWidth)
        leftWall = CornerRect(topCorner, wallWidth, boxSize+(wallWidth*2))
        rightWall = CornerRect(rightCorner, wallWidth, boxSize+(wallWidth*2))
        bottomWall = CornerRect(leftCorner, boxSize+(wallWidth*2), wallWidth)

        walls = [topWall.to_poly(), leftWall.to_poly(), rightWall.to_poly(), bottomWall.to_poly()]
        return walls

    def draw_agent(self, agent, agent_color):
        # Draw a circle and a line representing the heading
        line_color = Color(255,255,255)
        radius = agent.radius
        angle = agent.theta

        endpoint_x = agent.px + (radius * math.cos(angle))
        endpoint_y = agent.py + (radius * math.sin(angle))

        rect = pygame.draw.circle(self.surface, agent_color, (agent.px, agent.py), agent.radius)
        pygame.draw.line(self.surface, line_color, (agent.px, agent.py), (endpoint_x, endpoint_y))
        # Add bounding rect to dict
        self.agent_rects[agent.id] = rect


    def draw_goal(self, agent, agent_color):
        draw_color = agent_color
        for i in range(3, 0, -1): # Draw 3 levels of increasing sized circles from (size/3 to size)
            for c in range(3): # Calculate RGB colour of each fading circle
                draw_color[c] = max(0, agent_color[c] - 10 - 50*(3-i+1))
            # Draw the circle
            rect = pygame.draw.circle(self.surface, draw_color, (agent.gx, agent.gy), self.goal_size/i)
        # Add the biggest circle's bounding rectangle to dict
        self.goal_rects[agent.id] = rect 

    def draw_line(self, start, end, color):
        return pygame.draw.line(self.surface, color, start, end)

    def has_obstacle_at(self, pos):
        c = self.surface.get_at(pos)
        return (c in self.obstacle_colors)

    def has_wall_at(self, pos):
        c = self.surface.get_at(pos)
        return (c == self.WALL_COLOR)

    def has_obstacle_within_radius(self, pos, radius):
        no_of_points = 20
        no_of_radius = 3

        if self.has_obstacle_at(pos):
            return True
        else:
            for i in range(no_of_radius):
                r = radius / (i+1)
                for j in range(no_of_points):
                    ang = (2*math.pi / no_of_points) * j
                    x = pos[0] + math.floor(r * math.cos(ang))
                    y = pos[1] + math.floor(r * math.sin(ang))
                    if self.has_obstacle_at((x,y)):
                        return True
        return False

    def rect_collides_with_anything(self, rect):
        '''
        Not used right now becuase of the above function
        '''
        # Aggregate a list of all boudning rectangles exiting on the map
        list_of_every_rect = self.agent_rects.values() + self.goal_rects.values() + self.wall_rects
        # Check if the provided rect collides
        idx = rect.collidelist(list_of_every_rect)
        return idx != -1
        
    def contains_position(self, pos):
        return (0 < pos[0] < self.width) and (0 < pos[1] < self.height)

    def has_line_of_sight_between(self, start, end):
        visible = True
        dist = math.hypot(end[0] - start[0], end[1] - start[1])
        ang = math.atan2(end[1] - start[1], end[0] - start[0])
        scan_dist = 0 # or min_scan_range
        while scan_dist <= dist:
            scan_end_x = start[0] + math.floor(scan_dist * math.cos(ang))
            scan_end_y = start[1] + math.floor(scan_dist * math.sin(ang))
            if self.has_obstacle_at((scan_end_x, scan_end_y)):
                visible = False
                break
            scan_dist += 10
        return visible
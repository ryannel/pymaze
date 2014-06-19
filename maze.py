#!/usr/bin/python

import pygame
import sys
import random
import pprint
from pygame.locals import *


class Maze:

    def __init__(self, settings, mazeLayer, solveLayer):
        self.state = 'c'  # c = creating, s = solving, r = reset

        self.settings = settings

        self._resetLayers(mazeLayer, solveLayer)
        self._calcGridSize()
        self._resetMaze();

        self.mazeArray = self._drawGrid()
        self.compass = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        pygame.draw.rect(self.sLayer, (0, 0, 255, 255), Rect(0, 0, 8, 8))
        pygame.draw.rect(self.sLayer, (255, 0, 255, 255), Rect(632, 472, 8, 8))

    def _calcGridSize(self) :
        self.cellSize = self.settings['cellSize']
        self.screenSize = self.mLayer.get_size()
        self.gridDimensions = (self.screenSize[0] / self.cellSize[0], self.screenSize[1] / self.cellSize[1])
        self.totalCells = self.gridDimensions[0] * self.gridDimensions[1]

    def _resetMaze(self) :
        self.currentCell = random.randint(0, self.totalCells - 1)
        self.visitedCells = 1
        self.cellStack = []

    def _drawGrid(self) :
        mazeArray = []

        self.cellHeight = self.cellSize[1]
        self.cellWidth = self.cellSize[0]
        self.gridHeight = self.gridDimensions[1]
        self.gridWidth = self.gridDimensions[0]
        screenWidth = self.screenSize[0]

        for y in xrange(self.gridHeight): 
            pygame.draw.line(self.mLayer, (0, 0, 0, 255), (0, y * self.cellHeight), (screenWidth, y * self.cellHeight))
            for x in xrange(self.gridWidth):
                mazeArray.append(0)
                if y == 0:
                    pygame.draw.line(self.mLayer, (0, 0, 0, 255), (x * self.cellWidth, 0), (x * self.cellWidth, screenWidth))
        return mazeArray

    def _resetLayers(self, mazeLayer, solveLayer) :
        self.mLayer = mazeLayer
        self.sLayer = solveLayer
        self.mLayer.fill((0, 0, 0, 0))
        self.sLayer.fill((0, 0, 0, 0))

    def create(self) :

        moved = False
        #while self.visitedCells < self.totalCells:  # moved == False):
        while moved == False:
            x = self.currentCell % self.gridWidth
            y = self.currentCell / self.gridWidth

            neighbors = self.getNeighbors(x, y)

            if len(neighbors) > 0:
                idx = random.randint(0, len(neighbors) - 1)
                (nidx, direction) = neighbors[idx]
                dx = x * self.cellWidth
                dy = y * self.cellHeight

                if direction & 1:
                    self.mazeArray[nidx] |= 4
                    pygame.draw.line(self.mLayer, (0, 0, 0, 0), (dx, dy + 1), (dx, dy + 7))
                elif direction & 2:
                    self.mazeArray[nidx] |= 8
                    pygame.draw.line(self.mLayer, (0, 0, 0, 0), (dx + 1, dy + 8), (dx + 7, dy + 8))
                elif direction & 4:
                    self.mazeArray[nidx] |= 1
                    pygame.draw.line(self.mLayer, (0, 0, 0, 0), (dx + 8, dy + 1), (dx + 8, dy + 7))
                elif direction & 8:
                    self.mazeArray[nidx] |= 2
                    pygame.draw.line(self.mLayer, (0, 0, 0, 0), (dx + 1, dy), (dx + 7, dy))

                self.mazeArray[self.currentCell] |= direction
                self.cellStack.append(self.currentCell)
                self.currentCell = nidx
                self.visitedCells = self.visitedCells + 1
                moved = True
            else:
                self.currentCell = self.cellStack.pop()

    def getNeighbors(self, x, y) :
        """
        Gets the Neighboring cells with all 4 walls
        Returns a cell index number and direction
        """
        neighbors = []
        for i in xrange(4):
            nx = x + self.compass[i][0]
            ny = y + self.compass[i][1]
            if nx >= 0 and ny >= 0 and nx < self.gridWidth and ny < self.gridHeight:
                if self.mazeArray[ny * self.gridWidth + nx] & 15 == 0:
                    nidx = ny * self.gridWidth + nx
                    neighbors.append((nidx, 1 << i))
        return neighbors

    def update(self):
        if self.state == 'c' :

            if self.visitedCells < self.totalCells :
                self.create()

            # IF all cells have been visted reset the maze and solve
            else :
                self._resetMaze()
                self.currentCell = 0
                self.state = 's'

        elif self.state == 's' or self.visitedCells >= self.totalCells:

            if self.currentCell == self.totalCells - 1:  # have we reached the exit?
                self.state = 'r'
                return
            moved = False
            while moved == False:
                x = self.currentCell % 80
                y = self.currentCell / 80
                neighbors = []
                directions = self.mazeArray[self.currentCell] & 15
                for i in xrange(4):
                    if directions & 1 << i > 0:
                        nx = x + self.compass[i][0]
                        ny = y + self.compass[i][1]
                        if nx >= 0 and ny >= 0 and nx < 80 and ny < 60:
                            nidx = ny * 80 + nx
                            if self.mazeArray[nidx] & 0xFF00 == 0:  # make sure there's no backtrack
                                neighbors.append((nidx, 1 << i))
                if len(neighbors) > 0:
                    idx = random.randint(0, len(neighbors) - 1)
                    (nidx, direction) = neighbors[idx]
                    dx = x * 8
                    dy = y * 8
                    if direction & 1:
                        self.mazeArray[nidx] |= 4 << 12
                    elif direction & 2:
                        self.mazeArray[nidx] |= 8 << 12
                    elif direction & 4:
                        self.mazeArray[nidx] |= 1 << 12
                    elif direction & 8:
                        self.mazeArray[nidx] |= 2 << 12
                    pygame.draw.rect(self.sLayer, (0, 255, 0, 255),
                            Rect(dx, dy, 8, 8))
                    self.mazeArray[self.currentCell] |= direction << 8
                    self.cellStack.append(self.currentCell)
                    self.currentCell = nidx
                    moved = True
                else:
                    pygame.draw.rect(self.sLayer, (255, 0, 0, 255),
                            Rect(x * 8, y * 8, 8, 8))
                    self.mazeArray[self.currentCell] &= 0xF0FF  # not a solution
                    self.currentCell = self.cellStack.pop()
        elif self.state == 'r':
            self.__init__(self.settings, self.mLayer, self.sLayer)

    def draw(self, screen):
         screen.blit(self.sLayer, (0, 0))
         screen.blit(self.mLayer, (0, 0))


class mazeHarness:

    def __init__(self, settings) :
        self.settings = settings

        pygame.init()

        screen = self.createScreen()
        background = self.generateBackground()
        mazeLayer = self.createTransparentLayer()
        solveLayer = self.createTransparentLayer()

        maze = Maze(settings, mazeLayer, solveLayer)

        self.startAnimationLoop(maze, screen, background)

    def createScreen(self) :
        screen = pygame.display.set_mode(settings['dimensions'])
        pygame.display.set_caption(settings['caption'])
        return screen

    def generateBackground(self) :
        background = pygame.Surface(settings['dimensions']).convert();
        background.fill(settings['backgroundColour'])
        return background

    def createTransparentLayer(self) :
        layer = pygame.Surface(settings['dimensions']).convert_alpha()
        layer.fill((0, 0, 0, 0)) 
        return layer

    def startAnimationLoop(self, maze, screen, background) :
        screen.blit(background, (0, 0))
        pygame.display.flip()

        clock = pygame.time.Clock()
        while 1:
            clock.tick(60)
            if self.exitListener() : return
            self.updateMaze(maze, screen, background)

    def exitListener(self) :
        for event in pygame.event.get():
            if event.type == QUIT:
                return True
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return True

    def updateMaze(self, maze, screen, background) :
        maze.update()
        screen.blit(background, (0, 0))
        maze.draw(screen)
        pygame.display.flip()

settings = {
    'backgroundColour': (224,224,224),
    'dimensions': (640, 480),
    'cellSize': (8,8),
    'caption': 'Maze',
}

if __name__ == '__main__': mazeHarness(settings);

			
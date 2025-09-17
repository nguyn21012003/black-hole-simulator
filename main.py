import numpy as np
import pygame
from numpy import cos, hypot, sin, sqrt
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_MODELVIEW,
    GL_PROJECTION,
    GL_TRIANGLE_FAN,
    glBegin,
    glBlendFunc,
    glClear,
    glColor3f,
    glEnable,
    glEnd,
    glLineWidth,
    glLoadIdentity,
    glMatrixMode,
    glPointSize,
    glVertex2f,
    glViewport,
    GL_LINE_STRIP,
    GL_BLEND,
    GL_ONE_MINUS_SRC_COLOR,
    glColor4f,
    GL_SRC_ALPHA,
    glDisable,
)
from OpenGL.GLU import gluOrtho2D
from pygame.locals import DOUBLEBUF, OPENGL, QUIT
from pygame.math import Vector2, Vector3

c = 299792458.0


class Engine:
    def __init__(self, width=800, height=600):
        self.WIDTH = width
        self.HEIGHT = height

        self.width = 1.0e11
        self.height = 7.5e10

        self.offsetX = 0.0
        self.offsetY = 0.0
        self.zoom = 1.0
        self.middleMousePressed = False
        self.lastMouseX = 0.0
        self.lastMouseY = 0.0

        pygame.init()
        pygame.display.set_mode((self.WIDTH, self.HEIGHT), DOUBLEBUF | OPENGL)
        glViewport(0, 0, self.WIDTH, self.HEIGHT)

    def run(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        left = -self.width + self.offsetX
        right = self.width + self.offsetX
        bottom = -self.height + self.offsetY
        top = self.height + self.offsetY
        gluOrtho2D(left, right, bottom, top)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


class BlackHole:
    G = 6.67430e-11

    def __init__(self, pos: Vector2, mass: float):
        self.pos = pos
        self.mass = mass
        self.r_s = 2.0 * BlackHole.G * mass / (c**2)

    def infor(self):
        return f"The black hole Sagittarius A {self.pos}, {self.r_s}"

    def drawOGL(self):
        glBegin(GL_TRIANGLE_FAN)
        glColor3f(1, 0, 0)
        glVertex2f(self.pos.x, self.pos.y)
        for i in range(101):
            angle = 2 * np.pi * i / 100
            x = self.r_s * cos(angle) + self.pos.x
            y = self.r_s * sin(angle) + self.pos.y
            glVertex2f(x, y)
        glEnd()


class Photon:

    def __init__(self, pos: Vector2, dir: Vector2):
        self.x = pos.x
        self.y = pos.y
        self.r = hypot(self.x, self.y)
        self.dir = dir
        self.phi = np.arctan2(pos.y, pos.x)

        self.dr = self.dir.x
        self.dphi = self.dir.y

        self.dr = c * cos(self.phi) + self.dir.y * sin(self.phi)
        self.dphi = (-c * sin(self.phi) + self.dir.y * cos(self.phi)) / self.r
        self.d2r = 0
        self.d2phi = 0
        self.trail = []

    def infor(self):
        print("Information of photon", self.x)

    def drawPhoton(self):
        # glPointSize(5)
        # glBegin(GL_POINTS)
        # glColor3f(1, 1, 1)
        # glVertex2f(self.x, self.y)
        # glEnd()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_COLOR)
        glLineWidth(2)

        N = len(self.trail)
        if N < 2:
            return

        glBegin(GL_LINE_STRIP)
        for i in range(N):
            alpha = i / (N - 1)
            glColor4f(1, 1, 1, max(alpha, 0.05))
            # glColor3f(1, 1, 1)
            glVertex2f(self.trail[i].x, self.trail[i].y)
        glEnd()
        glDisable(GL_BLEND)

    def step(self, r_s, dlambda):
        self.r_s = r_s
        self.dlambda = dlambda

        self.r = hypot(self.x, self.y)
        if self.r < r_s:
            return

        self.dr += self.d2r * dlambda
        self.dphi += self.d2phi * dlambda

        self.r += self.dr * dlambda
        self.phi += self.dphi * dlambda

        # self.x += self.dir.x * c * 1e0
        # self.y += self.dir.y * c * 1e0

        self.x = cos(self.phi) * self.r
        self.y = sin(self.phi) * self.r

        self.trail.append(Vector2(self.x, self.y))


def geodesics(Photon, r_s):

    r = Photon.r
    phi = Photon.phi
    dr = Photon.dr
    dphi = Photon.dphi

    Photon.dr += r * dphi**2 - (c**2 * r_s) / (2 * r**2)
    Photon.dphi += -2 * dr * dphi / r

    return


def main():
    engine = Engine()
    black_hole = BlackHole(Vector2(0, 0), 8.54e36)
    print(black_hole.infor())

    photons = []

    for y in range(-int(engine.height), int(engine.height), int(1e10)):
        photons.append(
            Photon(Vector2(-10e10, y), Vector2(0.5, 0.0)),
        )
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        engine.run()
        black_hole.drawOGL()
        for photon in photons:
            geodesics(photon, black_hole.r_s)
            photon.step(black_hole.r_s, 1)
            photon.drawPhoton()

        pygame.display.flip()

    pygame.quit()
    return None


if __name__ == "__main__":
    main()

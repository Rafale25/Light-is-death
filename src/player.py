import glm
import time
from moderngl_window.context.pyglet import Keys

class Player:
    def __init__(self, x, y, keys=Keys):
        self.pos = glm.vec2(x, y)
        self.vel = glm.vec2(0.0, 0.0)

        self.speed = 2.0
        self.dash_mult = 2.5
        self.scale = 20

        ## keys constant
        self.keys = keys

        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

        self.dash_dir = glm.vec2(0.0, 0.0)
        self.dash = False ## is space pressed
        self.is_dashing = False
        # self.cooldown

        self.dash_stamina = 1.0 #0.0 -> 1.0

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y

    def update(self):
        ## Dash
        if self.dash:
            self.is_dashing = True
        else:
            self.is_dashing = False

        if self.is_dashing:
            self.dash_stamina -= 0.01

        if self.dash_stamina <= 0.0:
            self.dash_stamina = 0.0
            self.is_dashing = False
        self.dash_stamina = min(1.0, self.dash_stamina + 0.005)

        if not self.is_dashing:
            ## ZQSD Movements
            self.vel.x = 0
            self.vel.y = 0

            if self.move_up:
                self.vel.y += 1.0
            if self.move_down:
                self.vel.y -= 1.0
            if self.move_left:
                self.vel.x -= 1.0
            if self.move_right:
                self.vel.x += 1.0


        ## Apply vel ...
        if glm.length(self.vel) > 0.001:
            self.vel = glm.normalize(self.vel)

        if self.dash:
            self.vel *= self.dash_mult

        self.pos += self.vel

    def key_input(self, key, action, modifiers):
        ## Up
        if key == self.keys.Z:
            if action == self.keys.ACTION_PRESS:
                self.move_up = True
            elif action == self.keys.ACTION_RELEASE:
                self.move_up = False

        ## Right
        if key == self.keys.D:
            if action == self.keys.ACTION_PRESS:
                self.move_right = True
            elif action == self.keys.ACTION_RELEASE:
                self.move_right = False

        ## Left
        if key == self.keys.Q:
            if action == self.keys.ACTION_PRESS:
                self.move_left = True
            elif action == self.keys.ACTION_RELEASE:
                self.move_left = False

        ## Down
        if key == self.keys.S:
            if action == self.keys.ACTION_PRESS:
                self.move_down = True
            elif action == self.keys.ACTION_RELEASE:
                self.move_down = False

        ## Dash
        elif key == self.keys.SPACE:
            if action == self.keys.ACTION_PRESS:
                self.dash = True
            elif action == self.keys.ACTION_RELEASE:
                self.dash = False

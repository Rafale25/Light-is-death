# import glm
from pyglet.math import Vec2
import time
from moderngl_window.context.pyglet import Keys

ACTION_PRESS = 1
ACTION_RELEASE = 0

class Player:
    def __init__(self, x, y, keys=Keys):
        self.pos = Vec2(x, y)
        self.vel = Vec2(0.0, 0.0)

        self.speed = 4.0
        self.dash_mult = 2.2
        self.scale = 15

        ## keys constant
        self.keys = keys

        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

        self.dash_dir = Vec2(0.0, 0.0)
        self.dash = False ## is space pressed
        self.is_dashing = False ## is character currently dashing

        self.max_dash_cooldown = 0.75 #seconds
        self.dash_cooldown = self.max_dash_cooldown

        self.dash_stamina = 1.0 #0.0 -> 1.0

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y

    def update(self, delta_time):
        ### Dash
        ## if dash pressed && cooldown finished && is moving
        if self.dash and self.dash_cooldown <= 0 and self.vel.mag > 0:
            self.is_dashing = True

        ## update dash_stamina
        if self.is_dashing:
            self.dash_cooldown = self.max_dash_cooldown
            self.dash_stamina = max(0, self.dash_stamina - 0.012)
        ## update cooldown if not dashing
        else:
            self.dash_stamina = 1.0
            self.dash_cooldown = max(0, self.dash_cooldown - delta_time)

        ## stop dash if runs out of stamina
        ## if dash button not pressed, stop dash
        # if (self.dash_stamina <= 0) or (not self.dash and self.is_dashing):
        if not self.dash and self.is_dashing:
            self.is_dashing = False

        # print(self.dash, self.is_dashing)
        print(self.dash_cooldown)

        if not self.is_dashing:
            ## ZQSD Movements
            self.vel = Vec2(0, 0)

            if self.move_up:
                self.vel += (0, 1)
            if self.move_down:
                self.vel -= (0, 1)
            if self.move_left:
                self.vel -= (1, 0)
            if self.move_right:
                self.vel += (1, 0)

        ## Apply vel ...
        if self.vel.mag > 0.001:
            self.vel = self.vel.normalize()

        if self.is_dashing:
            self.vel *= (self.dash_mult,self.dash_mult)

        self.pos += self.vel * (self.speed,self.speed)

    def key_input(self, key, action, modifiers):
        ## Up
        if key == self.keys.Z:
            if action == ACTION_PRESS:
                self.move_up = True
            elif action == ACTION_RELEASE:
                self.move_up = False

        ## Right
        if key == self.keys.D:
            if action == ACTION_PRESS:
                self.move_right = True
            elif action == ACTION_RELEASE:
                self.move_right = False

        ## Left
        if key == self.keys.Q:
            if action == ACTION_PRESS:
                self.move_left = True
            elif action == ACTION_RELEASE:
                self.move_left = False

        ## Down
        if key == self.keys.S:
            if action == ACTION_PRESS:
                self.move_down = True
            elif action == ACTION_RELEASE:
                self.move_down = False

        ## Dash
        elif key == self.keys.SPACE:
            if action == ACTION_PRESS:
                self.dash = True
            elif action == ACTION_RELEASE:
                self.dash = False

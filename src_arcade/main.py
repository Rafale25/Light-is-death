#! /usr/bin/python3

import arcade

from random import randint, uniform
from math import cos, sin, atan2, pi, tau, radians
from array import array
from pathlib import Path

from pyglet.math import Mat4

from utils import *
from player import Player
from shapes import ShapeBuilder

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Global Game-Jam 2022"

ASSETS_PATH = Path(__file__).parent.parent.resolve() / "resources"

class Shape:
    ## to have a concret object for moving shapes instead of a list
    def __init__(self, x, y, angle, scale, dir, speed, shape):
        self.x = x
        self.y = y
        self.angle = angle
        self.scale = scale
        self.dir = dir
        self.speed = speed
        self.shape = shape

    def update(self):
        self.x += cos(self.dir) * self.speed
        self.y += sin(self.dir) * self.speed

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color((0, 0, 0))
        self.set_vsync(True)
        self.set_update_rate(1.0 / 60.0)

    def setup(self):
        self.projection = arcade.create_orthogonal_projection(0, self.width, 0, self.height)
        # self.projection = arcade.create_orthogonal_projection(-self.width*2, self.width*4, -self.height*2, self.height*4)

        self.texture = self.ctx.texture(size=self.get_framebuffer_size(), components=4)
        self.fbo = self.ctx.framebuffer(
            color_attachments=self.texture
        )

        self.program = {
            "SHAPE": self.ctx.load_program(
                vertex_shader=f'{ASSETS_PATH}/shape2.vert',
                fragment_shader=f'{ASSETS_PATH}/shape2.frag'),
        }
        self.program['SHAPE']['u_texture'] = 0

        self.quad = arcade.gl.geometry.quad_2d(size=(1, 1), pos=(0, 0))
        self.disk = self.ctx.geometry([arcade.gl.BufferDescription(
            self.ctx.buffer(data=array('f', ShapeBuilder.disk())),
            '2f',
            ['in_vert'],
        )], mode=self.ctx.TRIANGLE_FAN)


        ## Player
        self.player = Player(x=self.width/2, y=self.height/2)
        self.max_shapes = 59

        ## Shapes
        self.max_time_next_shape = 1
        self.time_next_shape = self.max_time_next_shape

        ## 0 == cube; 1 == disk
        self.shapes = []

        ## Game Logic
        self.started = False

    def generate_shapes(self, n=1):
        for i in range(n):
            shape = randint(0, 1)

            ## coming offscreen to somewhere into the screen
            x, y = random_uniform_vec2()
            x = (x * self.width) + self.width/2
            y = (y * self.width) + self.height/2

            ## point in screen to get direction
            px, py = uniform(0, self.width), uniform(0, self.height)
            dx, dy = px - x, py - y
            dir = atan2(dy, dx)

            ## random
            # x = uniform(100, self.width-100)
            # y = uniform(100, self.height-100)
            # dir = uniform(0, tau)

            speed = uniform(0.3, 1.2) * 3
            angle = uniform(0, tau)
            scale = uniform(200, self.width/3)

            yield Shape(x, y, angle, scale, dir, speed, shape)

        if n > 1:
            self.generate_shapes(n=n-1)

    def render_shapes(self):
        self.program['SHAPE']['u_projectionMatrix'] = self.projection

        for i, shape in enumerate(self.shapes):
            m = toMatrix(x=shape.x, y=shape.y, angle=shape.angle, scale=shape.scale)
            self.program['SHAPE']['u_modelMatrix'] = m
            if shape.shape == 0:
                self.quad.render(program=self.program['SHAPE'])
            else:
                self.disk.render(program=self.program['SHAPE'])

            self.ctx.flush()

    def on_draw(self):
        self.clear()

        self.ctx.disable(self.ctx.DEPTH_TEST)

        self.fbo.use()
        self.fbo.clear((0, 0, 0, 255))
        self.texture.use(unit=0)

        self.render_shapes()

        self.ctx.copy_framebuffer(src=self.fbo, dst=self.ctx.screen)
        self.ctx.screen.use()

        ## Dead if on whiteColor or out of screen
        pixel_color = arcade.get_pixel(*self.player.pos)
        if (not self.player.is_dashing and pixel_color[0] > 128) or\
                not (0 < self.player.x < self.width and 0 < self.player.y < self.height):
            print("DEAD")
            self.setup()

        arcade.draw_rectangle_filled(center_x=self.player.x, center_y=self.player.y, width=self.player.scale, height=self.player.scale,
            color=(180, 0, 0) if self.player.dash_cooldown > 0 else (0, 200, 0))
        arcade.draw_rectangle_filled(center_x=self.player.x, center_y=self.player.y+20, height=5,
            color=(0, 255, 255) if self.player.dash_cooldown > 0 else (0, 255, 0),
            width=map_range(self.player.dash_cooldown, 0, self.player.max_dash_cooldown, 40, 0))

    def on_update(self, delta_time):
        ## do not do game logic if game not started
        if not self.started: return


        self.player.update(delta_time)

        #TODO: better would be to check if a shape is going to be offscreen
        def isOffScreen(shape, margin=self.width * 3/4):
            return shape.x < -margin - shape.scale or\
                shape.x > margin + self.width + shape.scale or\
                shape.y < -margin - shape.scale or\
                shape.y > margin + self.height + shape.scale

        ## Remove shapes that are off bounds
        self.shapes[:] = (x for x in self.shapes if not isOffScreen(x))

        self.time_next_shape -= delta_time
        if self.time_next_shape <= 0.0:

            if len(self.shapes) < self.max_shapes:
                self.shapes.extend(self.generate_shapes(n=1))
                self.time_next_shape = self.max_time_next_shape

        for shape in self.shapes:
            shape.update()


    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.ESCAPE:
            self.close()

        self.player.key_input(key, 1, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        self.player.key_input(key, 0, key_modifiers)


if __name__ == "__main__":
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

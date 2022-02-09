#! /usr/bin/python3

import pyglet
import arcade

from random import randint, uniform
from math import cos, sin, atan2, pi, tau, radians
from array import array
from pathlib import Path
import time

from pyglet.math import Mat4

from utils import *
from player import Player
from shapes import ShapeBuilder
from particles import ParticleSystem

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Global Game-Jam 2022"

ASSETS_PATH = Path(__file__).parent.parent.resolve() / "resources"


STATE_START = 0
STATE_PLAYING = 1
STATE_OVER = 2

vert=\
"""
#version 330

uniform mat4 u_projectionMatrix;
uniform mat4 u_modelMatrix;

in vec2 in_vert;

void main() {
    gl_Position = u_projectionMatrix * u_modelMatrix * vec4(in_vert, 0.0, 1.0);
}

"""

frag=\
"""
#version 430

out vec4 f_color;

uniform sampler2D u_texture;

void main() {
    ivec2 uv = ivec2(gl_FragCoord.xy);
    vec3 texel_color = texelFetch(u_texture, uv, 0).rgb;

    vec3 color = vec3(1.0, 1.0, 1.0);

    if (texel_color.r > 0.5) {
        color = vec3(0.0, 0.0, 0.0);
    }

    f_color = vec4(color, 1.0);
}
"""

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color((0, 0, 0))
        self.set_vsync(True)
        self.set_update_rate(1.0 / 60.0)
        self.set_fullscreen(True)

    def setup(self):
        self.projection = arcade.create_orthogonal_projection(0, self.width, 0, self.height)

        self.texture = self.ctx.texture(size=self.get_framebuffer_size(), components=4)
        self.fbo = self.ctx.framebuffer(
            color_attachments=self.texture
        )

        self.program = {
            "SHAPE": self.ctx.program(
                vertex_shader=vert,
                fragment_shader=frag)
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

        ## Dash particules trail
        self.trailSystem = ParticleSystem()

        ## Game Logic
        # self.started = False
        self.game_state = STATE_START

        ## HighScore
        self.time_since_start = 0.0

        self.media_player = pyglet.media.Player()
        self.media_player.queue(pyglet.media.load("Bad-Apple.flv"))
        self.media_player.seek_next_frame()

        self.tick = 1

    def draw_start(self):
        self.fbo.use()
        self.fbo.clear((0, 0, 0, 255))

        arcade.draw_text(
            text="Press SPACE to start !!",
            bold=True,
            font_size=42,
            start_x=self.width/2,
            start_y=self.height/2,
            anchor_x="center",
            anchor_y="center",
            rotation=sin(time.time() * 3) * 10)

        self.ctx.flush()

        self.texture.use(unit=0)

        self.ctx.copy_framebuffer(src=self.fbo, dst=self.ctx.screen)
        self.ctx.screen.use()

    def draw_over(self):
        arcade.draw_text(
            text="Game Over :(",
            bold=True,
            font_size=42,
            start_x=self.width/2,
            start_y=self.height/2,
            anchor_x="center",
            anchor_y="center",
            rotation=sin(time.time() * 3) * 10)

        arcade.draw_text(
            text="HighScore: {}".format(round(self.time_since_start)),
            bold=True,
            font_size=18,
            start_x=self.width/2,
            start_y=self.height/2 + 150,
            anchor_x="center",
            anchor_y="center",
            rotation=cos(time.time() * 3) * 10)

    def on_draw(self):
        self.clear()
        self.ctx.disable(self.ctx.DEPTH_TEST)

        if self.game_state == STATE_START:
            self.draw_start()
            return

        if self.game_state == STATE_OVER:
            self.draw_over()
            return


        self.fbo.use()
        self.fbo.clear((0, 0, 0, 255))

        ## drawing text here so it can kills player >:p
        ## draw HighScore
        arcade.draw_text(
            text="HighScore: {}".format(round(self.time_since_start)),
            bold=True,
            font_size=22,
            start_x=self.width/2,
            start_y=self.height - 35,
            anchor_x="center",
            anchor_y="center")
        self.ctx.flush()

        ## tutorial text
        if self.time_since_start < 3:
            arcade.draw_text(
                text="Light kills you :)",
                bold=True,
                font_size=22,
                start_x=self.width/2,
                start_y=self.height/4,
                anchor_x="center",
                anchor_y="center")
        if 3 < self.time_since_start < 5:
            arcade.draw_text(
                text="ZQSD for moving, Space to dash",
                bold=True,
                font_size=22,
                multiline=True,
                start_x=self.width/2,
                start_y=self.height/4,
                anchor_x="center",
                anchor_y="center")
        if 5 < self.time_since_start < 7:
            arcade.draw_text(
                text="You are invicible while dashing",
                bold=True,
                font_size=22,
                multiline=True,
                start_x=self.width/2,
                start_y=self.height/4,
                anchor_x="center",
                anchor_y="center")

        self.texture.use(unit=0)

        ## draw here
        self.tick -= 1
        if self.tick <= 0:
            self.tick = 3
            self.media_player.seek_next_frame()

        with self.ctx.pyglet_rendering():
            self.ctx.disable(self.ctx.BLEND)
            self.media_player.texture.blit(
                0,
                0,
                width=self.width,
                height=self.height,
            )

        self.ctx.copy_framebuffer(src=self.fbo, dst=self.ctx.screen)
        self.ctx.screen.use()

        ## Dead if on whiteColor or out of screen
        # pixel_color = arcade.get_pixel(*self.player.pos)
        # if (not self.player.is_dashing and pixel_color[0] > 128) or\
        #         not (0 < self.player.x < self.width and 0 < self.player.y < self.height):
        #     self.game_state = STATE_OVER
            # print("DEAD")

        ## draw trail particles (trailSystem)
        for p in self.trailSystem.particles:
            arcade.draw_rectangle_filled(p.x, p.y, width=3, height=3, color=(0, 255, 255, map_range(p.lifetime, 0, 1, 0, 255)))

        ## draw player
        if self.player.is_dashing:
            arcade.draw_rectangle_filled(center_x=self.player.x, center_y=self.player.y, width=self.player.scale, height=self.player.scale,
                color=(0, 255, 255))
        else:
            arcade.draw_rectangle_filled(center_x=self.player.x, center_y=self.player.y, width=self.player.scale, height=self.player.scale,
                color=(180, 0, 0) if self.player.dash_cooldown > 0 else (0, 180, 0))

        ## draw player's dash cooldown
        if self.player.dash_cooldown > 0:
            arcade.draw_rectangle_filled(center_x=self.player.x, center_y=self.player.y+20, height=5,
                color=(0, 255, 255),
                width=map_range(self.player.dash_cooldown, 0, self.player.max_dash_cooldown, 40, 0))

    def isOffScreen(self, shape, margin=1000):
        margin=self.width * 3/4
        #TODO: better would be to check if a shape is going to be offscreen
        return shape.x < -margin - shape.scale or\
            shape.x > margin + self.width + shape.scale or\
            shape.y < -margin - shape.scale or\
            shape.y > margin + self.height + shape.scale

    def on_update(self, delta_time):

        ## do not do game logic if game not started
        if self.game_state == STATE_START:
            pass

        if self.game_state != STATE_PLAYING: return

        ## add deltatime because highscore is the time you survived
        self.time_since_start += delta_time

        self.player.update(delta_time)
        if self.player.is_dashing:
            self.trailSystem.spawn(*(self.player.pos + random_uniform_vec2()*(5,5)))

        self.trailSystem.update(delta_time)

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.ESCAPE:
            self.close()

        if key == arcade.key.SPACE:
            if self.game_state == STATE_START:
                self.game_state = STATE_PLAYING

            elif self.game_state == STATE_OVER:
                self.setup()

        self.player.key_input(key, 1, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        self.player.key_input(key, 0, key_modifiers)


if __name__ == "__main__":
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

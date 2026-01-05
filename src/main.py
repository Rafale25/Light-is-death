#! /usr/bin/python3

import arcade
import arcade.gui
from arcade.types import Color
from random import randint, uniform
from math import cos, sin, atan2, tau
from array import array
from pathlib import Path
import time
from pyglet.math import Mat4
from OpenGL.GL import *
from utils import *
from player import Player
from shapes import ShapeBuilder
from particles import ParticleSystem

import globals

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
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

    def update(self, delta_time):
        self.x += cos(self.dir) * self.speed * delta_time
        self.y += sin(self.dir) * self.speed * delta_time

STATE_START = 0
STATE_PLAYING = 1
STATE_OVER = 2

vert=\
"""
#version 330 core

uniform mat4 u_projectionMatrix;
uniform mat4 u_modelMatrix;

in vec2 in_vert;

void main() {
    gl_Position = u_projectionMatrix * u_modelMatrix * vec4(in_vert, 0.0, 1.0);
}

"""

frag=\
"""
#version 330 core

out vec4 f_color;

void main() {
    ivec2 uv = ivec2(gl_FragCoord.xy);
    vec3 color = vec3(1.0, 1.0, 1.0);
    f_color = vec4(color, 1.0);
}
"""

class MenuView(arcade.View):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

        self.ui = arcade.gui.UIManager()
        self.anchor = self.ui.add(arcade.gui.UIAnchorLayout())

        self.btn_style = {
            # You should provide a style for each widget state
            "normal": arcade.gui.UIFlatButton.UIStyle(
                font_color=arcade.color.WHITE,
                bg=Color(255, 255, 255, 2),
                font_size=24,
            ), # use default values for `normal` state
            "hover": arcade.gui.UIFlatButton.UIStyle(
                font_color=arcade.color.WHITE,
                bg=Color(255, 255, 255, 40),
                font_size=24,
            ),
            "press": arcade.gui.UIFlatButton.UIStyle(
                font_color=arcade.color.WHITE,
                bg=Color(255, 255, 255, 70),
                font_size=24,
            ),
            "disabled": arcade.gui.UIFlatButton.UIStyle(
                font_color=arcade.color.GRAY,
                bg=arcade.color.TRANSPARENT_BLACK,
                font_size=24,
            )
        }

        self.btn_style_selected = self.btn_style.copy()
        self.btn_style_selected["normal"] = arcade.gui.UIFlatButton.UIStyle(
                                        font_color=arcade.color.WHITE,
                                        bg=Color(255, 255, 255, 20),
                                        font_size=24)

        self.btn_quit = self.anchor.add(
            arcade.gui.UIFlatButton(text="Quit", width=200, style=self.btn_style),
            align_x=0,
            align_y=self.window.height * -0.1,
        )

        self.btn_qwerty = self.anchor.add(
            arcade.gui.UIFlatButton(text="QWERTY", width=200, style=self.btn_style),
            align_x=-200,
            align_y=self.window.height * 0.1,
        )

        self.btn_azerty = self.anchor.add(
            arcade.gui.UIFlatButton(text="AZERTY", width=200, style=self.btn_style),
            align_x=200,
            align_y=self.window.height * 0.1,
        )

        self.set_keyboard(globals.keyboard)

        @self.btn_quit.event("on_click")
        def btn_quit_on_click(event):
            self.window.close()

        @self.btn_qwerty.event("on_click")
        def btn_qwerty_on_click(event):
            self.set_keyboard('qwerty')

        @self.btn_azerty.event("on_click")
        def btn_azerty_on_click(event):
            self.set_keyboard('azerty')

    def set_keyboard(self, keyboard: str):
        if keyboard == 'qwerty':
            self.btn_qwerty.style = self.btn_style_selected
            self.btn_azerty.style = self.btn_style
        elif keyboard == 'azerty':
            self.btn_azerty.style = self.btn_style_selected
            self.btn_qwerty.style = self.btn_style
        else:
            print("Invalid keyboard")
            return

        globals.keyboard = keyboard
        self.ui.trigger_render()

    def on_show_view(self):
        self.ui.enable()
        arcade.set_background_color(arcade.color.BLACK)
        self.window.set_mouse_visible(True)

    def on_hide_view(self):
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.ui.draw()

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.ESCAPE:
            self.window.set_mouse_visible(False)
            self.window.show_view(self.parent_view)

class Game(arcade.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup()

    def setup(self):
        self.projection = Mat4.orthogonal_projection(0, self.width, 0, self.height, -1, 1)

        self.program = {
            "SHAPE":  self.window.ctx.program(
                vertex_shader=vert,
                fragment_shader=frag)
        }

        self.quad = arcade.gl.geometry.quad_2d(size=(1, 1), pos=(0, 0))
        self.disk =  self.window.ctx.geometry([arcade.gl.BufferDescription(
             self.window.ctx.buffer(data=array('f', ShapeBuilder.disk())),
            '2f',
            ['in_vert'],
        )], mode= self.window.ctx.TRIANGLE_FAN)


        ## Player
        self.player = Player(x=self.width/2, y=self.height/2)

        ## Dash particules trail
        self.trailSystem = ParticleSystem()

        ## Shapes
        self.max_time_next_shape = 1
        self.time_next_shape = self.max_time_next_shape

        ## 0 == cube; 1 == disk
        self.shapes = []
        self.max_shapes = 10
        self.max_cooldown_increase_max_shapes = 2.0 #seconds
        self.cooldown_increase_max_shapes = self.max_cooldown_increase_max_shapes

        ## Game Logic
        # self.started = False
        self.game_state = STATE_START

        ## HighScore
        self.time_since_start = 0.0

        self.text_start = arcade.Text(
            text="Press SPACE to start !!",
            x=self.width/2,
            y=self.height/2,
            font_size=42,
            bold=True,
            anchor_x="center",
            anchor_y="center"
        )

        self.text_tutorial = arcade.Text(
            text="",
            x=self.width/2,
            y=self.height/4,
            bold=True,
            font_size=22,
            anchor_x="center",
            anchor_y="center"
        )

        self.text_highscore = arcade.Text(
            text="HighScore: 0",
            x=self.width/2,
            y=self.height - 35,
            font_size=22,
            bold=True,
            anchor_x="center",
            anchor_y="center"
        )

        self.text_gameover = arcade.Text(
            text="Game Over :(",
            x=self.width/2,
            y=self.height/2,
            font_size=42,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )

        self.text_gameover_highscore = arcade.Text(
            text="HighScore: {}".format(round(self.time_since_start)),
            x=self.width/2,
            y=self.height/2 + 150,
            font_size=18,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )

    def generate_shapes(self, n=1):
        for _ in range(n):
            shape = randint(0, 1)

            ## coming offscreen to somewhere into the screen
            x, y = random_uniform_vec2()
            x = (x * self.width) + self.width/2
            y = (y * self.width) + self.height/2

            ## point in screen to get direction
            px, py = uniform(0, self.width), uniform(0, self.height)
            dx, dy = px - x, py - y
            dir = atan2(dy, dx)

            speed = uniform(35, 120)
            angle = uniform(0, tau)
            scale = uniform(200, self.width/3)

            yield Shape(x, y, angle, scale, dir, speed, shape)

        # if n > 1:
        #     self.generate_shapes(n=n-1)

    def render_shapes(self):
        glClear(GL_STENCIL_BUFFER_BIT)
        glStencilMask(1)
        glEnable(GL_COLOR_LOGIC_OP)
        glLogicOp(GL_INVERT)

        self.program['SHAPE']['u_projectionMatrix'] = self.projection

        for i, shape in enumerate(self.shapes):
            m = toMatrix(x=shape.x, y=shape.y, angle=shape.angle, scale=shape.scale)
            self.program['SHAPE']['u_modelMatrix'] = m
            if shape.shape == 0:
                self.quad.render(program=self.program['SHAPE'])
            else:
                self.disk.render(program=self.program['SHAPE'])

        # self.ctx.flush()
        glDisable(GL_COLOR_LOGIC_OP)

    def draw_start(self):
        self.text_start.rotation = sin(time.time() * 3) * 10
        self.text_start.draw()

        self.window.ctx.flush()
        self.render_shapes()

    def draw_over(self):
        self.text_gameover.rotation = sin(time.time() * 3) * 10
        self.text_gameover.draw()

        self.text_gameover_highscore.text = "HighScore: {}".format(round(self.time_since_start))
        self.text_gameover_highscore.rotation = cos(time.time() * 3) * 10
        self.text_gameover_highscore.draw()

    def on_draw(self):
        self.clear()
        self.window.ctx.disable(self.window.ctx.DEPTH_TEST)

        if self.game_state == STATE_START:
            self.draw_start()
            return

        if self.game_state == STATE_OVER:
            self.draw_over()
            return

        ## drawing text here so it can kills player >:p
        ## draw HighScore
        self.text_highscore.text = "HighScore: {}".format(round(self.time_since_start))
        self.text_highscore.draw()

        ## tutorial text
        if self.time_since_start < 3:
            self.text_tutorial.text = "Light kills you :)"
        elif self.time_since_start < 5:
            self.text_tutorial.text = ("WASD" if globals.keyboard == 'qwerty' else "ZQSD") + " for moving, Space to dash"
        elif self.time_since_start < 7:
            self.text_tutorial.text = "You are invicible while dashing"

        if self.time_since_start < 7:
            self.text_tutorial.draw()

        self.window.ctx.flush()

        glClear(GL_STENCIL_BUFFER_BIT)
        glStencilMask(1)
        glEnable(GL_COLOR_LOGIC_OP)
        glLogicOp(GL_INVERT)

        self.render_shapes()

        glDisable(GL_COLOR_LOGIC_OP)

        ## Dead if on whiteColor or out of screen
        pixel_color = arcade.get_pixel(*self.player.pos)
        if (not self.player.is_dashing and pixel_color[0] > 128) or\
                not (0 < self.player.x < self.width and 0 < self.player.y < self.height):
            self.game_state = STATE_OVER
            # print("DEAD")

        ## draw trail particles (trailSystem)
        for p in self.trailSystem.particles:
            alpha = max(0, min(255, map_range(p.lifetime, 0, 1, 0, 255)))
            arcade.draw_point(p.x, p.y, color=(0, 255, 255, alpha), size=3)

        ## draw player
        if self.player.is_dashing:
            arcade.draw_point(x=self.player.x, y=self.player.y, color=(0, 255, 255), size=self.player.scale)

        else:
            arcade.draw_point(x=self.player.x, y=self.player.y, color=(180, 0, 0) if self.player.dash_cooldown > 0 else (0, 180, 0), size=self.player.scale)

        ## draw player's dash cooldown
        if self.player.dash_cooldown > 0:
            rect = arcade.XYWH(self.player.x, self.player.y+20, map_range(self.player.dash_cooldown, 0, self.player.max_dash_cooldown, 40, 0), 5)
            arcade.draw_rect_filled(rect, color=(0, 255, 255))

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
            self.shapes[:] = (x for x in self.shapes if not self.isOffScreen(x))

            self.time_next_shape -= delta_time
            if self.time_next_shape <= 0.0:

                if len(self.shapes) < 10:
                    self.shapes.extend(self.generate_shapes(n=2))
                    self.time_next_shape = self.max_time_next_shape

            for shape in self.shapes:
                shape.update(delta_time)

        if self.game_state != STATE_PLAYING: return

        ## add deltatime because highscore is the time you survived
        self.time_since_start += delta_time

        self.cooldown_increase_max_shapes -= delta_time
        if self.cooldown_increase_max_shapes <= 0.0:
            self.cooldown_increase_max_shapes = self.max_cooldown_increase_max_shapes
            self.max_shapes += 1

        self.player.update(delta_time)
        if self.player.is_dashing:
            self.trailSystem.spawn(*(self.player.pos + random_uniform_vec2() * 5.0))

        self.trailSystem.update(delta_time)

        ## Remove shapes that are off bounds
        self.shapes[:] = (x for x in self.shapes if not self.isOffScreen(x))

        self.time_next_shape -= delta_time
        if self.time_next_shape <= 0.0:

            if len(self.shapes) < self.max_shapes:
                self.shapes.extend(self.generate_shapes(n=1))
                self.time_next_shape = self.max_time_next_shape

        for shape in self.shapes:
            shape.update(delta_time)

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView(self))

        if key == arcade.key.SPACE:
            if self.game_state == STATE_START:
                self.game_state = STATE_PLAYING
                self.shapes[:] = []

            elif self.game_state == STATE_OVER:
                self.setup()

        self.player.key_input(key, 1, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        self.player.key_input(key, 0, key_modifiers)


if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True, vsync=True)
    window.set_minimum_size(720, 480)
    window.set_mouse_visible(False)
    # self.set_update_rate(1.0 / 60.0)

    game_view = Game()
    window.show_view(game_view)

    arcade.run()

# pyinstaller --onefile --noconsole --add-data "resources;resources" ./src/main.py

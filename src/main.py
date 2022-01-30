#! /usr/bin/python3

import moderngl
import imgui
import glm

import moderngl_window
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from moderngl_window.opengl.vao import VAO

from random import randint, uniform
from math import cos, sin, atan2, pi, tau, radians
from array import array

from utils import *

from fps_counter import FpsCounter
from shapes import ShapeBuilder
from player import Player

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

class MyWindow(moderngl_window.WindowConfig):
    title = 'Global Game-jam 2022'
    gl_version = (4, 3)
    window_size = (1920, 1080)
    fullscreen = False
    resizable = False
    # samples = 8
    vsync = True
    resource_dir = './resources'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        imgui.create_context()
        self.imgui = ModernglWindowRenderer(self.wnd)

        self.query_debug_values = {}
        self.query = self.ctx.query(samples=False, time=True)
        self.fps_counter = FpsCounter()

        self.projection = glm.ortho(0, self.wnd.width, 0, self.wnd.height)
        # self.projection = glm.ortho(-self.wnd.width*2, self.wnd.width*4, -self.wnd.height*2, self.wnd.height*4)

        self.texture = self.ctx.texture(self.wnd.buffer_size, 4)
        self.fbo = self.ctx.framebuffer(
            color_attachments=self.texture
        )

        self.program = {
            "SHAPE": self.load_program(
                vertex_shader='./shape.vert',
                fragment_shader='./shape.frag'),
            "PLAYER": self.load_program(
                vertex_shader='./player.vert',
                fragment_shader='./player.frag'),
        }

        vertices = array('f', ShapeBuilder.quad())
        self.vao_quad = VAO(mode=moderngl.TRIANGLES)
        self.vao_quad.buffer(self.ctx.buffer(vertices), '2f', ['v_vert'])

        vertices = array('f', ShapeBuilder.disk())
        self.vao_disk = VAO(mode=moderngl.TRIANGLE_FAN)
        self.vao_disk.buffer(self.ctx.buffer(vertices), '2f', ['v_vert'])

        ## game
        self.player = Player(x=self.wnd.width/2, y=self.wnd.height/2)
        
        self.max_shapes = 200

        ## 0 == cube; 1 == disk
        self.shapes = []

    def generate_shapes(self, n):
        for i in range(n):
            shape = randint(0, 1)

            ## coming offscreen to somewhere into the screen
            x, y = random_uniform_vec2() * uniform(self.wnd.width, self.wnd.width*1.5)
            x += self.wnd.width/2
            y += self.wnd.height/2

            ## point in screen to get direction
            px, py = uniform(0, self.wnd.width), uniform(0, self.wnd.height)
            dx, dy = px - x, py - y
            dir = atan2(dy, dx)

            ## random
            # x = uniform(100, self.wnd.width-100)
            # y = uniform(100, self.wnd.height-100)
            # dir = uniform(0, tau)

            speed = uniform(0.3, 1.2) * 10
            angle = uniform(0, tau)
            scale = uniform(200, self.wnd.width/3)

            yield Shape(x, y, angle, scale, dir, speed, shape)

        if n > 1:
            self.generate_shapes(n=n-1)

    def update_uniforms(self, frametime):
        for str, program in self.program.items():
            program['u_projectionMatrix'].write(self.projection)

        self.program['SHAPE']['u_texture'] = 0

    def update(self, time_since_start, frametime):
        self.fps_counter.update(frametime)
        self.update_uniforms(frametime)
        self.player.update()

        #TODO: better would be to check if a shape is going to be offscreen
        def isOffScreen(shape, margin=self.wnd.width*1.1):
            return shape.x < -margin - shape.scale or\
                shape.x > margin + self.wnd.width + shape.scale or\
                shape.y < -margin - shape.scale or\
                shape.y > margin + self.wnd.height + shape.scale
            # if ok:
            #     print(f"OFFFSCREN !! {shape.x} {shape.y}")
            # return ok

        ## Remove shapes that are off bounds
        self.shapes[:] = (x for x in self.shapes if not isOffScreen(x))

        if len(self.shapes) < self.max_shapes:
            self.shapes.extend(self.generate_shapes(n=1))

        for shape in self.shapes:
            shape.update()



    def render_shapes(self):
        for i, shape in enumerate(self.shapes):
            m = toMatrix(x=shape.x, y=shape.y, angle=shape.angle, scale=shape.scale)
            self.program['SHAPE']['u_modelMatrix'].write(m)

            with self.query:
                if shape.shape == 0:
                    self.vao_quad.render(program=self.program['SHAPE'])
                else:
                    self.vao_disk.render(program=self.program['SHAPE'])
            self.query_debug_values[f'render {i}'] = self.query.elapsed * 10e-7

    def render(self, time_since_start, frametime):
        self.update(time_since_start, frametime)

        self.ctx.disable(moderngl.DEPTH_TEST) # disables wireframe and depth_test for imgui
        # self.ctx.clear(0, 0, 0, 1)

        ## Black & White
        self.fbo.clear(1, 1, 1, 1)
        self.fbo.use()
        self.texture.use(location=0)
        self.render_shapes()

        ## Player
        self.program['PLAYER']['u_modelMatrix'].write(
            toMatrix(x=self.player.x, y=self.player.y, scale=self.player.scale))
        self.vao_quad.render(program=self.program['PLAYER'])

        self.ctx.copy_framebuffer(src=self.fbo, dst=self.ctx.screen)

        self.ctx.screen.use()

        self.imgui_newFrame(frametime)
        self.imgui_render()

    def cleanup(self):
        print('Cleaning up ressources.')

        self.vao_quad.release()
        self.vao_disk.release()
        for str, program in self.program.items():
            program.release()

    def __del__(self):
        self.cleanup()

    ## IMGUI
    from _gui import\
        imgui_newFrame,\
        imgui_render

    ## EVENTS
    from _event import \
        resize,\
        key_event,\
        mouse_position_event,\
        mouse_drag_event,\
        mouse_scroll_event,\
        mouse_press_event,\
        mouse_release_event,\
        unicode_char_entered

if __name__ == "__main__":
    MyWindow.run()

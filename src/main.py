#! /usr/bin/python3

import moderngl
import imgui
import glm

import moderngl_window
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from moderngl_window.opengl.vao import VAO

from random import randint, uniform
from math import cos, sin, pi, tau, radians
from array import array

from fps_counter import FpsCounter
from shapes import ShapeBuilder

# import time

## to have a concret object for moving shapes instead of a list
class Shape:
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

        self.texture = self.ctx.texture(self.wnd.buffer_size, 4)
        self.fbo = self.ctx.framebuffer(
            color_attachments=self.texture
        )
        self.quad_fs = moderngl_window.geometry.quad_fs()

        self.program = {
            "SHAPE": self.load_program(
                vertex_shader='./shape.vert',
                fragment_shader='./shape.frag'),
        }

        vertices = array('f', ShapeBuilder.quad())
        self.vao_quad = VAO(mode=moderngl.TRIANGLES)
        self.vao_quad.buffer(self.ctx.buffer(vertices), '2f', ['v_vert'])

        vertices = array('f', ShapeBuilder.disk())
        self.vao_disk = VAO(mode=moderngl.TRIANGLE_FAN)
        self.vao_disk.buffer(self.ctx.buffer(vertices), '2f', ['v_vert'])

        ## game
        ## 0 == cube; 1 == disk
        self.shapes = self.generate_shapes(n=20)

    def generate_shapes(self, n):
        shapes = []
        for i in range(n):
            shape = randint(0, 1)
            x = uniform(100, self.wnd.width-100)
            y = uniform(100, self.wnd.height-100)
            dir = uniform(0, tau)
            speed = uniform(0.2, 1) * 0.5
            angle = uniform(0, tau)
            scale = uniform(200, self.wnd.width/3)
            shapes.append(Shape(x, y, angle, scale, dir, speed, shape))
        return shapes

    def update_uniforms(self, frametime):
        self.program['SHAPE']['u_projectionMatrix'].write(self.projection)
        self.program['SHAPE']['u_texture'] = 0

    def update(self, time_since_start, frametime):
        self.fps_counter.update(frametime)
        self.update_uniforms(frametime)

        for shape in self.shapes:
            shape.update()

    def render_shapes(self):
        for i, shape in enumerate(self.shapes):
            m = glm.mat4(1.0)
            m = glm.translate(m, glm.vec3(shape.x, shape.y, 0))
            m = glm.rotate(m, shape.angle, glm.vec3(0, 0, 1))
            m = glm.scale(m, glm.vec3(shape.scale))

            self.program['SHAPE']['u_modelMatrix'].write(m)

            with self.query:
                if shape.shape == 0:
                    self.vao_quad.render(program=self.program['SHAPE'])
                else:
                    self.vao_disk.render(program=self.program['SHAPE'])
            self.query_debug_values[f'render {i}'] = self.query.elapsed * 10e-7

    def render(self, time_since_start, frametime):
        self.update(time_since_start, frametime)

        # self.ctx.clear(0, 0, 0, 1)

        self.fbo.clear(0, 0, 0, 1)
        self.fbo.use()
        self.texture.use(location=0)
        self.render_shapes()
        self.ctx.copy_framebuffer(src=self.fbo, dst=self.ctx.screen)

        self.ctx.screen.use()
        self.ctx.disable(moderngl.DEPTH_TEST) # disables wireframe and depth_test for imgui

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

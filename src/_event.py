import imgui

def resize(self, width: int, height: int):
    self.imgui.resize(width, height)
    # self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)

def key_event(self, key, action, modifiers):
    self.imgui.key_event(key, action, modifiers)

    self.player.key_input(key, action, modifiers)

def mouse_position_event(self, x, y, dx, dy):
    self.imgui.mouse_position_event(x, y, dx, dy)


def mouse_drag_event(self, x, y, dx, dy):
    self.imgui.mouse_drag_event(x, y, dx, dy)

    io = imgui.get_io()
    if io.want_capture_mouse: return

def mouse_scroll_event(self, x_offset, y_offset):
    self.imgui.mouse_scroll_event(x_offset, y_offset)

def mouse_press_event(self, x, y, button):
    self.imgui.mouse_press_event(x, y, button)

def mouse_release_event(self, x: int, y: int, button: int):
    self.imgui.mouse_release_event(x, y, button)

def unicode_char_entered(self, char):
    self.imgui.unicode_char_entered(char)

import imgui

def imgui_newFrame(self, frametime):
    imgui.new_frame()
    imgui.begin("Properties", True)

    imgui.text("Dash Stamina: {}".format(self.player.dash_stamina));
    imgui.text("Nb shapes: {}".format(len(self.shapes)));

    imgui.text("fps: {:.2f}".format(self.fps_counter.get_fps()))
    for query, value in self.query_debug_values.items():
        imgui.text("{}: {:.2f} ms".format(query, value))


    imgui.spacing(); imgui.spacing()

    # imgui.text("Tree Settings");
    # imgui.begin_group()
    # c, self.TessLevel = imgui.slider_int(
    #     label="subdivision",
    #     value=self.TessLevel,
    #     min_value=1,
    #     max_value=64)
    # imgui.end_group()


    imgui.end()

def imgui_render(self):
    imgui.render()
    self.imgui.render(imgui.get_draw_data())

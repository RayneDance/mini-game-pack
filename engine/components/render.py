from engine.components.drawables import DrawDepth
class Render:
    def __init__(self):
        self.visible = True
        self.texture = None
        self.draw_depth = DrawDepth.DEFAULT

    def set_visible(self, visible: bool):
        self.visible = visible

    def set_texture(self, texture):
        self.texture = texture

    def set_draw_depth(self, depth: DrawDepth):
        self.draw_depth = depth
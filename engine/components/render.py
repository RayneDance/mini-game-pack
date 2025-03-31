from engine.components.drawables import DrawDepth
class Render:
    def __init__(self, texture=None, visible=True, draw_depth=DrawDepth.DEFAULT):
        self.visible = visible
        self.texture = texture
        self.draw_depth = draw_depth

    def set_visible(self, visible: bool):
        self.visible = visible

    def set_texture(self, texture):
        self.texture = texture

    def set_draw_depth(self, depth: DrawDepth):
        self.draw_depth = depth
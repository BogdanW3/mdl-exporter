
class War3Texture:
    def __init__(self, texture_path="Textures\\white.blp", replaceable_id=0):
        self.texture_path: str = texture_path
        self.replaceable_id: int = replaceable_id
        self.wrap_width: bool = False
        self.wrap_height: bool = False


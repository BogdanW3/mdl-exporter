
class War3Texture:
    def __init__(self, texture_path="Textures\\white.blp", replaceable_id=0):
        self.texture_path: str = texture_path
        self.replaceable_id: int = replaceable_id
        self.wrap_width: bool = False
        self.wrap_height: bool = False

    def _key(self):
        # Replaceable textures are told apart by id alone, others by path (the same file in different spelling
        # is still the same texture)
        try:
            replaceable = int(self.replaceable_id or 0)
        except (TypeError, ValueError):
            replaceable = 0
        if replaceable:
            return replaceable, ''
        return 0, (self.texture_path or '').replace('/', '\\').lower()

    def __eq__(self, other):
        if isinstance(other, War3Texture):
            return self._key() == other._key()
        return NotImplemented

    def __hash__(self):
        return hash(self._key())


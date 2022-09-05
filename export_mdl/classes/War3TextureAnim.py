from typing import Optional, List

from .War3AnimationCurve import War3AnimationCurve


class War3TextureAnim:
    def __init__(self):
        self.translation: Optional[War3AnimationCurve] = None
        self.rotation: Optional[War3AnimationCurve] = None
        self.scale: Optional[War3AnimationCurve] = None

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            a = [self.translation, self.rotation, self.scale]
            b = [other.translation, other.rotation, other.scale]

            for x, y in zip(a, b):
                if x != y:
                    return False

            return True

        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((hash(self.translation), hash(self.rotation), hash(self.scale)))

    def set_from(self,
                translation: Optional[War3AnimationCurve],
                rotation: Optional[War3AnimationCurve],
                scale: Optional[War3AnimationCurve]):
        self.translation = translation
        self.rotation = rotation
        self.scale = scale


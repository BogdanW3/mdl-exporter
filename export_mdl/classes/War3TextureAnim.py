from .War3AnimationCurve import War3AnimationCurve
from .animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve


class War3TextureAnim:
    def __init__(self):
        self.translation = None
        self.rotation = None
        self.scale = None

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

    @staticmethod
    def get(anim_data, uv_node, sequences):
        anim = War3TextureAnim()
        if anim_data.action:
            if len(uv_node.inputs) > 1: # 2.81 Mapping Node
                anim.translation = get_wc3_animation_curve(anim_data, 'nodes["%s"].inputs["Location"].default_value' % uv_node.name, 3, sequences)
                anim.rotation = get_wc3_animation_curve(anim_data, 'nodes["%s"].inputs["Rotation"].default_value' % uv_node.name, 3, sequences)
                anim.scale = get_wc3_animation_curve(anim_data, 'nodes["%s"].inputs["Scale"].default_value' % uv_node.name, 3, sequences)
            else:
                anim.translation = get_wc3_animation_curve(anim_data, 'nodes["%s"].translation' % uv_node.name, 3, sequences)
                anim.rotation = get_wc3_animation_curve(anim_data, 'nodes["%s"].rotation' % uv_node.name, 3, sequences)
                anim.scale = get_wc3_animation_curve(anim_data, 'nodes["%s"].scale' % uv_node.name, 3, sequences)

        return anim if any((anim.translation, anim.rotation, anim.scale)) else None

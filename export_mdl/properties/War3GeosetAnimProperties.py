import bpy
from bpy.props import FloatProperty, FloatVectorProperty, PointerProperty
from bpy.types import PropertyGroup


def _refresh(self, context):
    # So the viewport preview (drivers on the object color) follows a change right away
    self.id_data.update_tag()


class War3GeosetAnimProperties(PropertyGroup):
    """A mesh object's geoset animation: how visible and what tint its geosets have during each sequence."""
    alpha: FloatProperty(
        name="Alpha",
        description="Geoset visibility, 0 is hidden and 1 fully visible. Keyframe it to show or hide the "
                    "geoset during sequences (constant interpolation gives an on/off switch, linear a fade)",
        default=1.0,
        min=0.0,
        max=1.0,
        options={'ANIMATABLE'},
        update=_refresh
    )

    color: FloatVectorProperty(
        name="Color",
        description="Tint multiplied over the geoset. Can be keyframed",
        subtype='COLOR',
        size=3,
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        options={'ANIMATABLE'},
        update=_refresh
    )

    @classmethod
    def register(cls):
        bpy.types.Object.mdl_geoset = PointerProperty(type=War3GeosetAnimProperties)

    @classmethod
    def unregister(cls):
        del bpy.types.Object.mdl_geoset

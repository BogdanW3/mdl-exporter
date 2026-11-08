from bpy.props import BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty
from bpy.types import PropertyGroup


class War3LightSettings(PropertyGroup):
    light_type: EnumProperty(
        name="Type",
        items=[('Omnidirectional', "Omnidirectional", ""),
               ('Directional', "Directional", ""),
               ('Ambient', "Ambient", "")],
        default='Omnidirectional'
        )

    atten_start: FloatProperty(
        name="Attenuation Start",
        description="Range at which the light intensity starts to taper off.",
        min=0,
        default=80
        )

    atten_end: FloatProperty(
        name="Attenuation End",
        description="Maximum range of the light.",
        min=0,
        default=200
        )

    intensity: FloatProperty(
        name="Intensity",
        min=0,
        default=10,
        )

    amb_intensity: FloatProperty(
        name="Ambient Intensity",
        min=0,
        default=0
        )
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=[1.0, 1.0, 1.0],
        )

    amb_color: FloatVectorProperty(
        name="Ambient Color",
        subtype='COLOR',
        default=[1.0, 1.0, 1.0],
        )

    shadow_intensity: FloatProperty(
        name="Shadow Intensity",
        description="How dark the shadows of this light are. Exported for format version 1200 and up.",
        min=0,
        max=1,
        default=0.4
        )

    shadow_casting: BoolProperty(
        name="Cast Shadows",
        description="Whether this light casts shadows. Exported for format version 1300 and up.",
        default=False
        )

    shadow_casting_start: FloatProperty(
        name="Shadow Start",
        description="Distance at which shadow casting begins. Exported for format version 1300 and up.",
        min=0,
        default=0
        )

    shadow_casting_end: FloatProperty(
        name="Shadow End",
        description="Distance at which shadow casting stops. Exported for format version 1300 and up.",
        min=0,
        default=0
        )

    quadratic_falloff: FloatProperty(
        name="Quadratic Falloff",
        description="Exported for format version 1600 and up.",
        min=0,
        default=0.0005,
        precision=5
        )

    linear_falloff: FloatProperty(
        name="Linear Falloff",
        description="Exported for format version 1600 and up.",
        min=0,
        default=0,
        precision=5
        )

    damping: FloatProperty(
        name="Damping",
        description="Exported for format version 1600 and up.",
        min=0,
        default=0.00001,
        precision=6
        )

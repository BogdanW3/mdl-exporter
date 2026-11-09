import bpy
from bpy.props import StringProperty, EnumProperty, IntProperty, BoolProperty, FloatProperty, CollectionProperty, \
    FloatVectorProperty
from bpy.types import PropertyGroup


MATERIAL_SHADERS = [
    ('AUTO', "Automatic", "HD Default Unit when the node tree has normal, ORM or emissive textures and HD "
                          "skinning is on (the default), SD otherwise"),
    ('SD', "SD", "Classic material, every layer is drawn on top of the previous one"),
    ('HD', "HD Default Unit", "PBR material (v900+). The layers are the texture slots: diffuse, normal, ORM, "
                              "emissive, team color and environment"),
    ('CRYSTAL', "HD Crystal", "Like HD Default Unit, with the crystal shader (v900+)"),
]

# What each layer is used for when the material is HD, in slot order
HD_SLOT_NAMES = ("Diffuse", "Normal", "ORM", "Emissive", "Team Color", "Environment")


class War3MaterialLayerProperties(PropertyGroup):
    # bpy_type = bpy.types.Material
    name: StringProperty(
        name="Name",
        description="Name of this layer - this value is not exported.",
        default="Layer",
        maxlen=16
        )

    texture_type: EnumProperty(
        name="Texture Type",
        items=[('0', "Image", "", 0, 0),
               ('1', "Team Color", "", 0, 1),
               ('2', "Team Glow", "", 0, 2),
               ('11', "Cliff", "", 0, 11),
               ('31', "Lordaeron Tree", "", 0, 31),
               ('32', "Ashenvale Tree", "", 0, 32),
               ('33', "Barrens Tree", "", 0, 33),
               ('34', "Northrend Tree", "", 0, 34),
               ('35', "Mushroom Tree", "", 0, 35),
               ('36', "Replaceable ID", "", 0, 36)],
        default='0'
        )

    replaceable_id: IntProperty(
        name="ID",
        description="ID of the replaceable texture.",
        default=100,
        min=0
        )

    filter_mode: EnumProperty(
        name="Filter Mode",
        items=[('None', "Opaque", ""),
               ('Blend', "Blend", ""),
               ('Transparent', "Transparent", ""),
               ('Additive', "Additive", ""),
               ('AddAlpha', "Additive Alpha", ""),
               ('Modulate', "Modulate", ""),
               ('Modulate2x', "Modulate 2X", "")],
        default='None'
        )

    unshaded: BoolProperty(
        name="Unshaded",
        description="Ignore scene lighting, the texture shows at full brightness",
        default=False
        )

    unfogged: BoolProperty(
        name="Unfogged",
        description="Not affected by distance fog",
        default=False
        )

    sphere_env_map: BoolProperty(
        name="Sphere Environment Map",
        description="Map the texture as a reflection instead of using the UVs",
        default=False
        )

    wrap_width: BoolProperty(
        name="Wrap Width",
        description="Repeat the texture horizontally",
        default=False
        )

    wrap_height: BoolProperty(
        name="Wrap Height",
        description="Repeat the texture vertically",
        default=False
        )

    unlit: BoolProperty(
        name="Unlit",
        description="HD: skip lighting for this layer",
        default=False
        )

    back_faces_for_shadows: BoolProperty(
        name="Back Faces For Shadows",
        description="HD: cast shadows from back faces",
        default=False
        )

    ambient_occlusion: BoolProperty(
        name="Ambient Occlusion",
        description="HD: apply ambient occlusion",
        default=False
        )

    emissive_gain: FloatProperty(
        name="Emissive Gain",
        description="Strength of the emissive texture (v900+). Can be animated",
        default=1.0,
        min=0.0,
        options={'ANIMATABLE'}
        )

    fresnel_color: FloatVectorProperty(
        name="Fresnel Color",
        description="Rim light color (v1000+). Can be animated",
        subtype='COLOR',
        size=3,
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        options={'ANIMATABLE'}
        )

    fresnel_opacity: FloatProperty(
        name="Fresnel Opacity",
        description="Rim light strength, 0 turns it off (v1000+). Can be animated",
        default=0.0,
        min=0.0,
        max=1.0,
        options={'ANIMATABLE'}
        )

    fresnel_team_color: FloatProperty(
        name="Fresnel Team Color",
        description="How much the rim light takes the team color (v1000+). Can be animated",
        default=0.0,
        min=0.0,
        max=1.0,
        options={'ANIMATABLE'}
        )

    two_sided: BoolProperty(
        name="Two Sided",
        description="Whether or not to render backfaces.",
        default=False
        )

    no_depth_test: BoolProperty(
        name="No Depth Test",
        description="If true, this layer will always render, even if it's occluded.",
        default=False
        )

    no_depth_set: BoolProperty(
        name="No Depth Set",
        description="If true, this layer will never occlude other objects which are rendered afterwards.",
        default=False
        )

    alpha: FloatProperty(
        name="Alpha",
        description="Alpha factor used with the blend filter mode. Can be animated.",
        default=1.0,
        options={'ANIMATABLE'},
        min=0.0,
        max=1.0
        )
    path: StringProperty(
        name="Texture Path",
        default="",
        maxlen=256
        )

    @classmethod
    def register(cls):
        bpy.types.Material.mdl_layers = CollectionProperty(type=War3MaterialLayerProperties, options={'HIDDEN'})
        # bpy.types.Material.mdl_layers: CollectionProperty = CollectionProperty(type=War3MaterialLayerProperties, options={'HIDDEN'})
        # bpy.types.Material.mdl_layers
        bpy.types.Material.mdl_layer_index = IntProperty(name="Layer index", description="", default=0, options={'HIDDEN'})
        bpy.types.Material.priority_plane = IntProperty(name="Priority Plane", description="Order at which this material will be rendered", default=0, options={'HIDDEN'})
        bpy.types.Material.mdl_shader = EnumProperty(name="Shader", items=MATERIAL_SHADERS, default='AUTO',
                                                     options={'HIDDEN'})

    @classmethod
    def unregister(cls):
        del bpy.types.Material.mdl_layers
        del bpy.types.Material.mdl_layer_index
        del bpy.types.Material.priority_plane
        del bpy.types.Material.mdl_shader

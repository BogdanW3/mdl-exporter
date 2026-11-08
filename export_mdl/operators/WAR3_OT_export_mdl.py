import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import orientation_helper, ExportHelper, axis_conversion
from mathutils import Matrix

from ..classes.War3ExportSettings import War3ExportSettings

FORMAT_VERSIONS = [
    ('800', "800 (Classic / SD)", "Classic SD format, readable by every game version and tool"),
    ('900', "900", "Adds HD materials, tangents and skin weights"),
    ('1000', "1000", "Adds layer emissive and fresnel settings"),
    ('1100', "1100", "HD textures are bound per slot in a single layer"),
    ('1200', "1200", "Adds light shadow intensity"),
    ('1300', "1300", "Adds light shadow casting"),
    ('1400', "1400", "16 bit skin bone indices"),
    ('1600', "1600", "Adds light falloff and damping"),
    ('1800', "1800 (Latest)", "Latest format the game knows about"),
]


@orientation_helper(axis_forward='Y', axis_up='Z')
class WAR3_OT_export_mdl(Operator, ExportHelper):
    """MDL Exporter"""
    bl_idname = 'export.mdl_exporter'
    bl_description = 'Warcraft 3 MDL Exporter'
    bl_label = 'Export .MDL'
    filename_ext = ".mdl"

    filter_glob: StringProperty(
            default="*.mdl", options={'HIDDEN'}
            )

    filepath: StringProperty(
            subtype="FILE_PATH"
            )

    use_selection: BoolProperty(
            name="Selected Objects",
            description="Export only selected objects on visible layers",
            default=False,
            )

    format_version: EnumProperty(
            name="Format Version",
            description="MDL FormatVersion to write. Fields newer than this version are left out",
            items=FORMAT_VERSIONS,
            default='800',
            )

    global_scale: FloatProperty(
            name="Scale",
            min=0.01,
            max=1000.0,
            default=1,
            )

    optimize_animation: BoolProperty(
            name="Optimize Keyframes",
            description="Remove keyframes if the resulting motion deviates less than the tolerance value."
            )

    demote_to_helper: BoolProperty(
            name="Demote Bones To Helpers",
            description="Save bones not used for mesh as helpers.",
            default=True
            )

    use_actions: BoolProperty(
            name="Use Actions",
            description="Use actions instead of mdl-sequences"
            )

    use_skinweights: BoolProperty(
            name="Use SkinWeights",
            description="Use skin weights instead of vertex groups"
            )

    optimize_tolerance: FloatProperty(
            name="Tolerance",
            min=0.001,
            soft_max=0.1,
            default=0.05,
            subtype='DISTANCE',
            unit='LENGTH'
            )

    def execute(self, context: bpy.types.Context):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        settings: War3ExportSettings = War3ExportSettings()
        settings.global_matrix = axis_conversion(
            to_forward=self.axis_forward,
            to_up=self.axis_up,
        ).to_4x4() @ Matrix.Scale(self.global_scale, 4)

        settings.scale = self.global_scale
        settings.use_selection = self.use_selection
        settings.optimize_animation = self.optimize_animation
        settings.demote_to_helper = self.demote_to_helper
        settings.optimize_tolerance = self.optimize_tolerance
        settings.use_actions = self.use_actions
        settings.use_skinweights = self.use_skinweights

        from ..export_mdl import export_mdl
        export_mdl.save(self, context, settings, filepath=filepath, mdl_version=int(self.format_version))

        return {'FINISHED'}

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        layout.prop(self, "format_version")
        if self.use_skinweights and int(self.format_version) < 900:
            layout.label(text="Skin weights will be exported as version 1000", icon='INFO')
        layout.prop(self, "use_selection")
        layout.prop(self, "global_scale")
        layout.prop(self, "axis_forward")
        layout.prop(self, "axis_up")
        layout.separator()
        layout.prop(self, 'optimize_animation')
        layout.prop(self, 'demote_to_helper')
        layout.prop(self, 'use_actions')
        layout.prop(self, 'use_skinweights')
        if self.optimize_animation:
            box = layout.box()
            box.label(text="EXPERIMENTAL", icon='ERROR')
            layout.prop(self, 'optimize_tolerance')
        if self.use_actions:
            box = layout.box()
            box.label(text="EXPERIMENTAL", icon='ERROR')
            box.label(text="Will export action and not marker based sequences. "
                           "This does not yet support Rarity or NonLooping")
        if self.use_skinweights:
            box = layout.box()
            box.label(text="EXPERIMENTAL", icon='ERROR')
            box.label(text="Will export with skin weights and leave vertex groups empty.")
            # layout.prop(self, 'use_actions')

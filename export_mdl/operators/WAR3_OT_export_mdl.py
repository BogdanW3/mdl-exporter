import os

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import orientation_helper, ExportHelper, axis_conversion
from mathutils import Matrix

from ..classes.War3ExportSettings import War3ExportSettings

FORMAT_VERSIONS = [
    ('1800', "1800 (Latest)", "Latest format the game knows about"),
    ('1600', "1600", "Adds light falloff and damping"),
    ('1400', "1400", "16 bit skin bone indices"),
    ('1300', "1300", "Adds light shadow casting"),
    ('1200', "1200", "Adds light shadow intensity"),
    ('1100', "1100", "Layers name their own shader and list their textures by slot"),
    ('1000', "1000", "Adds layer emissive and fresnel settings"),
    ('900', "900", "Adds HD materials, tangents and skin weights"),
    ('800', "800 (Classic / SD)", "Classic SD format, readable by every game version and tool"),
]

# Export options remembered per .blend file, on the scene. The leading underscore hides it from the
# Custom Properties panel.
REMEMBERED_KEY = "_war3_export"
REMEMBERED_OPTIONS = ("file_format", "format_version", "use_selection", "global_scale", "axis_forward", "axis_up",
                      "optimize_animation", "optimize_tolerance", "demote_to_helper", "use_actions",
                      "use_skinweights")


def remember_options(operator, context: bpy.types.Context):
    """Store the dialog's options on the scene, so the next export (even after a cancel) starts from them."""
    try:
        context.scene[REMEMBERED_KEY] = {key: getattr(operator, key) for key in REMEMBERED_OPTIONS}
    except (AttributeError, TypeError, RuntimeError):
        pass  # The scene can't be written to in this context


def sub_panel(layout: bpy.types.UILayout, idname: str, title: str, default_closed: bool = False):
    """A collapsible section (Blender 4.1+), or a plain box on older versions. Returns None when collapsed."""
    if hasattr(layout, "panel"):
        header, body = layout.panel(idname, default_closed=default_closed)
        header.label(text=title)
        return body
    box = layout.box()
    box.label(text=title)
    return box


@orientation_helper(axis_forward='Y', axis_up='Z')
class WAR3_OT_export_mdl(Operator, ExportHelper):
    """Warcraft 3 Model Exporter"""
    bl_idname = 'export.mdl_exporter'
    bl_description = 'Export a Warcraft 3 model (.mdx or .mdl)'
    bl_label = 'Export Warcraft 3 Model'
    filename_ext = ".mdx"

    filter_glob: StringProperty(
            default="*.mdx;*.mdl", options={'HIDDEN'}
            )

    filepath: StringProperty(
            subtype="FILE_PATH"
            )

    file_format: EnumProperty(
            name="Format",
            items=[('MDX', "MDX (binary)", "Binary model, what the game and most tools load"),
                   ('MDL', "MDL (text)", "Text model, readable and editable by hand")],
            default='MDX',
            )

    use_selection: BoolProperty(
            name="Selected Objects",
            description="Export only selected objects on visible layers",
            default=False,
            )

    format_version: EnumProperty(
            name="Version",
            description="Format version to write. Fields newer than this version are left out",
            items=FORMAT_VERSIONS,
            default='1800',
            )

    global_scale: FloatProperty(
            name="Scale",
            min=0.01,
            max=1000.0,
            default=1,
            )

    optimize_animation: BoolProperty(
            name="Optimize Keyframes",
            description="Remove keyframes if the resulting motion deviates less than the tolerance value. "
                        "Experimental"
            )

    demote_to_helper: BoolProperty(
            name="Demote Bones To Helpers",
            description="Save bones not used for mesh as helpers.",
            default=True
            )

    use_actions: BoolProperty(
            name="Use Actions",
            description="Export each action as a sequence, instead of the timeline markers from the scene's "
                        "sequence list. Experimental: rarity and non looping aren't exported yet"
            )

    use_skinweights: BoolProperty(
            name="HD Skinning",
            description="Materials set to Automatic become HD when their node tree has normal, ORM or emissive "
                        "textures, and geosets using an HD material get skin weights and tangents. SD materials "
                        "are left as they are. Ignored for version 800, which has no HD",
            default=True
            )

    optimize_tolerance: FloatProperty(
            name="Tolerance",
            min=0.001,
            soft_max=0.1,
            default=0.05,
            subtype='DISTANCE',
            unit='LENGTH'
            )

    def invoke(self, context: bpy.types.Context, event):
        # Start from what this .blend exported with last time
        remembered = context.scene.get(REMEMBERED_KEY)
        if remembered is not None:
            for key in REMEMBERED_OPTIONS:
                if key in remembered:
                    try:
                        setattr(self, key, remembered[key])
                    except (TypeError, ValueError):
                        pass  # An option whose choices changed since
        return super().invoke(context, event)

    def check(self, context: bpy.types.Context):
        # Called on every option change: remember the options even if the export is cancelled
        remember_options(self, context)
        # Keep the file extension in line with the chosen format
        root, ext = os.path.splitext(self.filepath)
        wanted = "." + self.file_format.lower()
        if os.path.basename(root) and ext.lower() != wanted:
            self.filepath = root + wanted
            return True
        return False

    def execute(self, context: bpy.types.Context):
        filepath = self.filepath
        # An explicit .mdl/.mdx extension (e.g. from a script) decides the format
        ext = os.path.splitext(filepath)[1].lower()
        file_format = {'.mdx': 'MDX', '.mdl': 'MDL'}.get(ext, self.file_format)
        filepath = bpy.path.ensure_ext(filepath, "." + file_format.lower())

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
        try:
            warnings = export_mdl.save(self, context, settings, filepath=filepath,
                                       mdl_version=int(self.format_version), file_format=file_format)
        except ValueError as e:
            # Things the chosen format can't hold, explained in the message
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        for warning in warnings or ():
            self.report({'WARNING'}, warning)
        remember_options(self, context)
        return {'FINISHED'}

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        version = int(self.format_version)

        body = sub_panel(layout, "WAR3_export_format", "Format")
        if body:
            body.prop(self, "file_format")
            body.prop(self, "format_version")
            row = body.row()
            row.enabled = 900 <= version
            row.prop(self, "use_skinweights")
            if version < 900:
                body.label(text="Version 800 has no HD, everything is written as SD", icon='INFO')

        body = sub_panel(layout, "WAR3_export_transform", "Include & Transform")
        if body:
            body.prop(self, "use_selection")
            body.prop(self, "global_scale")
            body.prop(self, "axis_forward")
            body.prop(self, "axis_up")

        body = sub_panel(layout, "WAR3_export_animation", "Animation", default_closed=True)
        if body:
            body.prop(self, "demote_to_helper")
            body.prop(self, "use_actions")
            body.prop(self, "optimize_animation")
            if self.optimize_animation:
                body.prop(self, "optimize_tolerance")
            if self.use_actions or self.optimize_animation:
                body.label(text="Experimental options are on", icon='ERROR')

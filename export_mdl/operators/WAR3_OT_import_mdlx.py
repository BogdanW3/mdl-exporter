import os

import bpy
from bpy_extras import io_utils

from export_mdl import constants
from export_mdl.import_stuff.MDXImportProperties import MDXImportProperties
from export_mdl.import_stuff.mdl_parser.load_mdl import load_mdl
from export_mdl.import_stuff.mdx_parser.load_mdx import load_mdx


def set_team_color_property(operator, something):
    operator.teamColor = constants.TEAM_COLORS[int(operator.setTeamColor)]


class WAR3_OT_import_mdlx(bpy.types.Operator, io_utils.ImportHelper):
    """MDL Importer"""
    bl_idname = 'import.mdl_exporter'
    # bl_idname = 'warcraft_3.import_mdl_mdx'
    bl_label = 'Exp: Import *.mdl/*.mdx'
    bl_description = 'Import *.mdl/*.mdx files (Exporter function, 3d models of WarCraft 3)'
    bl_options = {'UNDO'}

    filename_ext = ['.mdx', '.mdl']
    filter_glob: bpy.props.StringProperty(default='*.mdx;*.mdl', options={'HIDDEN'})
    filepath: bpy.props.StringProperty(name='File Path', maxlen=1024, default='')
    useCustomFPS: bpy.props.BoolProperty(name='Use Custom FPS', default=False)
    animationFPS: bpy.props.FloatProperty(name='Animation FPS', default=30.0, min=1.0, max=1000.0)
    boneSize: bpy.props.FloatProperty(name='Bone Size', default=5.0, min=0.0001, max=1000.0)
    teamColor: bpy.props.FloatVectorProperty(
        name='Team Color',
        default=constants.TEAM_COLORS[0],
        min=0.0,
        max=1.0,
        size=3,
        subtype='COLOR',
        precision=3
        )
    setTeamColor: bpy.props.EnumProperty(
        items=[
            ("0", 'Red', ''),
            ("1", 'Blue', ''),
            ("2", 'Teal', ''),
            ("3", 'Purple', ''),
            ("4", 'Yellow', ''),
            ("5", 'Orange', ''),
            ("6", 'Green', ''),
            ("7", 'Pink', ''),
            ("8", 'Grey', ''),
            ("9", 'Light Blue', ''),
            ("10", 'Dark Green', ''),
            ("11", 'Brown', ''),
            ("12", 'Maroon', ''),
            ("13", 'Navy', ''),
            ("14", 'Turquoise', ''),
            ("15", 'Violet', ''),
            ("16", 'Wheat', ''),
            ("17", 'Peach', ''),
            ("18", 'Mint', ''),
            ("19", 'Lavender', ''),
            ("20", 'Coal', ''),
            ("21", 'Snow', ''),
            ("22", 'Emerald', ''),
            ("23", 'Peanut', ''),
            ("24", 'Black', '')
            ],
        name='Set Team Color',
        update=set_team_color_property,
        default="0"
        )

    def draw(self, context):
        layout = self.layout
        split = layout.split(factor=0.9)
        sub_split = split.split(factor=0.5)
        sub_split.label(text="Team Color:")
        sub_split.prop(self, 'setTeamColor', text="")
        split.prop(self, 'teamColor', text="")
        layout.prop(self, 'boneSize')
        layout.prop(self, 'useCustomFPS')
        if self.useCustomFPS:
            layout.prop(self, 'animationFPS')

    def execute(self, context):
        import_properties = MDXImportProperties()
        import_properties.mdx_file_path = self.filepath
        import_properties.team_color = self.setTeamColor
        import_properties.bone_size = self.boneSize
        import_properties.use_custom_fps = self.useCustomFPS
        import_properties.fps = self.animationFPS
        import_properties.calculate_frame_time()
        constants.os_path_separator = os.path
        if ".mdl" in self.filepath:
            load_mdl(import_properties)
        else:
            load_mdx(import_properties)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

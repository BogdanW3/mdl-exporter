import bpy


class War3Preferences(bpy.types.AddonPreferences):
    bl_idname = 'export_mdl'
    resourceFolder: bpy.props.StringProperty(
        name='Resource',
        default='',
        subtype='DIR_PATH'
        )
    alternativeResourceFolder: bpy.props.StringProperty(
        name='Alternative Resource',
        default='',
        subtype='DIR_PATH'
        )
    textureExtension: bpy.props.StringProperty(
        name='Image Extension',
        default='png'
        )
    defaultEncoding: bpy.props.EnumProperty(
        name='Default Encoding',
        items=[
            ('LATIN_1', 'latin-1',      ""),
            ('UTF_8',   'utf-8',        ""),
            ('UTF_16',  'utf-16',       ""),
            ('UTF_32',  'utf-32',       ""),
            ('ASCII',   'ascii',        ""),
            ('BIG5',    'big5 (CH)',    ""),
            ('EUC_KR',  'euc_kr (KR)',  ""),
            ('EUC_JP',  'euc_jp (JP)',  ""),
        ],
        default='LATIN_1'
        )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'resourceFolder')
        layout.prop(self, 'alternativeResourceFolder')
        layout.prop(self, 'textureExtension')
        layout.prop(self, 'defaultEncoding')

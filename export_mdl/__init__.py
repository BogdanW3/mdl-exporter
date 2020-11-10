# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
from .properties import War3BillboardProperties
from .properties import War3EventProperties
from .properties import War3LightSettings
from .properties import War3MaterialLayerProperties
from .properties import War3ParticleSystemProperties
from .properties import War3SequenceProperties
from .operators import WAR3_MT_emitter_presets
from .operators import WAR3_OT_add_anim_sequence
from .operators import WAR3_OT_create_collision_shape
from .operators import WAR3_OT_create_eventobject
from .operators import WAR3_OT_emitter_preset_add
from .operators import WAR3_OT_export_mdl
from .operators import WAR3_OT_material_list_action
from .operators import WAR3_OT_search_event_id
from .operators import WAR3_OT_search_event_type
from .operators import WAR3_OT_search_texture

bl_info = {
    "name": "Warcraft MDL Exporter",
    "author": "Kalle Halvarsson & me",
    'version': (0, 0, 1),
    "blender": (2, 80, 0),
    'category': 'Import-Export',
    "location": "File > Export > Warcraft MDL (.mdl)",
    "description": "Export mesh as Warcraft .MDL",
    }


if "bpy" in locals():
    from .operators import operators
    from .classes import classes
    from .export_mdl import export_mdl
    from .properties import properties
    from .ui import ui
    import importlib
    importlib.reload(properties)
    importlib.reload(operators)
    importlib.reload(classes)
    importlib.reload(export_mdl)
    importlib.reload(ui)
else:
    from .operators import operators
    from .classes import classes
    from .export_mdl import export_mdl
    from .properties import properties
    from .ui import ui

    import bpy
    import os
    import shutil

    from bpy.utils import register_class, unregister_class


classes = (
    War3MaterialLayerProperties.War3MaterialLayerProperties,
    War3EventProperties.War3EventProperties,
    War3SequenceProperties.War3SequenceProperties,
    War3BillboardProperties.War3BillboardProperties,
    War3ParticleSystemProperties.War3ParticleSystemProperties,
    War3LightSettings.War3LightSettings,
    WAR3_OT_export_mdl.WAR3_OT_export_mdl,
    WAR3_OT_search_event_type.WAR3_OT_search_event_type,
    WAR3_OT_search_event_id.WAR3_OT_search_event_id,
    WAR3_OT_search_texture.WAR3_OT_search_texture,
    WAR3_OT_create_eventobject.WAR3_OT_create_eventobject,
    WAR3_OT_create_collision_shape.WAR3_OT_create_collision_shape,
    WAR3_OT_material_list_action.WAR3_OT_material_list_action,
    WAR3_OT_emitter_preset_add.WAR3_OT_emitter_preset_add,
    WAR3_OT_add_anim_sequence.WAR3_OT_add_anim_sequence,
    WAR3_MT_emitter_presets.WAR3_MT_emitter_presets,
    ui.WAR3_UL_sequence_list,
    ui.WAR3_UL_material_layer_list,
    ui.WAR3_PT_sequences_panel,
    ui.WAR3_PT_event_panel,
    ui.WAR3_PT_billboard_panel,
    ui.WAR3_PT_material_panel,
    ui.WAR3_PT_particle_editor_panel,
    ui.WAR3_PT_light_panel
)


def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(export_mdl.operators.WAR3_OT_export_mdl.WAR3_OT_export_mdl.bl_idname, text="Warcraft MDL (.mdl)")


def register():
    for cls in classes:
        register_class(cls)
        
    bpy.types.TOPBAR_MT_file_export.append(menu_func)
    
    presets_path = os.path.join(bpy.utils.user_resource('SCRIPTS', "presets"), "mdl_exporter")
    emitters_path = os.path.join(presets_path, "emitters")
    
    if not os.path.exists(emitters_path):
        os.makedirs(emitters_path)
        source_path = os.path.join(os.path.join(os.path.dirname(__file__), "presets"), "emitters")
        files = os.listdir(source_path) 
        [shutil.copy2(os.path.join(source_path, f), emitters_path) for f in files]


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
        
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)


if __name__ == "__main__":
    register()

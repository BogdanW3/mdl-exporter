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
if "bpy" not in locals():
# if "mdl_exporter" not in locals():
    print("mdl_exporter: loading plugin")
    # import bpy
    # import os
    # import shutil
else:
    print("mdl_exporter: reloading  plugin")
    import importlib
    if "reload_ui_classes" in locals():
        from .ui import reload_ui_classes
        from .properties import reload_property_classes
        from .operators import reload_operator_classes
        from .classes import reload_war3_classes
        from .export_mdl import reload_export_classes
        from .import_stuff import reload_import_stuff
        from . import utils
        try:
            importlib.reload(reload_ui_classes)
            importlib.reload(reload_property_classes)
            importlib.reload(reload_operator_classes)
            importlib.reload(reload_war3_classes)
            importlib.reload(reload_export_classes)
            importlib.reload(reload_import_stuff)
            importlib.reload(utils)
        except ImportError:
            print("  could not reload module")
    else:
        from .ui import reload_ui_classes
        from .properties import reload_property_classes
        from .operators import reload_operator_classes
        from .classes import reload_war3_classes
        from .export_mdl import reload_export_classes
        from .import_stuff import reload_import_stuff


import bpy
import os
import shutil

from .ui.WAR3_PT_billboard_panel import WAR3_PT_billboard_panel
from .ui.WAR3_PT_event_panel import WAR3_PT_event_panel
from .ui.WAR3_PT_light_panel import WAR3_PT_light_panel
from .ui.WAR3_PT_material_panel import WAR3_PT_material_panel
from .ui.WAR3_PT_particle_editor_panel import WAR3_PT_particle_editor_panel
from .ui.WAR3_PT_sequences_panel import WAR3_PT_sequences_panel
from .ui.WAR3_UL_material_layer_list import WAR3_UL_material_layer_list
from .ui.WAR3_UL_sequence_list import WAR3_UL_sequence_list
from .ui.WAR3_PT_Armature_Sequences import WAR3_PT_Armature_Sequences
from .ui.WAR3_MT_sequence_context_menu import WAR3_MT_sequence_context_menu
from .properties.War3BillboardProperties import War3BillboardProperties
from .properties.War3EventProperties import War3EventProperties
from .properties.War3LightSettings import War3LightSettings
from .properties.War3MaterialLayerProperties import War3MaterialLayerProperties
from .properties.War3ParticleSystemProperties import War3ParticleSystemProperties
from .properties.War3ArmatureSequenceListItem import War3ArmatureSequenceListItem
from .properties.War3SequenceProperties import War3SequenceProperties
from .properties.War3Preferences import War3Preferences
from .properties.War3ArmatureProperties import War3ArmatureProperties
from .properties.War3SequencesProperties import War3SequencesProperties
from .operators.WAR3_MT_emitter_presets import WAR3_MT_emitter_presets
from .operators.WAR3_OT_add_anim_sequence import WAR3_OT_add_anim_sequence
from .operators.WAR3_OT_create_collision_shape import WAR3_OT_create_collision_shape
from .operators.WAR3_OT_create_eventobject import WAR3_OT_create_eventobject
from .operators.WAR3_OT_emitter_preset_add import WAR3_OT_emitter_preset_add
from .operators.WAR3_OT_export_mdl import WAR3_OT_export_mdl
from .operators.WAR3_OT_material_list_action import WAR3_OT_material_list_action
from .operators.WAR3_OT_search_event_id import WAR3_OT_search_event_id
from .operators.WAR3_OT_search_event_type import WAR3_OT_search_event_type
from .operators.WAR3_OT_search_texture import WAR3_OT_search_texture
from .operators.WAR3_OT_add_seq_to_armature import WAR3_OT_add_seq_to_armature
from .operators.WAR3_OT_remove_seq_from_armature import WAR3_OT_remove_seq_from_armature
from .operators.WAR3_OT_import_mdlx import WAR3_OT_import_mdlx
from .operators.WAR3_OT_generate_from_actions import WAR3_OT_generate_from_actions
from .operators.WAR3_OT_move_seq_in_list import WAR3_OT_move_seq_in_list

bl_info = {
    "name": "Warcraft MDL Exporter",
    "author": "Kalle Halvarsson (& twilac)",
    'version': (0, 0, 1),
    "blender": (2, 80, 0),
    'category': 'Import-Export',
    "location": "File > Export > Warcraft MDL (.mdl)",
    "description": "Export mesh as Warcraft .MDL",
    }


prop_classes = (
    War3Preferences,
    War3MaterialLayerProperties,
    War3EventProperties,
    War3BillboardProperties,
    War3ParticleSystemProperties,
    War3LightSettings,
    War3ArmatureSequenceListItem,
    War3ArmatureProperties,
    War3SequenceProperties,
    War3SequencesProperties
)

op_classes = (
    WAR3_OT_import_mdlx,
    WAR3_OT_export_mdl,
    WAR3_OT_search_event_type,
    WAR3_OT_search_event_id,
    WAR3_OT_search_texture,
    WAR3_OT_create_eventobject,
    WAR3_OT_create_collision_shape,
    WAR3_OT_material_list_action,
    WAR3_OT_emitter_preset_add,
    WAR3_OT_add_anim_sequence,
    WAR3_OT_add_seq_to_armature,
    WAR3_OT_remove_seq_from_armature,
    WAR3_MT_emitter_presets,
    WAR3_OT_generate_from_actions,
    WAR3_OT_move_seq_in_list
)

ui_classes = (
    WAR3_MT_sequence_context_menu,
    WAR3_UL_sequence_list,
    WAR3_UL_material_layer_list,
    WAR3_PT_sequences_panel,
    WAR3_PT_event_panel,
    WAR3_PT_billboard_panel,
    WAR3_PT_material_panel,
    WAR3_PT_particle_editor_panel,
    WAR3_PT_light_panel,
    WAR3_PT_Armature_Sequences
)


def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    # self.layout.operator(WAR3_OT_export_mdl.WAR3_OT_export_mdl.bl_idname, text="Warcraft MDL (.mdl)")
    self.layout.operator(WAR3_OT_export_mdl.bl_idname, text="Warcraft 3 MDL (.mdl)")


def menu_import_mdx(self, context):
    self.layout.operator(WAR3_OT_import_mdlx.bl_idname, text="Warcraft 3 (.mdl/.mdx) [WC3Exp]")


def register():
    from bpy.utils import register_class

    # for cls in classes:
    #     register_class(cls)

    print("  register property classes")
    for cls in prop_classes:
        # print("\t", cls)
        register_class(cls)

    # bpy.types.Armature.war_3 = bpy.props.PointerProperty(type=War3ArmatureProperties)
    # WarCraft3BoneProperties.bpy_type.war_3 = bpy.props.PointerProperty(type=WarCraft3BoneProperties)

    print("  register operator classes")
    for cls in op_classes:
        # print("\t", cls)
        register_class(cls)

    print("  register UI classes")
    for cls in ui_classes:
        # print("\t", cls)
        register_class(cls)
        
    bpy.types.TOPBAR_MT_file_export.append(menu_func)
    bpy.types.TOPBAR_MT_file_import.append(menu_import_mdx)

    presets_path = os.path.join(bpy.utils.user_resource('SCRIPTS', path="presets"), "mdl_exporter")
    emitters_path = os.path.join(presets_path, "emitters")
    
    if not os.path.exists(emitters_path):
        os.makedirs(emitters_path)
        source_path = os.path.join(os.path.join(os.path.dirname(__file__), "presets"), "emitters")
        files = os.listdir(source_path) 
        [shutil.copy2(os.path.join(source_path, f), emitters_path) for f in files]


def unregister():
    from bpy.utils import unregister_class
    # for cls in reversed(classes):
    #     unregister_class(cls)

    for cls in reversed(ui_classes):
        unregister_class(cls)
    for cls in reversed(op_classes):
        unregister_class(cls)
    for cls in reversed(prop_classes):
        unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func)


if __name__ == "__main__":
    register()
# # ##### BEGIN GPL LICENSE BLOCK #####
# #
# #  This program is free software; you can redistribute it and/or
# #  modify it under the terms of the GNU General Public License
# #  as published by the Free Software Foundation; either version 2
# #  of the License, or (at your option) any later version.
# #
# #  This program is distributed in the hope that it will be useful,
# #  but WITHOUT ANY WARRANTY; without even the implied warranty of
# #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #  GNU General Public License for more details.
# #
# #  You should have received a copy of the GNU General Public License
# #  along with this program; if not, write to the Free Software Foundation,
# #  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# #
# # ##### END GPL LICENSE BLOCK #####
# if "bpy" not in locals():
#     print("load mdl_exporter plugin")
#     import bpy
#     import os
#     import shutil
#     from .ui.WAR3_PT_billboard_panel import WAR3_PT_billboard_panel
#     from .ui.WAR3_PT_event_panel import WAR3_PT_event_panel
#     from .ui.WAR3_PT_light_panel import WAR3_PT_light_panel
#     from .ui.WAR3_PT_material_panel import WAR3_PT_material_panel
#     from .ui.WAR3_PT_particle_editor_panel import WAR3_PT_particle_editor_panel
#     from .ui.WAR3_PT_sequences_panel import WAR3_PT_sequences_panel
#     from .ui.WAR3_UL_material_layer_list import WAR3_UL_material_layer_list
#     from .ui.WAR3_UL_sequence_list import WAR3_UL_sequence_list
#     from .properties.War3BillboardProperties import War3BillboardProperties
#     from .properties.War3EventProperties import War3EventProperties
#     from .properties.War3LightSettings import War3LightSettings
#     from .properties.War3MaterialLayerProperties import War3MaterialLayerProperties
#     from .properties.War3ParticleSystemProperties import War3ParticleSystemProperties
#     from .properties.War3SequenceProperties import War3SequenceProperties
#     from .operators.WAR3_MT_emitter_presets import WAR3_MT_emitter_presets
#     from .operators.WAR3_OT_add_anim_sequence import WAR3_OT_add_anim_sequence
#     from .operators.WAR3_OT_create_collision_shape import WAR3_OT_create_collision_shape
#     from .operators.WAR3_OT_create_eventobject import WAR3_OT_create_eventobject
#     from .operators.WAR3_OT_emitter_preset_add import WAR3_OT_emitter_preset_add
#     from .operators.WAR3_OT_export_mdl import WAR3_OT_export_mdl
#     from .operators.WAR3_OT_material_list_action import WAR3_OT_material_list_action
#     from .operators.WAR3_OT_search_event_id import WAR3_OT_search_event_id
#     from .operators.WAR3_OT_search_event_type import WAR3_OT_search_event_type
#     from .operators.WAR3_OT_search_texture import WAR3_OT_search_texture
# else:
#     print("reload mdl_exporter plugin")
#     import importlib
#     from .ui import WAR3_PT_billboard_panel
#     from .ui import WAR3_PT_event_panel
#     from .ui import WAR3_PT_light_panel
#     from .ui import WAR3_PT_material_panel
#     from .ui import WAR3_PT_particle_editor_panel
#     from .ui import WAR3_PT_sequences_panel
#     from .ui import WAR3_UL_material_layer_list
#     from .ui import WAR3_UL_sequence_list
#     from .properties import War3BillboardProperties
#     from .properties import War3EventProperties
#     from .properties import War3LightSettings
#     from .properties import War3MaterialLayerProperties
#     from .properties import War3ParticleSystemProperties
#     from .properties import War3SequenceProperties
#     from .operators import WAR3_MT_emitter_presets
#     from .operators import WAR3_OT_add_anim_sequence
#     from .operators import WAR3_OT_create_collision_shape
#     from .operators import WAR3_OT_create_eventobject
#     from .operators import WAR3_OT_emitter_preset_add
#     from .operators import WAR3_OT_export_mdl
#     from .operators import WAR3_OT_material_list_action
#     from .operators import WAR3_OT_search_event_id
#     from .operators import WAR3_OT_search_event_type
#     from .operators import WAR3_OT_search_texture
#     try:
#         importlib.reload(WAR3_PT_billboard_panel)
#         importlib.reload(WAR3_PT_event_panel)
#         importlib.reload(WAR3_PT_light_panel)
#         importlib.reload(WAR3_PT_material_panel)
#         importlib.reload(WAR3_PT_particle_editor_panel)
#         importlib.reload(WAR3_PT_sequences_panel)
#         importlib.reload(WAR3_UL_material_layer_list)
#         importlib.reload(WAR3_UL_sequence_list)
#         importlib.reload(War3BillboardProperties)
#         importlib.reload(War3EventProperties)
#         importlib.reload(War3LightSettings)
#         importlib.reload(War3MaterialLayerProperties)
#         importlib.reload(War3ParticleSystemProperties)
#         importlib.reload(War3SequenceProperties)
#         importlib.reload(WAR3_MT_emitter_presets)
#         importlib.reload(WAR3_OT_add_anim_sequence)
#         importlib.reload(WAR3_OT_create_collision_shape)
#         importlib.reload(WAR3_OT_create_eventobject)
#         importlib.reload(WAR3_OT_emitter_preset_add)
#         importlib.reload(WAR3_OT_export_mdl)
#         importlib.reload(WAR3_OT_material_list_action)
#         importlib.reload(WAR3_OT_search_event_id)
#         importlib.reload(WAR3_OT_search_event_type)
#         importlib.reload(WAR3_OT_search_texture)
#     except ImportError:
#         print("could not reload module")
#
# bl_info = {
#     "name": "Warcraft MDL Exporter",
#     "author": "Kalle Halvarsson (& twilac)",
#     'version': (0, 0, 1),
#     "blender": (2, 80, 0),
#     'category': 'Import-Export',
#     "location": "File > Export > Warcraft MDL (.mdl)",
#     "description": "Export mesh as Warcraft .MDL",
#     }
#
#
# # if "bpy" in locals():
# #     from .operators import operators
# #     from .classes import classes
# #     from .export_mdl import export_mdl
# #     from .properties import properties
# #     from .ui import ui
# #     import importlib
# #     importlib.reload(properties)
# #     importlib.reload(operators)
# #     importlib.reload(classes)
# #     importlib.reload(export_mdl)
# #     importlib.reload(ui)
# # else:
# #     from .operators import (
# #         WAR3_OT_export_mdl,
# #         WAR3_OT_search_event_type,
# #         WAR3_OT_search_event_id,
# #         WAR3_OT_search_texture,
# #         WAR3_OT_create_eventobject,
# #         WAR3_OT_create_collision_shape,
# #         WAR3_OT_material_list_action,
# #         WAR3_OT_emitter_preset_add,
# #         WAR3_OT_add_anim_sequence,
# #         WAR3_MT_emitter_presets
# #     )
# #     from .classes import (
# #         War3AnimationCurve,
# #         War3AnimationSequence,
# #         War3Bone,
# #         War3CollisionShape,
# #         War3EventObject,
# #         War3ExportSettings,
# #         War3Geoset,
# #         War3GeosetAnim,
# #         War3Material,
# #         War3MaterialLayer,
# #         War3Model,
# #         War3Object,
# #         War3ParticleSystem,
# #         War3TextureAnim
# #     )
# #     from .export_mdl import export_mdl
# #     from .properties import (
# #         War3BillboardProperties,
# #         War3EventProperties,
# #         War3EventTypesContainer,
# #         War3LightSettings,
# #         War3MaterialLayerProperties,
# #         War3ParticleSystemProperties,
# #         War3SequenceProperties
# #     )
# #     from .ui import ui
# #
# #     import bpy
# #     import os
# #     import shutil
# #
# #     from bpy.utils import register_class, unregister_class
#
#
# prop_classes = (
#     War3MaterialLayerProperties,
#     War3EventProperties,
#     War3SequenceProperties,
#     War3BillboardProperties,
#     War3ParticleSystemProperties,
#     War3LightSettings
# )
#
# op_classes = (
#     WAR3_OT_export_mdl,
#     WAR3_OT_search_event_type,
#     WAR3_OT_search_event_id,
#     WAR3_OT_search_texture,
#     WAR3_OT_create_eventobject,
#     WAR3_OT_create_collision_shape,
#     WAR3_OT_material_list_action,
#     WAR3_OT_emitter_preset_add,
#     WAR3_OT_add_anim_sequence
# )
#
# ui_classes = (
#     WAR3_MT_emitter_presets,
#     WAR3_UL_sequence_list,
#     WAR3_UL_material_layer_list,
#     WAR3_PT_sequences_panel,
#     WAR3_PT_event_panel,
#     WAR3_PT_billboard_panel,
#     WAR3_PT_material_panel,
#     WAR3_PT_particle_editor_panel,
#     WAR3_PT_light_panel
# )
# # prop_classes = (
# #     War3MaterialLayerProperties.War3MaterialLayerProperties,
# #     War3EventProperties.War3EventProperties,
# #     War3SequenceProperties.War3SequenceProperties,
# #     War3BillboardProperties.War3BillboardProperties,
# #     War3ParticleSystemProperties.War3ParticleSystemProperties,
# #     War3LightSettings.War3LightSettings
# # )
# #
# # op_classes = (
# #     WAR3_OT_export_mdl.WAR3_OT_export_mdl,
# #     WAR3_OT_search_event_type.WAR3_OT_search_event_type,
# #     WAR3_OT_search_event_id.WAR3_OT_search_event_id,
# #     WAR3_OT_search_texture.WAR3_OT_search_texture,
# #     WAR3_OT_create_eventobject.WAR3_OT_create_eventobject,
# #     WAR3_OT_create_collision_shape.WAR3_OT_create_collision_shape,
# #     WAR3_OT_material_list_action.WAR3_OT_material_list_action,
# #     WAR3_OT_emitter_preset_add.WAR3_OT_emitter_preset_add,
# #     WAR3_OT_add_anim_sequence.WAR3_OT_add_anim_sequence
# # )
# #
# # ui_classes = (
# #     WAR3_MT_emitter_presets.WAR3_MT_emitter_presets,
# #     WAR3_UL_sequence_list,
# #     WAR3_UL_material_layer_list,
# #     WAR3_PT_sequences_panel,
# #     WAR3_PT_event_panel,
# #     WAR3_PT_billboard_panel,
# #     WAR3_PT_material_panel,
# #     WAR3_PT_particle_editor_panel,
# #     WAR3_PT_light_panel
# # )
#
# # classes = (
# #     War3MaterialLayerProperties.War3MaterialLayerProperties,
# #     War3EventProperties.War3EventProperties,
# #     War3SequenceProperties.War3SequenceProperties,
# #     War3BillboardProperties.War3BillboardProperties,
# #     War3ParticleSystemProperties.War3ParticleSystemProperties,
# #     War3LightSettings.War3LightSettings,
# #     WAR3_OT_export_mdl.WAR3_OT_export_mdl,
# #     WAR3_OT_search_event_type.WAR3_OT_search_event_type,
# #     WAR3_OT_search_event_id.WAR3_OT_search_event_id,
# #     WAR3_OT_search_texture.WAR3_OT_search_texture,
# #     WAR3_OT_create_eventobject.WAR3_OT_create_eventobject,
# #     WAR3_OT_create_collision_shape.WAR3_OT_create_collision_shape,
# #     WAR3_OT_material_list_action.WAR3_OT_material_list_action,
# #     WAR3_OT_emitter_preset_add.WAR3_OT_emitter_preset_add,
# #     WAR3_OT_add_anim_sequence.WAR3_OT_add_anim_sequence,
# #     WAR3_MT_emitter_presets.WAR3_MT_emitter_presets,
# #     WAR3_UL_sequence_list,
# #     WAR3_UL_material_layer_list,
# #     WAR3_PT_sequences_panel,
# #     WAR3_PT_event_panel,
# #     WAR3_PT_billboard_panel,
# #     WAR3_PT_material_panel,
# #     WAR3_PT_particle_editor_panel,
# #     WAR3_PT_light_panel
# # )
#
#
# def menu_func(self, context):
#     self.layout.operator_context = 'INVOKE_DEFAULT'
#     self.layout.operator(WAR3_OT_export_mdl.WAR3_OT_export_mdl.bl_idname, text="Warcraft MDL (.mdl)")
#
#
# def register():
#     from bpy.utils import register_class
#     # for cls in classes:
#     #     register_class(cls)
#
#     print("register property classes")
#     for cls in prop_classes:
#         print("\t", cls)
#         register_class(cls)
#
#     print("register operator classes")
#     for cls in op_classes:
#         print("\t", cls)
#         register_class(cls)
#
#     print("register UI classes")
#     for cls in ui_classes:
#         print("\t", cls)
#         register_class(cls)
#
#     bpy.types.TOPBAR_MT_file_export.append(menu_func)
#
#     presets_path = os.path.join(bpy.utils.user_resource('SCRIPTS', path="presets"), "mdl_exporter")
#     emitters_path = os.path.join(presets_path, "emitters")
#
#     if not os.path.exists(emitters_path):
#         os.makedirs(emitters_path)
#         source_path = os.path.join(os.path.join(os.path.dirname(__file__), "presets"), "emitters")
#         files = os.listdir(source_path)
#         [shutil.copy2(os.path.join(source_path, f), emitters_path) for f in files]
#
#
# def unregister():
#     from bpy.utils import unregister_class
#     # for cls in reversed(classes):
#     #     unregister_class(cls)
#
#     for cls in reversed(ui_classes):
#         unregister_class(cls)
#     for cls in reversed(op_classes):
#         unregister_class(cls)
#     for cls in reversed(prop_classes):
#         unregister_class(cls)
#
#     bpy.types.TOPBAR_MT_file_export.remove(menu_func)
#
#
# if __name__ == "__main__":
#     register()

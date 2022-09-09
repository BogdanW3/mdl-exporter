# import importlib.util
# from pathlib import Path
# import os
#
#
# def reload():
#     import importlib
#     from . import WAR3_PT_billboard_panel
#     from . import WAR3_PT_event_panel
#     from . import WAR3_PT_light_panel
#     from . import WAR3_PT_material_panel
#     from . import WAR3_PT_particle_editor_panel
#     from . import WAR3_PT_sequences_panel
#     from . import WAR3_UL_material_layer_list
#     from . import WAR3_UL_sequence_list
#
#     try:
#         print("    reloading UI modules")
#         importlib.reload(WAR3_PT_billboard_panel)
#         importlib.reload(WAR3_PT_event_panel)
#         importlib.reload(WAR3_PT_light_panel)
#         importlib.reload(WAR3_PT_material_panel)
#         importlib.reload(WAR3_PT_particle_editor_panel)
#         importlib.reload(WAR3_PT_sequences_panel)
#         importlib.reload(WAR3_UL_material_layer_list)
#         importlib.reload(WAR3_UL_sequence_list)
#     except ImportError:
#         print("    could not reload UI modules")
#
#
# def register():
#     from bpy.utils import register_class
#     from . import __init__
#     importlib.util.find_spec()
#     prop_classes = (
#         ui.War3Preferences.War3Preferences,
#         ui.War3MaterialLayerProperties.War3MaterialLayerProperties,
#         ui.War3EventProperties.War3EventProperties,
#         ui.War3SequenceProperties.War3SequenceProperties,
#         ui.War3BillboardProperties.War3BillboardProperties,
#         ui.War3ParticleSystemProperties.War3ParticleSystemProperties,
#         ui.War3LightSettings.War3LightSettings,
#         ui.War3ArmatureSequenceList.War3ArmatureSequenceList,
#         ui.War3ArmatureProperties.War3ArmatureProperties
#     )
#     for cls in prop_classes:
#         # print("\t", cls)
#         register_class(cls)
#
#
# def unregister():
#     from bpy.utils import unregister_class
#     for cls in prop_classes:
#         # print("\t", cls)
#         unregister_class(cls)
#
#
# def get_module_files(package_name):
#     MODULE_EXTENSIONS = '.py'
#     spec = importlib.util.find_spec(package_name)
#     if spec is None:
#         return set()
#
#     pathname = Path(spec.origin).parent
#     package_files = set()
#     for file in os.scandir(pathname):
#         if file.name.startswith('__'):
#             continue
#         current = '.'.join((package_name, file.name.partition('.')[0]))
#         if file.is_file():
#             if file.name.endswith(MODULE_EXTENSIONS):
#                 package_files.add(current)

import importlib
from . import WAR3_MT_emitter_presets
from . import WAR3_OT_add_anim_sequence
from . import WAR3_OT_create_collision_shape
from . import WAR3_OT_create_eventobject
from . import WAR3_OT_emitter_preset_add
from . import WAR3_OT_emitter_set_from_bpy
from . import WAR3_OT_export_mdl
from . import WAR3_OT_material_list_action
from . import WAR3_OT_search_event_id
from . import WAR3_OT_search_event_type
from . import WAR3_OT_search_texture
from . import WAR3_OT_import_mdlx
from . import WAR3_OT_add_seq_to_armature
from . import WAR3_OT_generate_from_actions
from . import WAR3_OT_move_seq_in_list
from . import WAR3_OT_sequence_tools
from . import WAR3_OT_setup_hd_nodes
from . import WAR3_OT_geoset_preview

try:
    print("    reloading operator modules")
    importlib.reload(WAR3_MT_emitter_presets)
    importlib.reload(WAR3_OT_add_anim_sequence)
    importlib.reload(WAR3_OT_create_collision_shape)
    importlib.reload(WAR3_OT_create_eventobject)
    importlib.reload(WAR3_OT_emitter_preset_add)
    importlib.reload(WAR3_OT_emitter_set_from_bpy)
    importlib.reload(WAR3_OT_export_mdl)
    importlib.reload(WAR3_OT_material_list_action)
    importlib.reload(WAR3_OT_search_event_id)
    importlib.reload(WAR3_OT_search_event_type)
    importlib.reload(WAR3_OT_search_texture)
    importlib.reload(WAR3_OT_import_mdlx)
    importlib.reload(WAR3_OT_add_seq_to_armature)
    importlib.reload(WAR3_OT_generate_from_actions)
    importlib.reload(WAR3_OT_move_seq_in_list)
    importlib.reload(WAR3_OT_sequence_tools)
    importlib.reload(WAR3_OT_setup_hd_nodes)
    importlib.reload(WAR3_OT_geoset_preview)
except ImportError:
    print("    could not reload operator modules")

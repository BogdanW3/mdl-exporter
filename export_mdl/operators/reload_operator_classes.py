import importlib
from . import WAR3_MT_emitter_presets
from . import WAR3_OT_add_anim_sequence
from . import WAR3_OT_create_collision_shape
from . import WAR3_OT_create_eventobject
from . import WAR3_OT_emitter_preset_add
from . import WAR3_OT_export_mdl
from . import WAR3_OT_material_list_action
from . import WAR3_OT_search_event_id
from . import WAR3_OT_search_event_type
from . import WAR3_OT_search_texture
from . import WAR3_OT_import_mdlx
from . import WAR3_OT_add_seq_to_armature
from . import WAR3_OT_move_seq_up
from . import WAR3_OT_move_seq_down
from . import WAR3_OT_generate_from_actions
from . import WAR3_OT_move_seq_in_list

try:
    print("    reloading operator modules")
    importlib.reload(WAR3_MT_emitter_presets)
    importlib.reload(WAR3_OT_add_anim_sequence)
    importlib.reload(WAR3_OT_create_collision_shape)
    importlib.reload(WAR3_OT_create_eventobject)
    importlib.reload(WAR3_OT_emitter_preset_add)
    importlib.reload(WAR3_OT_export_mdl)
    importlib.reload(WAR3_OT_material_list_action)
    importlib.reload(WAR3_OT_search_event_id)
    importlib.reload(WAR3_OT_search_event_type)
    importlib.reload(WAR3_OT_search_texture)
    importlib.reload(WAR3_OT_import_mdlx)
    importlib.reload(WAR3_OT_add_seq_to_armature)
    importlib.reload(WAR3_OT_move_seq_up)
    importlib.reload(WAR3_OT_move_seq_down)
    importlib.reload(WAR3_OT_generate_from_actions)
    importlib.reload(WAR3_OT_move_seq_in_list)
except ImportError:
    print("    could not reload operator modules")

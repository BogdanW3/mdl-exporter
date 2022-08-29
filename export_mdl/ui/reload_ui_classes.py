import importlib
from . import WAR3_PT_billboard_panel
from . import WAR3_PT_event_panel
from . import WAR3_PT_light_panel
from . import WAR3_PT_material_panel
from . import WAR3_PT_particle_editor_panel
from . import WAR3_PT_sequences_panel
from . import WAR3_UL_material_layer_list
from . import WAR3_UL_sequence_list

try:
    print("    reloading UI modules")
    importlib.reload(WAR3_PT_billboard_panel)
    importlib.reload(WAR3_PT_event_panel)
    importlib.reload(WAR3_PT_light_panel)
    importlib.reload(WAR3_PT_material_panel)
    importlib.reload(WAR3_PT_particle_editor_panel)
    importlib.reload(WAR3_PT_sequences_panel)
    importlib.reload(WAR3_UL_material_layer_list)
    importlib.reload(WAR3_UL_sequence_list)
except ImportError:
    print("    could not reload UI modules")

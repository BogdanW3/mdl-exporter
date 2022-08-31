import importlib
from . import add_bones
from . import add_empties_animations
from . import add_lights
from . import add_particle_systems
from . import create_collision_shapes
from . import create_material_stuff
from . import from_scene
from . import get_actions
from . import get_parent
from . import get_sequences
from . import get_visibility
from . import is_animated_ugg
from . import make_mesh
from . import get_bpy_mesh
from . import register_global_sequence
from . import to_scene


try:
    print("    reloading model util modules")
    # importlib.reload(WAR3_MT_emitter_presets)
    importlib.reload(add_bones)
    importlib.reload(add_empties_animations)
    importlib.reload(add_lights)
    importlib.reload(add_particle_systems)
    importlib.reload(create_collision_shapes)
    importlib.reload(create_material_stuff)
    importlib.reload(from_scene)
    importlib.reload(get_actions)
    importlib.reload(get_parent)
    importlib.reload(get_sequences)
    importlib.reload(get_visibility)
    importlib.reload(is_animated_ugg)
    importlib.reload(make_mesh)
    importlib.reload(get_bpy_mesh)
    importlib.reload(register_global_sequence)
    importlib.reload(to_scene)
except ImportError:
    print("    could not reload model util modules")

import importlib
from .mdl_parser import reload_mdl_parser
from .mdx_parser import reload_mdx_parser
from . import create_armature_actions

import bpy
if bpy.app.version[0] < 4:
    from . import create_bone_groups
else:
    from . import create_bone_collections as create_bone_groups
from . import create_armature_object
from . import create_material
from . import create_mesh_objects
from . import create_object_actions
from . import create_other_objects
from . import create_attachment_empties
from . import create_collision_empties
from . import create_event_empties
from . import create_light_objects
from . import load_stuff
from . import load_warcraft_3_model
from . import MDXImportProperties
from . import War3BpyMaterial

try:
    print("    reloading import modules")
    importlib.reload(reload_mdl_parser)
    importlib.reload(reload_mdx_parser)
    importlib.reload(create_bone_groups)
    importlib.reload(create_armature_actions)
    importlib.reload(create_armature_object)
    importlib.reload(create_material)
    importlib.reload(create_mesh_objects)
    importlib.reload(create_object_actions)
    importlib.reload(create_other_objects)

    importlib.reload(create_attachment_empties)
    importlib.reload(create_collision_empties)
    importlib.reload(create_event_empties)
    importlib.reload(create_light_objects)
    importlib.reload(load_stuff)
    importlib.reload(load_warcraft_3_model)
    importlib.reload(MDXImportProperties)
    importlib.reload(War3BpyMaterial)
except ImportError:
    print("    could not reload import modules")

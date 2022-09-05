import importlib
from .animation_curve_utils import reload_anim_cuvre_utils
from .bpy_helpers import reload_bpy_helpers
from .model_utils import reload_war3_model_utils
from . import War3AnimationAction
from . import War3AnimationCurve
from . import War3AnimationSequence
from . import War3Attachment
from . import War3Bone
from . import War3CollisionShape
from . import War3EventObject
from . import War3ExportSettings
from . import War3Geoset
from . import War3GeosetAnim
from . import War3Helper
from . import War3Layer
from . import War3Light
from . import War3Material
from . import War3Model
from . import War3Node
from . import War3ParticleSystem
from . import War3TextureAnim
from . import War3Vertex

try:
    print("    reloading WC3 class modules")
    # importlib.reload(WAR3_MT_emitter_presets)
    importlib.reload(reload_anim_cuvre_utils)
    importlib.reload(reload_bpy_helpers)
    importlib.reload(reload_war3_model_utils)
    importlib.reload(War3AnimationAction)
    importlib.reload(War3AnimationCurve)
    importlib.reload(War3AnimationSequence)
    importlib.reload(War3Attachment)
    importlib.reload(War3Bone)
    importlib.reload(War3CollisionShape)
    importlib.reload(War3EventObject)
    importlib.reload(War3ExportSettings)
    importlib.reload(War3Geoset)
    importlib.reload(War3GeosetAnim)
    importlib.reload(War3Helper)
    importlib.reload(War3Layer)
    importlib.reload(War3Light)
    importlib.reload(War3Material)
    importlib.reload(War3Model)
    importlib.reload(War3Node)
    importlib.reload(War3ParticleSystem)
    importlib.reload(War3TextureAnim)
    importlib.reload(War3Vertex)
except ImportError:
    print("    could not reload WC3 class modules")

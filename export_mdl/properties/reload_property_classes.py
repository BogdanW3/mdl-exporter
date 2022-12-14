import importlib
from . import War3BillboardProperties
from . import War3EventProperties
from . import War3LightSettings
from . import War3MaterialLayerProperties
from . import War3ParticleSystemProperties
from . import War3ArmatureProperties
from . import War3SequencesProperties

try:
    print("    reloading property modules")
    importlib.reload(War3BillboardProperties)
    importlib.reload(War3EventProperties)
    importlib.reload(War3LightSettings)
    importlib.reload(War3MaterialLayerProperties)
    importlib.reload(War3ParticleSystemProperties)
    importlib.reload(War3ArmatureProperties)
    importlib.reload(War3SequencesProperties)
except ImportError:
    print("    could not reload property modules")

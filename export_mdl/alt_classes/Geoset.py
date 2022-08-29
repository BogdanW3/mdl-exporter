from typing import Optional, List, Tuple

from mathutils import Vector

from export_mdl.alt_classes.GeosetAnim import GeosetAnim
from export_mdl.alt_classes.GeosetVertex import GeosetVertex
from export_mdl.alt_classes.Material import Material


class Geoset:
    def __init__(self):
        self.geo_anim: Optional[GeosetAnim]
        self.vertices: List[GeosetVertex] = []
        self.triangles: List[Tuple[GeosetVertex]] = []
        self.material: Material
        self.min_extent: Optional[Vector]
        self.max_extent: Optional[Vector]
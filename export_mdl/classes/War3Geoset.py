class War3Geoset:
    def __init__(self):
        self.vertices = []
        self.triangles = []
        self.matrices = []
        self.skin_matrices = []
        self.skin_weights = []
        self.objects = []
        self.min_extent = None
        self.max_extent = None
        self.mat_name = None
        self.geoset_anim = None

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.mat_name == other.mat_name and self.geoset_anim == other.geoset_anim
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # return hash(tuple(sorted(self.__dict__.items())))
        return hash((self.mat_name, hash(self.geoset_anim)))  # Different geoset anims should split geosets

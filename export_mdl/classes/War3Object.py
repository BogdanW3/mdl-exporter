class War3Object:  # Stores information about an MDL object (not a blender object!)
    def __init__(self, name):
        self.parent = None
        self.name = name
        self.pivot = None  # TODO
        self.anim_loc = None
        self.anim_rot = None
        self.anim_scale = None
        self.billboarded = False
        self.billboard_lock = (False, False, False)

    def set_billboard(billboard):
        bb = obj.mdl_billboard
        self.billboarded = bb.billboarded
        self.billboard_lock = (bb.billboard_lock_z, bb.billboard_lock_y, bb.billboard_lock_x)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # return hash(tuple(sorted(self.__dict__.items())))
        return hash(self.name)

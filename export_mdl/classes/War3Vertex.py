class War3Vertex:
    # def __init__(self, pos: [float], normal: [float], uv: [float], matrix, skin, tangent: [float]):
    def __init__(self, pos: [float], normal: [float], uv: [float], matrix, bone_list, weight_list, tangent: [float]):
        self.pos: [float] = pos
        self.normal: [float] = normal
        self.tangent: [float] = tangent
        self.uv: [float] = uv
        self.matrix = matrix
        # self.skin = skin
        self.bone_list = bone_list
        self.weight_list = weight_list
        # self.weight_list = []
        # self.bone_list = []

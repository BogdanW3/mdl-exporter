class War3Vertex:
    def __init__(self, pos: [float], normal: [float], uv: [float], matrix, skin, tangent: [float]):
        self.pos: [float] = pos
        self.normal: [float] = normal
        self.tangent: [float] = tangent
        self.uv: [float] = uv
        self.matrix = matrix
        self.skin = skin
        # self.weight_list = []
        # self.bone_list = []

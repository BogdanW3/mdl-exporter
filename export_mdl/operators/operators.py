# import os
#
#
# def load_texture_list():
#     directory = os.path.dirname(__file__)
#
#     path = os.path.join(directory, "../textures.txt")
#     l = []
#     with open(path, 'r') as f:
#         l = [(line[:-1], os.path.basename(line[:-1]), os.path.basename(line[:-1])) for line in f.readlines()]
#
#     return l
#
#
# texture_paths = load_texture_list()

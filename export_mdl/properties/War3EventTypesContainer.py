import os
from typing import List, Tuple


class War3EventTypesContainer:

    def __init__(self):
        self.enums = {}

        directory = os.path.dirname(__file__)

        self.enums['SND'] = self.get_strings_from_file(os.path.join(directory, "../sound_types.txt"))
        splat_types = self.get_strings_from_file(os.path.join(directory, "../splat_types.txt"))
        self.enums['SPL'] = splat_types
        self.enums['FTP'] = splat_types
        self.enums['UBR'] = self.get_strings_from_file(os.path.join(directory, "../ubersplat_types.txt"))
        self.enums['SPN'] = self.get_path_strings_from_file(os.path.join(directory, "../spawnobject_types.txt"))

    @staticmethod
    def get_path_strings_from_file(path):
        strings4 = []
        with open(path, 'r') as file:
            for line in file.readlines():
                parts = line.split(" ")
                strings4.append((parts[0], parts[1][:-1].split("\\")[-1], ""))
        return strings4

    @staticmethod
    def get_strings_from_file(path: str) -> List[Tuple[str, str, str]]:
        strings = []
        with open(path, 'r') as file:
            for line in file.readlines():
                parts = line.split(" ")
                strings.append((parts[0], parts[1][:-1], ""))
        return strings

# def update_event_type(self, context):
#     obj = context.active_object
#
#     counter = 0
#
#     self.event_id = war3_event_types.enums[self.event_type][0][0]
#
#     while True:
#         if not any([ob for ob in context.scene.objects if ob.name.startswith("%s%d" % (self.event_type, counter))]):
#             obj.name = "%s%d%s" % (self.event_type, counter, self.event_id)
#             break
#         counter += 1
#
#     obj['event_type'] = self.event_type
#     obj['event_id'] = self.event_id
#
#
# def get_event_items(self, context):
#     return war3_event_types.enums[self.event_type]
#
#
# war3_event_types = War3EventTypesContainer()

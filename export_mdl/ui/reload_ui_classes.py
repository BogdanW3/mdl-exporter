import importlib
import typing
from . import WAR3_PT_billboard_panel
from . import WAR3_PT_event_panel
from . import WAR3_PT_light_panel
from . import WAR3_PT_material_panel
from . import WAR3_PT_particle_editor_panel
from . import WAR3_PT_sequences_panel
from . import WAR3_UL_material_layer_list
from . import WAR3_UL_sequence_list
# from . import __init__
#
# import inspect
# # import testpkg
#
#
# # def is_wanted_module(thing):
# #     print("'__builtins__'", str(thing).count('__builtins__'))
# #     return inspect.ismodule(thing) and not inspect.isbuiltin(thing) and str(thing).count('__builtins__') == 0
# #
# # def uggugg(things):
# #     for thing in things:
# #         if str(thing).count('__builtins__') == 0:
# #             print(thing)
# #
# #
# # getmembers = inspect.getmembers(__init__, inspect.ismodule)
# # print("getmembers: ", getmembers)
# # print("getmembers: ", getmembers[0][1])
# # # print("getmembers2: ", inspect.getmembers(getmembers[0][1]), inspect.ismodule)
# # print("getmembers.getM: ", inspect.getmembers(getmembers[0][1], inspect.ismodule))
# #
# # getmembers2 = inspect.getmembers(__init__)
# # print("getmembers2: ", getmembers2)
#
# def get_members():
#     this_module = inspect.getmembers(__init__, inspect.ismodule)[0][1]
#     return inspect.getmembers(this_module, inspect.ismodule)
#
#
# print("    reloading UI modules")
# module_members = get_members()
# for member in module_members:
#     try:
#         if str(member).count('__init__') == 0 and str(member).count('reload_ui') == 0:
#             print("      reloading ", member)
#             importlib.reload(member[1])
#             print("member[1]:", member[1])
#             print("classes:", inspect.getmembers(member, inspect.isclass))
#             print("classes:", inspect.getmembers(member, inspect.isclass)[0][1])
#             # print("members:", inspect.getmembers(member))
#     except ImportError:
#         print("    could not reload UI module:", member)
try:
    importlib.reload(WAR3_PT_billboard_panel)
    importlib.reload(WAR3_PT_event_panel)
    importlib.reload(WAR3_PT_light_panel)
    importlib.reload(WAR3_PT_material_panel)
    importlib.reload(WAR3_PT_particle_editor_panel)
    importlib.reload(WAR3_PT_sequences_panel)
    importlib.reload(WAR3_UL_material_layer_list)
    importlib.reload(WAR3_UL_sequence_list)


except ImportError:
    print("    could not reload UI modules")


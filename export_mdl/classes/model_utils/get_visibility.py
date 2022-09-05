# from typing import Optional, List, Set
#
# import bpy
#
# from ..War3AnimationAction import War3AnimationAction
# from ..War3AnimationCurve import War3AnimationCurve
# from ..animation_curve_utils.get_wc3_animation_curve import get_wc3_animation_curve
#
#
# def get_visibility(sequences: List[War3AnimationAction], global_seqs: Set[int], bpy_obj: bpy.types.Object) -> Optional[War3AnimationCurve]:
#     animation_data = bpy_obj.animation_data
#     if animation_data is not None:
#         curve = get_wc3_animation_curve(animation_data, 'hide_render', 1, sequences)
#         if curve is not None:
#             return curve
#     if bpy_obj.parent is not None and bpy_obj.parent_type != 'BONE':
#         return get_visibility(sequences, global_seqs, bpy_obj.parent)
#     return None

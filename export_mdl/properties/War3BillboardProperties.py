from bpy.props import BoolProperty
from bpy.types import PropertyGroup


class War3BillboardProperties(PropertyGroup):
    billboarded: BoolProperty(
        name="Billboarded",
        description="If true, this object will always face the camera.",
        default=False
        )
    billboard_lock_x: BoolProperty(
        name="Billboard Lock X",
        description="Limits billboarding around the X axis.",
        default=False,
        )
    billboard_lock_y: BoolProperty(
        name="Billboard Lock Y",
        description="Limits billboarding around the Y axis.",
        default=False
        )
    billboard_lock_z: BoolProperty(
        name="Billboard Lock Z",
        description="Limits billboarding around the Z axis.",
        default=False
        )
    camera_anchored: BoolProperty(
        name="Camera Anchored",
        description="Node flag CameraAnchored",
        default=False
        )
    dont_inherit_translation: BoolProperty(
        name="Don't Inherit Translation",
        description="Ignore the parent's translation",
        default=False
        )
    dont_inherit_rotation: BoolProperty(
        name="Don't Inherit Rotation",
        description="Ignore the parent's rotation",
        default=False
        )
    dont_inherit_scaling: BoolProperty(
        name="Don't Inherit Scaling",
        description="Ignore the parent's scaling",
        default=False
        )

    def node_flags(self) -> int:
        """The MDX node flags these stand for (besides billboarding)."""
        return (0x1 if self.dont_inherit_translation else 0) | (0x2 if self.dont_inherit_rotation else 0) | \
            (0x4 if self.dont_inherit_scaling else 0) | (0x80 if self.camera_anchored else 0)

    def set_node_flags(self, flags: int):
        self.dont_inherit_translation = bool(flags & 0x1)
        self.dont_inherit_rotation = bool(flags & 0x2)
        self.dont_inherit_scaling = bool(flags & 0x4)
        self.camera_anchored = bool(flags & 0x80)

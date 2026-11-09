import bpy

from ..frame_rate import scene_fps


class MDXImportProperties:
    def __init__(self):
        self.mdx_file_path: str = ''
        self.team_color: str = '0'
        self.bone_size: float = 1.0
        # 'FIT': change the scene's rate if needed so every key lands on a whole frame,
        # 'SCENE': keep the scene's rate (keys snap to its frames), 'CUSTOM': switch the scene to self.fps
        self.frame_rate: str = 'FIT'
        self.use_custom_fps: bool = False  # (Older callers: same as frame_rate = 'CUSTOM')
        self.fps: float = 30
        self.frame_time: float = 1.0
        self.messages = []  # What the import changed or lost, for the operator to report

    def calculate_frame_time(self):
        if self.use_custom_fps:
            self.frame_rate = 'CUSTOM'
        if self.frame_rate != 'CUSTOM':
            self.fps = scene_fps(bpy.context.scene)
        self.frame_time = 1000 / self.fps

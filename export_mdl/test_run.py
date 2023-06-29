from export_mdl.import_stuff.MDXImportProperties import MDXImportProperties

from export_mdl.import_stuff.mdl_parser.load_mdl import load_mdl
# run this with
# "PATH\TO\BLENDER\blender" --background --python "PATH\TO\test_run.py" "PATH\TO\model.mdx"
from export_mdl.import_stuff.mdx_parser.load_mdx import load_mdx


# run through CMD using:
# "C:\path\to\Blender 2.93\blender" --background --python "C:\path\to\export_mdl\test_run.py" "D:\path\to\file.mdl"
# (note that the first argument after "--python" should be the path to this file)
def test_run(filepath):
    print("file: ", filepath)
    import_properties = MDXImportProperties()
    import_properties.mdx_file_path = filepath
    import_properties.set_team_color = (1.0, 0.000911, 0.000911)  # red
    import_properties.bone_size = 5.0
    import_properties.use_custom_fps = False
    import_properties.fps = 30.0
    import_properties.calculate_frame_time()

    if ".mdl" in filepath:
        load_mdl(import_properties)
    else:
        load_mdx(import_properties)
    return {'FINISHED'}


import sys

if __name__ == "__main__":
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")
    print(sys.argv)
    test_run(sys.argv[4])

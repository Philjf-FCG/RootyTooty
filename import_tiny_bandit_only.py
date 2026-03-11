import os
import unreal

PROJECT_ROOT = r"C:\Unreal Projects\rooty\RootyTooty"
DEST_PATH = "/Game/Assets"
SOURCE_FILE = os.path.join(
    PROJECT_ROOT,
    "Tiny_Bandit_extracted",
    "A_physically_short_c_0408200831_texture_fbx",
    "A_physically_short_c_0408200831_texture.fbx",
)
DEST_NAME = "Tiny_Bandit"


if not unreal.EditorAssetLibrary.does_directory_exist(DEST_PATH):
    unreal.EditorAssetLibrary.make_directory(DEST_PATH)

if not os.path.exists(SOURCE_FILE):
    unreal.log_error(f"TINY_IMPORT: Missing source file: {SOURCE_FILE}")
    raise RuntimeError("Bandit source file missing")

options = unreal.FbxImportUI()
options.set_editor_property("import_mesh", True)
options.set_editor_property("import_as_skeletal", False)
options.set_editor_property("import_materials", False)
options.set_editor_property("import_textures", False)
options.set_editor_property("create_physics_asset", False)

sm_data = options.get_editor_property("static_mesh_import_data")
if sm_data:
    sm_data.set_editor_property("combine_meshes", True)

task = unreal.AssetImportTask()
task.set_editor_property("filename", SOURCE_FILE)
task.set_editor_property("destination_path", DEST_PATH)
task.set_editor_property("destination_name", DEST_NAME)
task.set_editor_property("replace_existing", True)
task.set_editor_property("automated", True)
task.set_editor_property("save", True)
task.set_editor_property("options", options)

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

asset_path = f"{DEST_PATH}/{DEST_NAME}.{DEST_NAME}"
if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
    unreal.EditorAssetLibrary.save_asset(asset_path)
    unreal.log(f"TINY_IMPORT: Imported {asset_path}")
else:
    unreal.log_error(f"TINY_IMPORT: Expected asset missing after import: {asset_path}")
    raise RuntimeError("Bandit import failed")

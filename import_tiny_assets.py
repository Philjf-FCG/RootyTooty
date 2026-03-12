import os
import unreal

PROJECT_ROOT = r"C:\Unreal Projects\rooty\RootyTooty"
DEST_PATH = "/Game/Assets"

ASSET_IMPORTS = [
    {
        "source": os.path.join(PROJECT_ROOT, "Tiny_Cowboy.fbx"),
        "dest": "Tiny_Cowboy",
    },
    {
        "source": os.path.join(
            PROJECT_ROOT,
            "Tiny_Bandit_extracted",
            "A_physically_short_c_0408200831_texture_fbx",
            "A_physically_short_c_0408200831_texture.fbx",
        ),
        "dest": "Tiny_Bandit",
    },
]


def ensure_folder(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def make_fbx_options():
    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_as_skeletal", False)
    options.set_editor_property("import_materials", True)
    options.set_editor_property("import_textures", True)
    options.set_editor_property("create_physics_asset", False)

    sm_data = options.get_editor_property("static_mesh_import_data")
    if sm_data:
        sm_data.set_editor_property("combine_meshes", True)
        sm_data.set_editor_property("generate_lightmap_u_vs", True)
    return options


def import_tiny_assets():
    ensure_folder(DEST_PATH)
    fbx_options = make_fbx_options()

    for item in ASSET_IMPORTS:
        source_file = item["source"]
        dest_name = item["dest"]

        if not os.path.exists(source_file):
            unreal.log_error(f"TINY_IMPORT: Missing source file: {source_file}")
            continue

        task = unreal.AssetImportTask()
        task.set_editor_property("filename", source_file)
        task.set_editor_property("destination_path", DEST_PATH)
        task.set_editor_property("destination_name", dest_name)
        task.set_editor_property("replace_existing", True)
        task.set_editor_property("automated", True)
        task.set_editor_property("save", True)
        task.set_editor_property("options", fbx_options)

        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

        asset_path = f"{DEST_PATH}/{dest_name}.{dest_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
            unreal.EditorAssetLibrary.save_asset(asset_path)
            unreal.log(f"TINY_IMPORT: Imported {asset_path}")
        else:
            unreal.log_error(f"TINY_IMPORT: Expected asset missing after import: {asset_path}")


if __name__ == "__main__":
    import_tiny_assets()

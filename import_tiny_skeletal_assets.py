import os
import unreal

PROJECT_ROOT = r"C:\Unreal Projects\rooty\RootyTooty"
DEST_PATH = "/Game/Assets"

ASSET_IMPORTS = [
    {
        "source": os.path.join(PROJECT_ROOT, "Tiny_Cowboy.fbx"),
        "dest": "SKM_Tiny_Cowboy",
    },
    {
        "source": os.path.join(
            PROJECT_ROOT,
            "Tiny_Bandit_extracted",
            "A_physically_short_c_0408200831_texture_fbx",
            "A_physically_short_c_0408200831_texture.fbx",
        ),
        "dest": "SKM_Tiny_Bandit",
    },
]


def _load_first(paths):
    for path in paths:
        asset = unreal.load_asset(path)
        if asset:
            return asset
    return None


def _resolve_target_skeleton():
    return _load_first([
        "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple_Skeleton",
        "/Game/Mannequins/Meshes/SKM_Manny_Simple_Skeleton",
        "/Game/Characters/Mannequins/Meshes/SK_Mannequin_Skeleton",
        "/Game/Mannequins/Meshes/SK_Mannequin_Skeleton",
    ])


def _ensure_folder(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def _make_skeletal_options(target_skeleton):
    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_as_skeletal", True)
    options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    options.set_editor_property("import_materials", True)
    options.set_editor_property("import_textures", True)
    options.set_editor_property("create_physics_asset", False)

    if target_skeleton:
        options.set_editor_property("skeleton", target_skeleton)

    sk_data = options.get_editor_property("skeletal_mesh_import_data")
    if sk_data:
        sk_data.set_editor_property("import_meshes_in_bone_hierarchy", True)
        sk_data.set_editor_property("import_morph_targets", False)
        sk_data.set_editor_property("update_skeleton_reference_pose", False)
        sk_data.set_editor_property("use_t0_as_ref_pose", True)
    return options


def import_tiny_skeletal_assets():
    _ensure_folder(DEST_PATH)

    target_skeleton = _resolve_target_skeleton()
    if target_skeleton:
        unreal.log(f"TINY_SKM_IMPORT: Using target skeleton {target_skeleton.get_path_name()}")
    else:
        unreal.log_warning("TINY_SKM_IMPORT: Could not find mannequin skeleton; import may generate a new skeleton or fail.")

    for item in ASSET_IMPORTS:
        source_file = item["source"]
        dest_name = item["dest"]

        if not os.path.exists(source_file):
            unreal.log_error(f"TINY_SKM_IMPORT: Missing source file: {source_file}")
            continue

        task = unreal.AssetImportTask()
        task.set_editor_property("filename", source_file)
        task.set_editor_property("destination_path", DEST_PATH)
        task.set_editor_property("destination_name", dest_name)
        task.set_editor_property("replace_existing", True)
        task.set_editor_property("automated", True)
        task.set_editor_property("save", True)
        task.set_editor_property("options", _make_skeletal_options(target_skeleton))

        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

        mesh_path = f"{DEST_PATH}/{dest_name}.{dest_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(mesh_path):
            unreal.EditorAssetLibrary.save_asset(mesh_path)
            unreal.log(f"TINY_SKM_IMPORT: Imported {mesh_path}")
        else:
            unreal.log_error(f"TINY_SKM_IMPORT: Skeletal mesh not found after import: {mesh_path}")


if __name__ == "__main__":
    import_tiny_skeletal_assets()

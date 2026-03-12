import unreal

BOBRITO_FBX = r"C:/Unreal Projects/rooty/RootyTooty/Saved/ImportedCharacters/bobrito-bandito-game-ready-3d-model-free/source/Offensive Idle.fbx"
DEST_PATH = "/Game/ImportedCharacters/Bobrito"
DEST_NAME = "SK_BobritoEnemy"
SKELETON_PATH = "/Game/ImportedCharacters/Bobrito/SK_BobritoEnemy_Skeleton.SK_BobritoEnemy_Skeleton"


def main() -> None:
    if not unreal.Paths.file_exists(BOBRITO_FBX):
        unreal.log_error(f"[BOBRITO_REIMPORT] FBX not found: {BOBRITO_FBX}")
        return

    skeleton = unreal.load_object(None, SKELETON_PATH)

    options = unreal.FbxImportUI()
    options.set_editor_property("automated_import_should_detect_type", False)
    options.set_editor_property("import_as_skeletal", True)
    options.set_editor_property("import_animations", False)
    options.set_editor_property("import_materials", True)
    options.set_editor_property("import_textures", True)
    options.set_editor_property("create_physics_asset", False)
    options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)

    if skeleton:
        options.set_editor_property("skeleton", skeleton)

    sk_data = options.get_editor_property("skeletal_mesh_import_data")
    sk_data.set_editor_property("import_mesh_lo_ds", False)
    sk_data.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)

    task = unreal.AssetImportTask()
    task.set_editor_property("filename", BOBRITO_FBX)
    task.set_editor_property("destination_path", DEST_PATH)
    task.set_editor_property("destination_name", DEST_NAME)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("replace_existing_settings", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    task.set_editor_property("options", options)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    imported = task.get_editor_property("imported_object_paths")
    if imported:
        unreal.log(f"[BOBRITO_REIMPORT] Imported objects: {imported}")
    else:
        unreal.log_warning("[BOBRITO_REIMPORT] No imported object paths reported")

    enemy_mesh = unreal.load_object(None, f"{DEST_PATH}/{DEST_NAME}.{DEST_NAME}")
    if enemy_mesh:
        mat_count = enemy_mesh.get_num_materials()
        unreal.log(f"[BOBRITO_REIMPORT] Enemy mesh material slots: {mat_count}")
        for i in range(mat_count):
            mat = enemy_mesh.get_material(i)
            unreal.log(f"[BOBRITO_REIMPORT] Slot {i}: {unreal.get_path_name(mat) if mat else '<None>'}")


if __name__ == "__main__":
    main()

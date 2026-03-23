import unreal

PNG_PATH = r"C:\\Unreal Projects\\rooty\\RootyTooty\\HUD.png"
DEST_PATH = "/Game/UI"


def import_texture():
    task = unreal.AssetImportTask()
    task.filename = PNG_PATH
    task.destination_path = DEST_PATH
    task.destination_name = "HUD"
    task.automated = True
    task.replace_existing = True
    task.save = True

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    if task.imported_object_paths:
        unreal.log("HUD import success:")
        for p in task.imported_object_paths:
            unreal.log("  " + p)
    else:
        unreal.log_warning("HUD import produced no object paths")


if __name__ == "__main__":
    import_texture()

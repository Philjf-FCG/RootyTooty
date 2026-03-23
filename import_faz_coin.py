import unreal

FBX_PATH = r"C:\\Unreal Projects\\rooty\\RootyTooty\\_faz_coin_unpacked\\source\\Faz-Coin.fbx"
DEST_PATH = "/Game/FazCoin"


def import_fbx_static_mesh():
    task = unreal.AssetImportTask()
    task.filename = FBX_PATH
    task.destination_path = DEST_PATH
    task.destination_name = "Faz-Coin"
    task.automated = True
    task.replace_existing = True
    task.save = True

    opts = unreal.FbxImportUI()
    opts.import_animations = False
    opts.import_as_skeletal = False
    opts.import_materials = True
    opts.import_textures = True
    opts.import_mesh = True
    opts.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    task.options = opts

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    if task.imported_object_paths:
        unreal.log("FAZ_COIN import success:")
        for p in task.imported_object_paths:
            unreal.log("  " + p)
    else:
        unreal.log_warning("FAZ_COIN import produced no object paths")


if __name__ == "__main__":
    import_fbx_static_mesh()

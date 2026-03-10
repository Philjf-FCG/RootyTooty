import unreal

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

task = unreal.AssetImportTask()
task.filename = r"C:/Unreal Projects/rooty/RootyTooty/Assets/StylizedPickaxe/Stylized Pickaxe Asset/Textures/PNG/T_pickaxe_Metallic.png"
task.destination_path = "/Game/Weapons/Pickaxe/Textures"
task.automated = True
task.save = True
task.replace_existing = True
task.replace_existing_settings = True

asset_tools.import_asset_tasks([task])
unreal.EditorAssetLibrary.save_directory("/Game/Weapons/Pickaxe/Textures", only_if_is_dirty=False, recursive=True)
unreal.log(f"Imported: {task.imported_object_paths}")

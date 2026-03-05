import os
import unreal

project_dir = unreal.Paths.project_dir()
source_dir = os.path.join(project_dir, "Assets")
destination_path = "/Game/Assets"

unreal.EditorAssetLibrary.make_directory(destination_path)

if not os.path.isdir(source_dir):
    unreal.log_error(f"Assets folder not found: {source_dir}")
else:
    fbx_files = [
        os.path.join(source_dir, name)
        for name in os.listdir(source_dir)
        if name.lower().endswith(".fbx")
    ]

    if not fbx_files:
        unreal.log_warning(f"No FBX files found in: {source_dir}")
    else:
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        tasks = []

        for fbx_file in fbx_files:
            task = unreal.AssetImportTask()
            task.filename = fbx_file
            task.destination_path = destination_path
            task.automated = True
            task.replace_existing = True
            task.save = True

            options = unreal.FbxImportUI()
            options.import_as_skeletal = False
            options.import_mesh = True
            options.import_textures = True
            options.import_materials = True
            options.import_animations = False
            options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
            task.options = options

            tasks.append(task)

        asset_tools.import_asset_tasks(tasks)
        unreal.EditorAssetLibrary.save_directory(destination_path, only_if_is_dirty=False, recursive=True)
        unreal.log(f"Imported {len(tasks)} FBX assets from {source_dir} to {destination_path}")

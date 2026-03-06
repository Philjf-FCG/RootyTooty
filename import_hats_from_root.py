import os
import unreal


def _collect_fbx_files(folder_path: str) -> list[str]:
    if not os.path.isdir(folder_path):
        return []
    return [
        os.path.join(folder_path, name)
        for name in os.listdir(folder_path)
        if name.lower().endswith(".fbx")
    ]


project_dir = unreal.Paths.project_dir()
source_root = os.path.join(project_dir, "Assets")
source_free = os.path.join(source_root, "FreeWestern")

destination_root = "/Game/Assets"
destination_free = "/Game/Assets/FreeWestern"

unreal.EditorAssetLibrary.make_directory(destination_root)
unreal.EditorAssetLibrary.make_directory(destination_free)

fbx_roots = _collect_fbx_files(source_root)
fbx_free = _collect_fbx_files(source_free)

if not os.path.isdir(source_root):
    unreal.log_error(f"Assets folder not found: {source_root}")
    unreal.log("Create it and add free FBX files from trusted sources before running this script.")
elif not fbx_roots and not fbx_free:
    unreal.log_warning(f"No FBX files found in: {source_root} or {source_free}")
else:
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    tasks: list[unreal.AssetImportTask] = []

    def _queue_import(fbx_file: str, destination: str) -> None:
        task = unreal.AssetImportTask()
        task.filename = fbx_file
        task.destination_path = destination
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

    for fbx_file in fbx_roots:
        _queue_import(fbx_file, destination_root)

    for fbx_file in fbx_free:
        _queue_import(fbx_file, destination_free)

    asset_tools.import_asset_tasks(tasks)
    unreal.EditorAssetLibrary.save_directory(destination_root, only_if_is_dirty=False, recursive=True)
    unreal.log(
        f"Imported {len(tasks)} FBX assets. "
        f"Root: {len(fbx_roots)} -> {destination_root}, "
        f"FreeWestern: {len(fbx_free)} -> {destination_free}"
    )

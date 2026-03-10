import unreal

fbx_path = r"C:/Unreal Projects/rooty/RootyTooty/Assets/StylizedPickaxe/Stylized Pickaxe Asset/FBX/stylized_pickaxe_SM.fbx"
tex_dir = r"C:/Unreal Projects/rooty/RootyTooty/Assets/StylizedPickaxe/Stylized Pickaxe Asset/Textures/Unreal"
dest_path = "/Game/Weapons/Pickaxe"

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# Import FBX static mesh.
mesh_task = unreal.AssetImportTask()
mesh_task.filename = fbx_path
mesh_task.destination_path = dest_path
mesh_task.automated = True
mesh_task.save = True
mesh_task.replace_existing = True
mesh_task.replace_existing_settings = True

mesh_opts = unreal.FbxImportUI()
mesh_opts.import_mesh = True
mesh_opts.import_as_skeletal = False
mesh_opts.import_animations = False
mesh_opts.import_materials = True
mesh_opts.import_textures = True
mesh_opts.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
mesh_task.options = mesh_opts

# Import Unreal-authored texture set (TGA) as fallback for material hookup.
tex_tasks = []
for texture_name in [
    "T_pickaxe_BaseColor.tga",
    "T_pickaxe_Normal.tga",
    "T_pickaxe_OcclusionRoughnessMetallic.tga",
]:
    task = unreal.AssetImportTask()
    task.filename = f"{tex_dir}/{texture_name}"
    task.destination_path = dest_path
    task.automated = True
    task.save = True
    task.replace_existing = True
    tex_tasks.append(task)

all_tasks = [mesh_task] + tex_tasks
asset_tools.import_asset_tasks(all_tasks)
unreal.EditorAssetLibrary.save_directory(dest_path, only_if_is_dirty=False, recursive=True)

for task in all_tasks:
    unreal.log(f"Imported: {task.imported_object_paths}")
